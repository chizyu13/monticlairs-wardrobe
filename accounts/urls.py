from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import register_view, login_view  # Import custom views
from django.contrib.auth import views as auth_views  # Import auth views for password reset

app_name = 'accounts'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    # Updated logout to use a custom POST-only view
    path('logout/', views.logout_view, name='logout'),  # Changed from LogoutView to custom view
    
    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]