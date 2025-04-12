from django.urls import path
from home import views
from .views import custom_password_change, password_change_done_view




app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('category/create/', views.create_category, name='create_category'),
    path('categories/', views.category_list, name='category_list'),
    path('product/post/', views.post_product, name='post_product'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/<int:id>/update/', views.update_product, name='update_product'),
    path('admin/dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('profile/', views.profile_view, name='profile_view'),  # Changed from 'profile' to 'profile_view'
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    path('checkouts/', views.user_checkouts, name='user_checkouts'),
    path('sales/report/', views.sales_report, name='sales_report'),
    path('sales/receipt/<int:sale_id>/', views.generate_receipt, name='generate_receipt'),
    path('sales/export/', views.export_sales, name='export_sales'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/toggle/', views.toggle_product_status, name='toggle_product_status'),
    path('profile/', views.profile_view, name='profile'),
    path('sale/<int:id>/', views.sale_detail, name='sale_detail'),
    path('checkout/<int:pk>/', views.checkout_detail, name='checkout_detail'),
    path('process/', views.checkout_process, name='checkout_process'),
   # urls.py
   path('manage-products/', views.manage_products, name='manage_products'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete-product'),
    path('sales/export/pdf/', views.export_sales_pdf, name='export_sales_pdf'),
    path('checkout-success/', views.checkout_success, name='checkout_success'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('password_change/', custom_password_change, name='password_change'),
    path('password_change/', password_change_done_view, name='password_change_done'),
]
