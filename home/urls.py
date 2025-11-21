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
    
    # Customer Care Pages
    path('size-guide/', views.size_guide, name='size_guide'),
    path('delivery-info/', views.delivery_info, name='delivery_info'),
    path('returns/', views.returns, name='returns'),
    path('faq/', views.faq, name='faq'),
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
    
    # Product Manual URLs
    path('product/<int:product_id>/manual/download/', views.download_product_manual, name='download_product_manual'),
    
    # Help Center URLs
    path('help/', views.help_center, name='help_center'),
    path('help/<slug:slug>/', views.guide_detail, name='guide_detail'),
    path('help/category/<str:category>/', views.guide_category, name='guide_category'),
    
    # Customer Chat URLs
    path('chat/start/', views.start_chat_session, name='start_chat_session'),
    path('chat/start/<int:product_id>/', views.start_chat_session, name='start_chat_session_product'),
    path('chat/send/<str:session_id>/', views.send_message, name='send_message'),
    path('chat/messages/<str:session_id>/', views.get_messages, name='get_messages'),
    path('chat/close/<str:session_id>/', views.close_chat, name='close_chat'),
]
