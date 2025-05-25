from django.urls import path
from .views import DashboardsView



urlpatterns = [
    
    path(
        "",
        DashboardsView.as_view(template_name="landing_test.html"),
        name="index",
    ),

    # Dashboard view
    path(
        "dashboard/",
        DashboardsView.as_view(template_name="dashboard_analytics.html"),
        name="dashboard",
    ),
    
    
]
