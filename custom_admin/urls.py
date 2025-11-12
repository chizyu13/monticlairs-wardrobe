from django.urls import path
from . import views

app_name='custom_admin'

urlpatterns = [
    path('', views.custom_admin_dashboard, name='dashboard'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('sales-reports/', views.sales_reports, name='sales_reports'),
    
    # Product Management URLs
    path('products/', views.manage_products, name='manage_products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/approve/', views.approve_product, name='approve_product'),
    path('products/<int:product_id>/reject/', views.reject_product, name='reject_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    
    # Order Management URLs
    path('orders/', views.manage_orders, name='manage_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    
    # Customer Management URLs
    path('customers/', views.manage_customers, name='manage_customers'),
    path('customers/<int:user_id>/', views.customer_detail, name='customer_detail'),
    
    # Payment Verification URLs
    path('payments/', views.manage_payments, name='manage_payments'),
    path('payments/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:payment_id>/approve/', views.approve_payment, name='approve_payment'),
    path('payments/<int:payment_id>/reject/', views.reject_payment, name='reject_payment'),
    path('payments/<int:payment_id>/processing/', views.mark_payment_processing, name='mark_payment_processing'),
]
