from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from home import views as home_views
from accounts.views import register_view, login_view, logout_view
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),
    path('admin/users/', lambda request: redirect('admin/auth/user/'), name='users_redirect'),

    # Test page
    path('test/', lambda request: render(request, 'test.html'), name='test'),

    # Authentication
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('accounts/login/', login_view, name='accounts_login'),  # Alternative login URL
    path('logout/', logout_view, name='logout'),

    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # App-specific URLs
    path('cart/', include('cart.urls')),
    path('chat/', include('chat.urls')),
    path('custom-admin/', include('custom_admin.urls')),
    path('payment/', include(('payment.urls', 'payment'), namespace='payment')),
    path('staff/', include(('staff_dashboard.urls', 'staff_dashboard'), namespace='staff_dashboard')),

    # Home app URLs with namespace
    path('', include(('home.urls', 'home'), namespace='home')),
    path('', include(('reports.urls', 'reports'), namespace='reports')),
]

# Serve media files during development
# Note: Static files are automatically served by django.contrib.staticfiles when DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
