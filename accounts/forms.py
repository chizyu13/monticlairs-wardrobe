from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from home.models import Profile  # Import from home app

def validate_password_strength(password):
    """
    Validate password strength:
    - Must be at least 8 characters
    - Must contain a mixture of characters and symbols
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters.")
    
    # Check for at least one letter
    has_letter = re.search(r'[a-zA-Z]', password)
    # Check for at least one symbol (special character)
    has_symbol = re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password)
    
    if not has_letter or not has_symbol:
        raise ValidationError(
            "Password must contain a mixture of characters and symbols. "
            "Example: Pass@1 or Pwd#2"
        )

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a unique username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def clean_password1(self):
        """Validate password strength."""
        password1 = self.cleaned_data.get('password1')
        if password1:
            validate_password_strength(password1)
        return password1
    
    def clean_email(self):
        """Validate email format and check if it already exists."""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError("Email is required.")
        
        # Email format validation - must contain @ and domain
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError(
                "Please enter a valid email address (e.g., munachizyuka@gmail.com). "
                "Email must contain '@' and a valid domain."
            )
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        
        return email
        
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Create a strong password'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a unique username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
        }
    
    def clean_password(self):
        """Validate password strength."""
        password = self.cleaned_data.get('password')
        if password:
            validate_password_strength(password)
        return password
    
    def clean_email(self):
        """Validate email format and check if it already exists."""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError("Email is required.")
        
        # Email format validation - must contain @ and domain
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError(
                "Please enter a valid email address (e.g., munachizyuka@gmail.com). "
                "Email must contain '@' and a valid domain."
            )
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us a bit about yourself and your style preferences...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the role field since this is now a customer-only boutique
        # All new users will be customers by default
