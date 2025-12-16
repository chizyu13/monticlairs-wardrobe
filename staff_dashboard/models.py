from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class StaffApproval(models.Model):
    """
    Model to track staff member approval status.
    Staff members must be approved by an administrator before accessing the dashboard.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_approval',
        verbose_name=_('User')
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Is Approved')
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_approvals_given',
        verbose_name=_('Approved By')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Approved At')
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Revoked At')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"{self.user.username} - {status}"

    class Meta:
        verbose_name = _('Staff Approval')
        verbose_name_plural = _('Staff Approvals')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_approved']),
        ]


class CustomerInquiry(models.Model):
    """
    Model to track customer inquiries and support requests.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inquiries',
        verbose_name=_('Customer')
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('Subject')
    )
    message = models.TextField(
        verbose_name=_('Message')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_inquiries',
        verbose_name=_('Resolved By')
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Resolved At')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    def __str__(self):
        return f"{self.subject} - {self.customer.username}"

    class Meta:
        verbose_name = _('Customer Inquiry')
        verbose_name_plural = _('Customer Inquiries')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]


class InquiryResponse(models.Model):
    """
    Model to track staff responses to customer inquiries.
    """
    inquiry = models.ForeignKey(
        CustomerInquiry,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('Inquiry')
    )
    staff_member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inquiry_responses',
        verbose_name=_('Staff Member')
    )
    message = models.TextField(
        verbose_name=_('Message')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    def __str__(self):
        return f"Response by {self.staff_member.username} to {self.inquiry.subject}"

    class Meta:
        verbose_name = _('Inquiry Response')
        verbose_name_plural = _('Inquiry Responses')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['inquiry', 'created_at']),
        ]


class StaffAuditLog(models.Model):
    """
    Model to track all staff actions for audit purposes.
    """
    ACTION_CHOICES = [
        ('order_status_update', _('Order Status Update')),
        ('product_update', _('Product Update')),
        ('stock_update', _('Stock Update')),
        ('inquiry_resolved', _('Inquiry Resolved')),
    ]

    staff_member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name=_('Staff Member')
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name=_('Action')
    )
    target_model = models.CharField(
        max_length=50,
        verbose_name=_('Target Model')
    )
    target_id = models.PositiveIntegerField(
        verbose_name=_('Target ID')
    )
    changes = models.JSONField(
        verbose_name=_('Changes'),
        help_text=_('JSON object containing the changes made')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp')
    )

    def __str__(self):
        return f"{self.staff_member.username} - {self.action} - {self.timestamp}"

    class Meta:
        verbose_name = _('Staff Audit Log')
        verbose_name_plural = _('Staff Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['staff_member', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
