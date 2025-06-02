from django.views.generic import TemplateView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from django.shortcuts import render, redirect
from django.contrib import messages
from config.mongodb import MongoDBConnection
from datetime import datetime
import bcrypt
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to auth/urls.py file for more pages.
"""


class AuthView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Update the context
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )

        return context

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            # Get form data from JSON if it's an Ajax request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                data = json.loads(request.body)
                username = data.get('username', '').strip()
                email = data.get('email', '').strip()
                password = data.get('password', '')
                confirm_password = data.get('confirm-password', '')
            else:
                # Get form data from POST for regular form submission
                username = request.POST.get('username', '').strip()
                email = request.POST.get('email', '').strip()
                password = request.POST.get('password', '')
                confirm_password = request.POST.get('confirm-password', '')
            
            # Basic validation
            if not username or not email or not password or not confirm_password:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'All fields are required'})
                messages.error(request, 'All fields are required')
                return redirect('auth-register-basic')
            
            # Username validation
            if len(username) < 3:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'Username must be at least 3 characters long'})
                messages.error(request, 'Username must be at least 3 characters long')
                return redirect('auth-register-basic')
            
            if not username.isalnum():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'Username can only contain letters and numbers'})
                messages.error(request, 'Username can only contain letters and numbers')
                return redirect('auth-register-basic')
            
            # Email validation
            if not validate_email(email):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'Please enter a valid email address'})
                messages.error(request, 'Please enter a valid email address')
                return redirect('auth-register-basic')
            
            # Password validation
            is_strong, password_message = validate_password_strength(password)
            if not is_strong:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': password_message})
                messages.error(request, password_message)
                return redirect('auth-register-basic')
            
            if password != confirm_password:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'Passwords do not match'})
                messages.error(request, 'Passwords do not match')
                return redirect('auth-register-basic')
            
            # Connect to MongoDB
            mongo = MongoDBConnection()
            users_collection = mongo.database.users
            
            # Check if user already exists
            if users_collection.find_one({'email': email}):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'This email is already registered'})
                messages.error(request, 'This email is already registered')
                return redirect('auth-register-basic')
            
            if users_collection.find_one({'username': username}):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'This username is already taken'})
                messages.error(request, 'This username is already taken')
                return redirect('auth-register-basic')
            
            # Hash the password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # Create user document
            user_data = {
                'username': username,
                'email': email,
                'password': hashed_password.decode('utf-8'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Insert user into MongoDB
            users_collection.insert_one(user_data)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Registration successful! Welcome to NeuroVue. Please login to continue.',
                    'redirect': '/auth/login/'
                })
            
            messages.success(request, 'Registration successful! Welcome to NeuroVue. Please login to continue.')
            return redirect('auth-login-basic')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': f'Registration failed: {str(e)}'})
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('auth-register-basic')
    
    return render(request, 'auth_register_basic.html')

def login_user(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            
            if not email or not password:
                messages.error(request, 'Please enter both email and password')
                return redirect('auth-login-basic')
            
            # Connect to MongoDB
            mongo = MongoDBConnection()
            users_collection = mongo.database.users
            
            # Find user by email
            user = users_collection.find_one({'email': email})
            
            if not user:
                messages.error(request, 'Invalid email or password')
                return redirect('auth-login-basic')
            
            # Verify password
            stored_password = user['password'].encode('utf-8')
            if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
                messages.error(request, 'Invalid email or password')
                return redirect('auth-login-basic')
            
            # Create session
            request.session['user_id'] = str(user['_id'])
            request.session['username'] = user['username']
            request.session['email'] = user['email']
            
            # Update last login
            users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            
            messages.success(request, f'Welcome back, {user["username"]}!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Login failed: {str(e)}')
            return redirect('auth-login-basic')
    
    return render(request, 'auth_login_basic.html')

def logout_user(request):
    # Clear session
    request.session.flush()
    messages.success(request, 'You have been successfully logged out')
    return redirect('auth-login-basic')
