from django.urls import path
from . import views

app_name = 'staff_dashboard'

urlpatterns = [
    # Dashboard home
    path('', views.staff_dashboard_home, name='home'),
    
    # Order management
    path('orders/', views.staff_orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.staff_order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.staff_order_update_status, name='order_update_status'),
    
    # Product management
    path('products/', views.staff_products_list, name='products_list'),
    path('products/<int:product_id>/', views.staff_product_detail, name='product_detail'),
    path('products/<int:product_id>/update/', views.staff_product_update, name='product_update'),
    
    # Inquiry management
    path('inquiries/', views.staff_inquiries_list, name='inquiries_list'),
    path('inquiries/<int:inquiry_id>/', views.staff_inquiry_detail, name='inquiry_detail'),
    path('inquiries/<int:inquiry_id>/resolve/', views.staff_inquiry_resolve, name='inquiry_resolve'),
    path('inquiries/<int:inquiry_id>/respond/', views.staff_inquiry_respond, name='inquiry_respond'),
    
    # Admin views
    path('admin/approvals/', views.admin_staff_approval_list, name='admin_approval_list'),
    path('admin/approvals/<int:user_id>/approve/', views.admin_staff_approve, name='admin_staff_approve'),
    path('admin/approvals/<int:user_id>/revoke/', views.admin_staff_revoke, name='admin_staff_revoke'),
    path('admin/audit-log/', views.admin_audit_log, name='admin_audit_log'),
]
