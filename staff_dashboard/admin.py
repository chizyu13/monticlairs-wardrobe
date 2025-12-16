from django.contrib import admin
from .models import StaffApproval, CustomerInquiry, InquiryResponse, StaffAuditLog


@admin.register(StaffApproval)
class StaffApprovalAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_approved', 'approved_by', 'approved_at', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CustomerInquiry)
class CustomerInquiryAdmin(admin.ModelAdmin):
    list_display = ['subject', 'customer', 'status', 'resolved_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'customer__username', 'message']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(InquiryResponse)
class InquiryResponseAdmin(admin.ModelAdmin):
    list_display = ['inquiry', 'staff_member', 'created_at']
    list_filter = ['created_at']
    search_fields = ['inquiry__subject', 'staff_member__username', 'message']
    readonly_fields = ['created_at']


@admin.register(StaffAuditLog)
class StaffAuditLogAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'action', 'target_model', 'target_id', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['staff_member__username', 'target_model']
    readonly_fields = ['timestamp']
