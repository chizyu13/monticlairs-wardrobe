# payment/models.py
from django.db import models
from django.contrib.auth.models import User

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('airtel', 'Airtel Money'),
        ('mtn', 'MTN Mobile Money'),
        ('stripe', 'Stripe'),
        ('cash', 'Cash'),
        ('delivery', 'Payment on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True, help_text='Error details if payment failed')
    retry_count = models.PositiveIntegerField(default=0, help_text='Number of retry attempts')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    gps_location = models.CharField(max_length=100, blank=True, null=True)
    hostel_name = models.CharField(max_length=100, blank=True, null=True)
    room_number = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['reference']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.method} - {self.reference}"
    
    def can_retry(self, max_retries=3):
        """Check if payment can be retried."""
        return self.status == 'failed' and self.retry_count < max_retries
    
    def mark_as_completed(self):
        """Mark payment as completed."""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])
    
    def mark_as_failed(self, error_message=None):
        """Mark payment as failed."""
        self.status = 'failed'
        if error_message:
            self.error_message = error_message[:500]
        self.save(update_fields=['status', 'error_message', 'updated_at'])
    
    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1
        self.save(update_fields=['retry_count', 'updated_at'])
