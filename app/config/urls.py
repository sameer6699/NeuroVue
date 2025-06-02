from django.contrib import admin
from django.urls import include, path
from web_project.views import SystemView
from django.http import HttpResponseServerError

urlpatterns = [
    path("admin/", admin.site.urls),

    # Dashboard urls - Keep this first to ensure it takes precedence at root path
    path("", include("apps.dashboards.urls")),

    # All other app urls
    path("", include("apps.layouts.urls")),
    path("", include("apps.pages.urls")),
    path("", include("apps.authentication.urls")),
    path("", include("apps.cards.urls")),
    path("", include("apps.ui.urls")),
    path("", include("apps.extended_ui.urls")),
    path("", include("apps.icons.urls")),
    path("", include("apps.forms.urls")),
    path("", include("apps.form_layouts.urls")),
    path("", include("apps.tables.urls")),
]

def custom_handler404(request, exception):
    view = SystemView.as_view(template_name="pages_misc_error.html", status=404)
    return view(request)

def custom_handler400(request, exception):
    view = SystemView.as_view(template_name="pages_misc_error.html", status=400)
    return view(request)

def custom_handler500(request):
    view = SystemView.as_view(template_name="pages_misc_error.html", status=500)
    return view(request)


