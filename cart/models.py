from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone


# Checkout model
class Checkout(models.Model):
    LOCATION_CHOICES = [
        ("inside", "Inside Campus"),
        ("outside", "Outside Campus"),
    ]
    PAYMENT_CHOICES = [
        ("cash", "Cash"),
        ("delivery", "Payment on Delivery"),
        ("mtn", "MTN Mobile Money"),
        ("airtel", "Airtel Money"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_checkouts",
    )
    location = models.CharField(max_length=10, choices=LOCATION_CHOICES)
    room_number = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?\d{9,15}$', "Enter a valid phone number (e.g., +260123456789)")],
    )
    gps_location = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Checkout by {self.user.username} - {self.location} - {self.payment_method}"

    def get_total_cost(self):
        """Calculate total cost including delivery fee based on user's cart items."""
        cart_items = self.user.cart_items.filter(added_at__lte=self.created_at)
        subtotal = sum(item.get_total_price() for item in cart_items)
        return subtotal + self.delivery_fee

    class Meta:
        ordering = ["-created_at"]


# Cart model
class Cart(models.Model):
    def get_default_user():
        """Dynamic default: Returns first active user or falls back to ID 1."""
        if User.objects.exists():
            first_active_user = User.objects.filter(is_active=True).first()
            return first_active_user.id if first_active_user else 1
        return 1  # Fallback if no users exist

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items",
        default=get_default_user,
    )
    product = models.ForeignKey(
        "home.Product",
        on_delete=models.CASCADE,
        related_name="cart_entries",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.quantity}"

    def get_total_price(self):
        """Calculate total price for this cart item."""
        return self.product.price * self.quantity

    class Meta:
        ordering = ["-added_at"]
        unique_together = ["user", "product"]
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
