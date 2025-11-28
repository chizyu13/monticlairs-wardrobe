# Add this to payment/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Refund(models.Model):
    """Model to track payment refunds for cancelled orders"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE, related_name='refunds')
    order = models.ForeignKey('home.Order', on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(help_text='Reason for refund')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin approval tracking
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='refunds_requested')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='refunds_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # PIN verification
    pin_verified = models.BooleanField(default=False)
    pin_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True, null=True, help_text='Admin notes')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', 'status']),
            models.Index(fields=['order']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Refund #{self.id} - {self.payment.reference} - ZMW {self.amount}"
    
    def approve_refund(self, admin_user):
        """Approve the refund"""
        self.status = 'approved'
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
    
    def complete_refund(self):
        """Mark refund as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])
    
    def reject_refund(self, reason=None):
        """Reject the refund"""
        self.status = 'rejected'
        if reason:
            self.notes = reason
        self.save(update_fields=['status', 'notes', 'updated_at'])
    
    def verify_pin(self):
        """Mark PIN as verified"""
        self.pin_verified = True
        self.pin_verified_at = timezone.now()
        self.save(update_fields=['pin_verified', 'pin_verified_at', 'updated_at'])
