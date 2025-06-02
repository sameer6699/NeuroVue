from django.views.generic import TemplateView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from django.http import JsonResponse
from config.mongodb import MongoDBConnection


class SystemView(TemplateView):
    template_name = "pages/system/not-found.html"
    status = ""

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Define the layout for this module
        # _templates/layout/system.html
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("system.html", context),
                "status": self.status,
            }
        )

        return context

def test_mongodb_connection(request):
    """
    Test view to verify MongoDB connection
    """
    try:
        # Get MongoDB connection instance
        mongo_connection = MongoDBConnection()
        
        # Test database access
        db = mongo_connection.database
        collections = db.list_collection_names()
        
        return JsonResponse({
            'status': 'success',
            'message': 'MongoDB connection is working!',
            'collections': list(collections)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to connect to MongoDB: {str(e)}'
        }, status=500)
