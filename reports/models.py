from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta


class ReportCache(models.Model):
    """Cache for generated reports to improve performance"""
    REPORT_TYPES = [
        ('daily_sales', _('Daily Sales Report')),
        ('order_status', _('Order Status Report')),
        ('product_sales', _('Product Sales Report')),
        ('stock_level', _('Stock Level Report')),
        ('customer_growth', _('Customer Growth Report')),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    date_from = models.DateField()
    date_to = models.DateField()
    data = models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_type', 'date_from', 'date_to']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} ({self.date_from} to {self.date_to})"
    
    def is_expired(self):
        return timezone.now() > self.expires_at


class ReportSchedule(models.Model):
    """Schedule for automated report generation"""
    FREQUENCY_CHOICES = [
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
    ]
    
    REPORT_TYPES = [
        ('daily_sales', _('Daily Sales Report')),
        ('order_status', _('Order Status Report')),
        ('product_sales', _('Product Sales Report')),
        ('stock_level', _('Stock Level Report')),
        ('customer_growth', _('Customer Growth Report')),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    email_recipients = models.TextField(help_text=_("Comma-separated email addresses"))
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    next_send = models.DateTimeField()
    
    class Meta:
        ordering = ['next_send']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.get_frequency_display()}"


class ReportAccess(models.Model):
    """Track report access for audit purposes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_accesses')
    report_type = models.CharField(max_length=50)
    accessed_at = models.DateTimeField(auto_now_add=True)
    export_format = models.CharField(max_length=20, null=True, blank=True)  # pdf, excel, csv
    
    class Meta:
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['user', 'accessed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.report_type} ({self.accessed_at})"
