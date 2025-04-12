from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal

import re
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# Custom validator for Zambian phone number
def validate_zambian_phone(value):
    if not re.match(r'^\+260\d{9}$', value):
        raise ValidationError(_("Enter a valid Zambian number (e.g., +260123456789)"))
    return value

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Category Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', verbose_name=_("Created By"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from .models import Category  # Assuming Category is in the same models.py; adjust if elsewhere

class Product(models.Model):
    STATUS_CHOICES = [
        ("active", _("Active")),
        ("inactive", _("Inactive")),
        ("sold", _("Sold")),
        ("draft", _("Draft")),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Product Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_("Price")
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Seller")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Category")
    )
    image = models.ImageField(
        upload_to="products/%Y/%m/%d/",
        null=True,
        blank=True,
        verbose_name=_("Product Image")
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status")
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Stock Quantity")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )

    def __str__(self):
        return self.name

    def is_in_stock(self):
        """Check if the product is available for purchase."""
        return self.stock > 0 and self.status == "active"

    def reduce_stock(self, quantity):
        """Reduce stock by the specified quantity, with validation."""
        if self.status != "active":
            raise ValueError(_(f"Cannot reduce stock for {self.name}. Status is '{self.status}', must be 'active'."))
        if quantity > self.stock:
            raise ValueError(_(f"Insufficient stock for {self.name}. Available: {self.stock}, Requested: {quantity}"))
        self.stock -= quantity
        self.save(update_fields=['stock'])

    def increase_stock(self, quantity):
        """Increase stock by the specified quantity."""
        if quantity < 0:
            raise ValueError(_(f"Cannot increase stock by a negative quantity: {quantity}"))
        self.stock += quantity
        self.save(update_fields=['stock'])

    def mark_as_sold(self):
        """Mark the product as sold and set stock to 0."""
        self.status = "sold"
        self.stock = 0
        self.save(update_fields=['status', 'stock'])

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        indexes = [
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['created_at']),
        ]
class Checkout(models.Model):
    class LocationChoices(models.TextChoices):
        INSIDE = "inside", _("Inside Campus")
        OUTSIDE = "outside", _("Outside Campus")

    class PaymentChoices(models.TextChoices):
        CASH = "cash", _("Cash")
        DELIVERY = "delivery", _("Payment on Delivery")
        MTN = "mtn", _("MTN Mobile Money")
        AIRTEL = "airtel", _("Airtel Money")

    class PaymentStatusChoices(models.TextChoices):
        PENDING = "pending", _("Pending")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checkouts", verbose_name=_("User"))
    location = models.CharField(max_length=10, choices=LocationChoices.choices, verbose_name=_("Location"))
    room_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Room Number"))
    phone_number = models.CharField(max_length=15, validators=[validate_zambian_phone], verbose_name=_("Phone Number"))
    gps_location = models.CharField(max_length=255, verbose_name=_("GPS Location"))
    payment_method = models.CharField(max_length=10, choices=PaymentChoices.choices, verbose_name=_("Payment Method"))
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)], verbose_name=_("Delivery Fee"))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Transaction ID"))
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.PENDING, verbose_name=_("Payment Status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"Checkout #{self.id} by {self.user.username}"
from decimal import Decimal

def get_total_cost(self):
    subtotal = sum(order.total_price for order in self.orders.all())
    return subtotal + Decimal(str(self.delivery_fee))


    def save(self, *args, **kwargs):
        if self.payment_method == self.PaymentChoices.DELIVERY and self.delivery_fee == 0.00:
            self.delivery_fee = 20.00 if self.location == self.LocationChoices.INSIDE else 50.00
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Checkout")
        verbose_name_plural = _("Checkouts")

validate_zambian_phone = RegexValidator(
    regex=r'^\+260\d{9}$',
    message="Phone number must be in the format: '+260xxxxxxxxx' (10 digits total after +260)."
)


from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

# Custom validator for Zambian phone numbers (example)
validate_zambian_phone = RegexValidator(
    regex=r'^(09|\+2609|2609)[0-9]{8}$',
    message="Phone number must be a valid Zambian number (e.g., 0971234567 or +260971234567)."
)

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",  # Kept as 'profile' assuming single Profile model
        verbose_name=_("User")
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Bio")
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Location")
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[validate_zambian_phone],
        verbose_name=_("Phone Number")
    )
    profile_picture = models.ImageField(
        upload_to="profiles/%Y/%m/%d/",
        null=True,
        blank=True,
        default="profiles/default_profile.jpg",  # Ensure this file exists in media
        verbose_name=_("Profile Picture")
    )

    def save(self, *args, **kwargs):
        # Handle profile picture updates (e.g., delete old image if replaced)
        if self.pk:
            old_profile = Profile.objects.get(pk=self.pk)
            if old_profile.profile_picture and self.profile_picture != old_profile.profile_picture:
                old_profile.profile_picture.delete(save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile for {self.user.username}"

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        SHIPPED = "shipped", _("Shipped")
        DELIVERED = "delivered", _("Delivered")
        CANCELLED = "cancelled", _("Cancelled")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name=_("User"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders", verbose_name=_("Product"))
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name=_("Quantity"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)], verbose_name=_("Total Price"))
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING, verbose_name=_("Status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    checkout = models.ForeignKey(Checkout, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name=_("Checkout"))

    def __str__(self):
        return f"Order #{self.id} - {self.product.name}"

    def calculate_total(self):
        return self.product.price * self.quantity

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                self.total_price = self.calculate_total()
                self.product.reduce_stock(self.quantity)
            elif self.quantity != self._original_quantity():
                diff = self.quantity - self._original_quantity()
                if diff > 0:
                    self.product.reduce_stock(diff)
                elif diff < 0:
                    self.product.stock += abs(diff)
                    self.product.save()
                self.total_price = self.calculate_total()
            super().save(*args, **kwargs)

    def _original_quantity(self):
        if self.pk:
            return Order.objects.get(pk=self.pk).quantity
        return self.quantity

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales", verbose_name=_("Product"))
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales", verbose_name=_("Seller"))
    buyer = models.ForeignKey(User, related_name="purchases", on_delete=models.CASCADE, verbose_name=_("Buyer"))
    sale_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Sale Date"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Total Amount"))
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name=_("Quantity"))

    def __str__(self):
        return f"Sale #{self.id} - {self.product.name}"

    class Meta:
        ordering = ["-sale_date"]
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")
