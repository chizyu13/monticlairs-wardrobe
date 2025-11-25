from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
import requests
from django.conf import settings
from .forms import SignUpForm, UserRegisterForm, ProfileForm
from home.models import Product, Profile  # Import from home app


# Register View for boutique customers
def register_view(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.save()
            
            # Profile is automatically created by signal
            # Use get_or_create to handle race conditions
            try:
                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'bio': profile_form.cleaned_data.get('bio', ''),
                    }
                )
                
                # Update profile with form data if not just created
                if not created:
                    profile.bio = profile_form.cleaned_data.get('bio', '')
                
                if profile_form.cleaned_data.get('profile_picture'):
                    profile.profile_picture = profile_form.cleaned_data.get('profile_picture')
                    profile.save()
                    
            except Exception as e:
                # If profile creation fails, still allow login
                print(f"Profile creation warning: {e}")
            
            login(request, user)
            messages.success(request, "Welcome to Montclair Wardrobe! Your account has been created successfully.")
            return redirect('home:main_page')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = SignUpForm()
        profile_form = ProfileForm()
    return render(request, 'accounts/register.html', {'user_form': user_form, 'profile_form': profile_form})


# Login View for boutique customers
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Hello! Welcome to Montclair Wardrobe!")
                
                # Check if user is staff/admin
                if user.is_staff or user.is_superuser:
                    return redirect('custom_admin:dashboard')
                else:
                    # Regular customers go to home page
                    return redirect('home:main_page')
        
        # Only add one error message if authentication fails
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

# Logout View (accepts both GET and POST)
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home:main_page')


# Note: Dashboard functionality is handled by custom_admin app
# Regular customers use the main boutique interface

# Password Reset Request View
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    domain = get_current_site(request).domain
                    reset_link = f'http://{domain}/accounts/reset/{uid}/{token}/'
                    subject = 'Password Reset Request'
                    message = render_to_string(
                        'accounts/password_reset_email.html',
                        {'reset_link': reset_link, 'user': user}
                    )
                    send_mail(subject, message, 'no-reply@example.com', [email], fail_silently=False)
                messages.success(request, "A password reset link has been sent to your email.")
                return redirect('password_reset_done')
            else:
                messages.error(request, "No user found with that email address.")
        else:
            messages.error(request, "Invalid email. Please enter a valid email address.")
    else:
        form = PasswordResetForm()
    return render(request, 'accounts/password_reset.html', {'form': form})

# CSRF Failure View
def csrf_failure(request, reason=""):
    return render(request, 'errors/csrf_failure.html', {'reason': reason})
