from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('reports/', views.reports_dashboard, name='dashboard'),
    path('daily-sales/', views.daily_sales_report, name='daily_sales'),
    path('order-status/', views.order_status_report, name='order_status'),
    path('product-sales/', views.product_sales_report, name='product_sales'),
    path('stock-level/', views.stock_level_report, name='stock_level'),
    path('customer-growth/', views.customer_growth_report, name='customer_growth'),
    path('export/', views.export_report, name='export'),
]
