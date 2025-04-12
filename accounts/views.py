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
from .forms import SignUpForm
from .models import Product

# Register View
def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login View
def login_view(request):
    form = AuthenticationForm()
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')  # Adjust 'home' with the correct URL name if needed
            else:
                messages.error(request, "Invalid username or password.")
        else:
            # If form is not valid, show specific form errors
            messages.error(request, "Invalid username or password.")
            print(f"Form errors: {form.errors}")
    
    return render(request, 'registration/login.html', {
        'form': form,
    })

# Logout View (New, using POST)
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

# User Dashboard View
def user_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    user = request.user
    products = Product.objects.filter(seller=user)
    return render(request, 'accounts/user_dashboard.html', {'products': products})

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
                return redirect('accounts:password_reset_done')
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
