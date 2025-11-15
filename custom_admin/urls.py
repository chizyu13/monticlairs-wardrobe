from django.urls import path
from . import views
from home import views as home_views

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
    
    # Product Manual Management URLs
    path('product/<int:product_id>/manual/upload/', views.upload_product_manual, name='upload_product_manual'),
    path('product/<int:product_id>/manual/delete/', views.delete_product_manual, name='delete_product_manual'),
    
    # Platform Guide Management URLs
    path('guides/', views.guide_list, name='guide_list'),
    path('guides/create/', views.manage_guide, name='create_guide'),
    path('guides/<int:guide_id>/edit/', views.manage_guide, name='edit_guide'),
    path('guides/<int:guide_id>/delete/', views.delete_guide, name='delete_guide'),
    path('guides/<int:guide_id>/attachment/upload/', views.upload_guide_attachment, name='upload_guide_attachment'),
    path('guides/attachment/<int:attachment_id>/delete/', views.delete_guide_attachment, name='delete_guide_attachment'),
    
    # Live Chat Management URLs
    path('chat/', home_views.admin_chat_dashboard, name='chat_dashboard'),
    path('chat/<str:session_id>/', home_views.admin_chat_session, name='chat_session'),
    path('chat/<str:session_id>/send/', home_views.admin_send_message, name='chat_send_message'),
    path('chat/<str:session_id>/messages/', home_views.admin_get_messages, name='chat_get_messages'),
    path('chat/<str:session_id>/close/', home_views.admin_close_chat, name='chat_close'),
    path('chat/<str:session_id>/assign/', home_views.admin_assign_chat, name='chat_assign'),
]
