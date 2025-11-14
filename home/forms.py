from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product, Checkout, Category, Review, ProductManual, PlatformGuide, GuideAttachment

# Product Form
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image', 'stock', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("Stock can't be negative.")
        return stock


# Checkout Form
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Checkout
        fields = ['location', 'room_number', 'phone_number', 'gps_location', 'payment_method']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your location'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter room number (if inside campus)'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'gps_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter GPS coordinates'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(phone_number) < 10:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone_number


# Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter category description'}),
        }


from django import forms
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@example.com'):  # Replace or remove this rule
            raise forms.ValidationError("Please use a valid email address.")
        return email

# app/forms.py

from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    subject = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'What can we help you with?'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control textarea',
            'rows': 5,
            'placeholder': 'Tell us how we can help you...'
        })
    )



# Review Form
class ReviewForm(forms.ModelForm):
    """Form for submitting product reviews."""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(
                choices=Review.RATING_CHOICES,
                attrs={'class': 'rating-input'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Summarize your experience',
                'maxlength': '200'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts about this product...',
                'rows': 5,
                'minlength': '10',
                'maxlength': '500'
            }),
        }
        labels = {
            'rating': 'Your Rating',
            'title': 'Review Title',
            'comment': 'Your Review',
        }
        help_texts = {
            'rating': 'Select a rating from 1 (Poor) to 5 (Excellent)',
            'title': 'Give your review a short title',
            'comment': 'Write at least 10 characters (maximum 500)',
        }
    
    def clean_rating(self):
        """Validate rating is between 1 and 5."""
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating
    
    def clean_comment(self):
        """Validate comment length."""
        comment = self.cleaned_data.get('comment')
        if len(comment) < 10:
            raise forms.ValidationError('Review must be at least 10 characters long.')
        if len(comment) > 500:
            raise forms.ValidationError('Review must not exceed 500 characters.')
        return comment
    
    def clean_title(self):
        """Validate title length."""
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters long.')
        return title



# Product Manual Form
class ProductManualForm(forms.ModelForm):
    """Form for uploading product manuals."""
    
    class Meta:
        model = ProductManual
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_("File size must not exceed 10MB"))
            
            # Validate file extension
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError(_("Only PDF files are allowed"))
            
            # Validate file content type
            if file.content_type != 'application/pdf':
                raise forms.ValidationError(_("Invalid file type. Only PDF files are allowed"))
        
        return file


# Platform Guide Form
class PlatformGuideForm(forms.ModelForm):
    """Form for creating/editing platform guides."""
    
    class Meta:
        model = PlatformGuide
        fields = ['title', 'category', 'description', 'content', 'featured', 'display_order', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter guide title'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief summary of the guide'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Full guide content (HTML supported)'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Guide Title',
            'category': 'Category',
            'description': 'Short Description',
            'content': 'Guide Content',
            'featured': 'Feature this guide',
            'display_order': 'Display Order',
            'is_published': 'Publish this guide',
        }
        help_texts = {
            'display_order': 'Lower numbers appear first',
            'featured': 'Featured guides appear prominently on the Help Center homepage',
        }
    
    def clean_title(self):
        """Validate title length."""
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title
    
    def clean_description(self):
        """Validate description length."""
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise forms.ValidationError('Description must be at least 10 characters long.')
        return description
    
    def clean_content(self):
        """Validate content length."""
        content = self.cleaned_data.get('content')
        if len(content) < 50:
            raise forms.ValidationError('Content must be at least 50 characters long.')
        return content


# Guide Attachment Form
class GuideAttachmentForm(forms.ModelForm):
    """Form for uploading guide attachments."""
    
    class Meta:
        model = GuideAttachment
        fields = ['file', 'caption']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional caption for the attachment'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_("File size must not exceed 10MB"))
            
            # Validate file type
            ext = file.name.lower().split('.')[-1]
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError(_("Only PDF and image files (JPG, PNG) are allowed"))
            
            # Validate content type
            valid_types = ['application/pdf', 'image/jpeg', 'image/png']
            if file.content_type not in valid_types:
                raise forms.ValidationError(_("Invalid file type"))
        
        return file
