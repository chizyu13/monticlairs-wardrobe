from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator


class Product(models.Model):
    # Product name
    name = models.CharField(max_length=255)

    # Product description (optional)
    description = models.TextField(blank=True)

    # Product price (must be a positive value, using MinValueValidator)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]  # Ensures price can't be zero or negative
    )
    
    # Seller: Either 'auth.User' or 'CustomUser' depending on which model you're using
    seller = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Change 'auth.User' to your custom model if needed

    # Category for the product (optional, or can be predefined if needed)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    # Product image (optional)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    # Product status (active, inactive, or sold)
    status = models.CharField(
        max_length=50, 
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('sold', 'Sold')],
        default='active'
    )

    # Created and updated timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Price validation (ensures the price is positive)
    def clean(self):
        if self.price <= 0:
            raise ValidationError('Price must be a positive number.')

    # String representation of the product
    def __str__(self):
        return f'{self.name} - {self.price}'

    # Optional: method to get the product's image URL
    def get_image_url(self):
        if self.image:
            return self.image.url
        return 'https://via.placeholder.com/150'  # Return a default image if none is set

    # Optional: Method to get product age
    def get_product_age(self):
        return timezone.now() - self.created_at


from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accounts_profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

from django.db import models
from django.contrib.auth.models import User
 # Assuming a Product model exists

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
