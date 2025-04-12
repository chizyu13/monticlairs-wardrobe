from django.urls import path
from . import views
from .views import custom_admin_dashboard, manage_users, sales_reports

app_name='custom_admin'

urlpatterns = [
    path('', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('dashboard/', custom_admin_dashboard, name='dashboard'),
    path('manage-users/', manage_users, name='manage_users'),
    path('sales-reports/', sales_reports, name='sales_reports'),
    
]
