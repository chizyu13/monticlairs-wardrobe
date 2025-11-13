from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
from datetime import timedelta

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
    image = models.ImageField(upload_to='categories/%Y/%m/%d/', null=True, blank=True, verbose_name=_("Category Image"))
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Icon Class"), help_text=_("Font Awesome icon class (e.g., fas fa-gem)"))
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
    
    APPROVAL_CHOICES = [
        ("pending", _("Pending Approval")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Product Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
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
    static_image = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Static Image Path"),
        help_text=_("Path to image in static folder (e.g., 'images/Jewerly/watch1.jpg')")
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
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default="pending",
        verbose_name=_("Approval Status")
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_products",
        verbose_name=_("Approved By")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approved At")
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
    
    def get_image_url(self):
        """Get the image URL, preferring uploaded image over static image."""
        if self.image:
            return self.image.url
        elif self.static_image:
            from django.templatetags.static import static
            return static(self.static_image)
        return None

    def is_in_stock(self):
        """Check if the product is available for purchase."""
        return self.stock > 0 and self.status == "active" and self.approval_status == "approved"
    
    def get_available_stock(self):
        """Get available stock after accounting for active reservations."""
        # Import here to avoid circular import
        from home.models import StockReservation
        return StockReservation.get_available_stock(self)
    
    def get_average_rating(self):
        """Get average rating for this product."""
        from django.db.models import Avg
        result = self.reviews.aggregate(Avg('rating'))
        return round(result['rating__avg'] or 0, 1)
    
    def get_rating_count(self):
        """Get total number of reviews for this product."""
        return self.reviews.count()
    
    def get_rating_distribution(self):
        """Get distribution of ratings (1-5 stars)."""
        distribution = {}
        total = self.get_rating_count()
        
        for rating in range(1, 6):
            count = self.reviews.filter(rating=rating).count()
            percentage = (count / total * 100) if total > 0 else 0
            distribution[rating] = {
                'count': count,
                'percentage': round(percentage, 1)
            }
        
        return distribution
    
    def get_verified_review_count(self):
        """Get count of verified purchase reviews."""
        return self.reviews.filter(is_verified_purchase=True).count()
    
    def is_available_for_customers(self):
        """Check if the product is available for customers to see and purchase."""
        return self.approval_status == "approved" and self.status == "active"
    
    def is_low_stock(self, threshold=5):
        """Check if the product stock is below the threshold."""
        return 0 < self.stock <= threshold
    
    def get_stock_status(self):
        """Get a human-readable stock status."""
        if self.stock == 0:
            return "out_of_stock"
        elif self.is_low_stock():
            return "low_stock"
        else:
            return "in_stock"
    
    def get_stock_status_display(self):
        """Get a display-friendly stock status message."""
        status = self.get_stock_status()
        if status == "out_of_stock":
            return "Out of Stock"
        elif status == "low_stock":
            return f"Low Stock ({self.stock} left)"
        else:
            return "In Stock"

    def reduce_stock(self, quantity, reason=None, changed_by=None, order=None):
        """Reduce stock by the specified quantity, with validation and history tracking."""
        if self.status != "active":
            raise ValueError(_(f"Cannot reduce stock for {self.name}. Status is '{self.status}', must be 'active'."))
        if quantity > self.stock:
            raise ValueError(_(f"Insufficient stock for {self.name}. Available: {self.stock}, Requested: {quantity}"))
        
        # Record history before changing stock
        from home.models import StockHistory
        StockHistory.record_change(
            product=self,
            change_type='sale',
            quantity_change=-quantity,
            reason=reason,
            changed_by=changed_by,
            order=order
        )
        
        self.stock -= quantity
        self.save(update_fields=['stock'])

    def increase_stock(self, quantity, reason=None, changed_by=None):
        """Increase stock by the specified quantity with history tracking."""
        if quantity < 0:
            raise ValueError(_(f"Cannot increase stock by a negative quantity: {quantity}"))
        
        # Record history before changing stock
        from home.models import StockHistory
        StockHistory.record_change(
            product=self,
            change_type='restock',
            quantity_change=quantity,
            reason=reason,
            changed_by=changed_by
        )
        
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
        INSIDE = "inside", _("Lusaka City")
        OUTSIDE = "outside", _("Outside Lusaka")

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
    location = models.CharField(max_length=10, choices=LocationChoices.choices, verbose_name=_("Delivery Area"), blank=True, null=True)
    room_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Delivery Address"))
    delivery_address = models.TextField(blank=True, null=True, verbose_name=_("Full Delivery Address"))
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
        SHIPPED = "shipped", _("Courier is on the way")
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

class Review(models.Model):
    RATING_CHOICES = [
        (1, _("1 Star - Poor")),
        (2, _("2 Stars - Fair")),
        (3, _("3 Stars - Good")),
        (4, _("4 Stars - Very Good")),
        (5, _("5 Stars - Excellent")),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Product")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Reviewer")
    )
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        verbose_name=_("Rating")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Review Title")
    )
    comment = models.TextField(
        verbose_name=_("Review Comment")
    )
    is_verified_purchase = models.BooleanField(
        default=False,
        verbose_name=_("Verified Purchase")
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
        return f"Review by {self.user.username} for {self.product.name}"
    
    @classmethod
    def user_has_purchased(cls, user, product):
        """
        Check if a user has purchased a specific product.
        
        Args:
            user: User instance
            product: Product instance
        
        Returns:
            bool: True if user has purchased the product
        """
        from home.models import Order
        return Order.objects.filter(
            user=user,
            product=product,
            status__in=['delivered', 'completed']
        ).exists()
    
    @classmethod
    def user_can_review(cls, user, product):
        """
        Check if a user can review a product.
        
        Args:
            user: User instance
            product: Product instance
        
        Returns:
            tuple: (can_review, reason)
        """
        # Check if user has already reviewed
        if cls.objects.filter(user=user, product=product).exists():
            return False, "You have already reviewed this product"
        
        # Check if user has purchased the product
        if not cls.user_has_purchased(user, product):
            return False, "You can only review products you have purchased"
        
        return True, None
    
    @classmethod
    def create_verified_review(cls, user, product, rating, title, comment):
        """
        Create a review with automatic purchase verification.
        
        Args:
            user: User instance
            product: Product instance
            rating: Rating (1-5)
            title: Review title
            comment: Review comment
        
        Returns:
            tuple: (review, created, error_message)
        """
        # Check if user can review
        can_review, reason = cls.user_can_review(user, product)
        if not can_review:
            return None, False, reason
        
        # Check if user has purchased
        is_verified = cls.user_has_purchased(user, product)
        
        # Create review
        review = cls.objects.create(
            user=user,
            product=product,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=is_verified
        )
        
        return review, True, None
    
    def get_average_rating(product):
        """Get average rating for a product."""
        from django.db.models import Avg
        result = Review.objects.filter(product=product).aggregate(Avg('rating'))
        return result['rating__avg'] or 0

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        unique_together = [("product", "user")]
        indexes = [
            models.Index(fields=['product', 'rating']),
            models.Index(fields=['created_at']),
        ]


class StockReservation(models.Model):
    """
    Model to track stock reservations during checkout process.
    Reservations expire after a set time to prevent stock from being held indefinitely.
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('expired', _('Expired')),
        ('cancelled', _('Cancelled')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stock_reservations',
        verbose_name=_('User')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_reservations',
        verbose_name=_('Product')
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Quantity')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    expires_at = models.DateTimeField(
        verbose_name=_('Expires At')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Stock Reservation')
        verbose_name_plural = _('Stock Reservations')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['product', 'status']),
            models.Index(fields=['expires_at', 'status']),
        ]
    
    def __str__(self):
        return f"Reservation: {self.quantity}x {self.product.name} for {self.user.username}"
    
    def is_expired(self):
        """Check if the reservation has expired."""
        return timezone.now() > self.expires_at and self.status == 'active'
    
    def mark_as_expired(self):
        """Mark the reservation as expired."""
        if self.status == 'active':
            self.status = 'expired'
            self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_completed(self):
        """Mark the reservation as completed (order placed)."""
        if self.status == 'active':
            self.status = 'completed'
            self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_cancelled(self):
        """Mark the reservation as cancelled."""
        if self.status == 'active':
            self.status = 'cancelled'
            self.save(update_fields=['status', 'updated_at'])
    
    @classmethod
    def create_reservation(cls, user, product, quantity, expiry_minutes=15):
        """
        Create a new stock reservation.
        Returns (reservation, created) tuple.
        """
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        # Check if there's an existing active reservation for this user and product
        existing = cls.objects.filter(
            user=user,
            product=product,
            status='active'
        ).first()
        
        if existing:
            # Update existing reservation
            existing.quantity = quantity
            existing.expires_at = expires_at
            existing.save(update_fields=['quantity', 'expires_at', 'updated_at'])
            return existing, False
        else:
            # Create new reservation
            reservation = cls.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                expires_at=expires_at
            )
            return reservation, True
    
    @classmethod
    def get_reserved_stock(cls, product):
        """Get the total quantity of active reservations for a product."""
        return cls.objects.filter(
            product=product,
            status='active',
            expires_at__gt=timezone.now()
        ).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @classmethod
    def get_available_stock(cls, product):
        """Get the available stock after accounting for active reservations."""
        reserved = cls.get_reserved_stock(product)
        return max(0, product.stock - reserved)
    
    @classmethod
    def cleanup_expired_reservations(cls):
        """Mark all expired reservations as expired."""
        expired_count = cls.objects.filter(
            status='active',
            expires_at__lte=timezone.now()
        ).update(status='expired', updated_at=timezone.now())
        return expired_count


class StockHistory(models.Model):
    """
    Model to track all stock changes for audit and reporting purposes.
    """
    CHANGE_TYPE_CHOICES = [
        ('initial', _('Initial Stock')),
        ('restock', _('Restocked')),
        ('sale', _('Sold')),
        ('return', _('Returned')),
        ('adjustment', _('Manual Adjustment')),
        ('reservation', _('Reserved')),
        ('reservation_released', _('Reservation Released')),
        ('damaged', _('Damaged/Lost')),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_history',
        verbose_name=_('Product')
    )
    change_type = models.CharField(
        max_length=30,
        choices=CHANGE_TYPE_CHOICES,
        verbose_name=_('Change Type')
    )
    quantity_change = models.IntegerField(
        verbose_name=_('Quantity Change'),
        help_text=_('Positive for additions, negative for reductions')
    )
    stock_before = models.PositiveIntegerField(
        verbose_name=_('Stock Before')
    )
    stock_after = models.PositiveIntegerField(
        verbose_name=_('Stock After')
    )
    reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Reason')
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_changes',
        verbose_name=_('Changed By')
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_changes',
        verbose_name=_('Related Order')
    )
    reservation = models.ForeignKey(
        StockReservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_changes',
        verbose_name=_('Related Reservation')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Stock History')
        verbose_name_plural = _('Stock Histories')
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['change_type', '-created_at']),
            models.Index(fields=['changed_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.product.name}: {self.quantity_change:+d} ({self.change_type})"
    
    @classmethod
    def record_change(cls, product, change_type, quantity_change, reason=None, 
                     changed_by=None, order=None, reservation=None):
        """
        Record a stock change in the history.
        
        Args:
            product: Product instance
            change_type: Type of change (from CHANGE_TYPE_CHOICES)
            quantity_change: Amount changed (positive or negative)
            reason: Optional reason for the change
            changed_by: User who made the change
            order: Related order (if applicable)
            reservation: Related reservation (if applicable)
        
        Returns:
            StockHistory instance
        """
        stock_before = product.stock
        stock_after = max(0, stock_before + quantity_change)
        
        history = cls.objects.create(
            product=product,
            change_type=change_type,
            quantity_change=quantity_change,
            stock_before=stock_before,
            stock_after=stock_after,
            reason=reason,
            changed_by=changed_by,
            order=order,
            reservation=reservation
        )
        
        return history
    
    @classmethod
    def get_product_history(cls, product, days=30):
        """Get stock history for a product for the last N days."""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            product=product,
            created_at__gte=cutoff_date
        ).select_related('changed_by', 'order', 'reservation')
    
    @classmethod
    def get_stock_summary(cls, product):
        """Get a summary of stock changes for a product."""
        from django.db.models import Sum, Count
        
        summary = cls.objects.filter(product=product).aggregate(
            total_added=Sum('quantity_change', filter=models.Q(quantity_change__gt=0)),
            total_removed=Sum('quantity_change', filter=models.Q(quantity_change__lt=0)),
            total_changes=Count('id')
        )
        
        return {
            'total_added': summary['total_added'] or 0,
            'total_removed': abs(summary['total_removed'] or 0),
            'total_changes': summary['total_changes'] or 0,
            'current_stock': product.stock
        }


class Store(models.Model):
    """Model for physical store locations."""
    name = models.CharField(max_length=255, verbose_name=_("Store Name"))
    address = models.TextField(verbose_name=_("Address"))
    city = models.CharField(max_length=100, default="Lusaka", verbose_name=_("City"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_("Latitude"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_("Longitude"))
    phone_number = models.CharField(
        max_length=15,
        validators=[validate_zambian_phone],
        verbose_name=_("Phone Number")
    )
    whatsapp_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[validate_zambian_phone],
        verbose_name=_("WhatsApp Number")
    )
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email"))
    opening_hours = models.TextField(
        help_text=_("e.g., Mon-Fri: 9AM-6PM, Sat: 10AM-4PM"),
        verbose_name=_("Opening Hours")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_pickup_point = models.BooleanField(default=True, verbose_name=_("Available as Pickup Point"))
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_stores",
        verbose_name=_("Store Manager")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.name} - {self.city}"

    class Meta:
        ordering = ['city', 'name']
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")
