from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from home import views as home_views
from accounts.views import register_view, login_view, logout_view
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),
    # Redirect admin/users/ to admin/auth/user/
    path('admin/users/', lambda request: redirect('admin/auth/user/'), name='users_redirect'),
    
    # Core pages
    path('', home_views.home, name='home'),
    path('products/', home_views.products, name='products'),
    path('about/', home_views.about, name='about'),
    path('privacy-policy/', home_views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', home_views.terms_of_service, name='terms_of_service'),
    
    # Authentication
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # App-specific URLs
    path('cart/', include('cart.urls')),
    path('custom-admin/', include('custom_admin.urls')),
    # project/urls.py
    

    
    # Optional: Include home.urls only if it defines unique paths not already covered
    path('', include('home.urls')),  # Commented out to avoid conflicts; re-enable if needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)