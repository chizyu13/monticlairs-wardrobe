from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponse
from home import views
from .views import contact_view

app_name = 'home'

urlpatterns = [
    # Essential pages only
    path('', views.home, name='main_page'),
    path('test-home/', lambda request: HttpResponse("Test home page works!"), name='test_home'),
    path('home/', lambda request: redirect('/', permanent=True), name='home_redirect'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('contact/', contact_view, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('clock/', views.clock_view, name='clock'),
    path('category/<str:category_slug>/', views.category_products, name='category_products'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-orders/', views.user_checkouts, name='user_checkouts'),
    path('post-product/', views.post_product, name='post_product'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-process/', views.checkout_process, name='checkout_process'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('checkout-success/', views.checkout_success, name='checkout_success'),
    path('checkout/<int:checkout_id>/', views.checkout_detail, name='checkout_detail'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # Receipt URLs
    path('receipt/<int:checkout_id>/download/', views.download_receipt, name='download_receipt'),
    path('receipt/<int:checkout_id>/view/', views.view_receipt, name='view_receipt'),
]
