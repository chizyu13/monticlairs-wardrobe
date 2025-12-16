from django.contrib import admin
from .models import ReportCache, ReportSchedule, ReportAccess


@admin.register(ReportCache)
class ReportCacheAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'date_from', 'date_to', 'generated_at', 'is_expired')
    list_filter = ('report_type', 'generated_at')
    search_fields = ('report_type',)
    readonly_fields = ('generated_at', 'expires_at')
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'frequency', 'is_active', 'next_send', 'last_sent')
    list_filter = ('report_type', 'frequency', 'is_active')
    search_fields = ('email_recipients',)
    readonly_fields = ('created_at', 'last_sent')
    
    fieldsets = (
        ('Report Configuration', {
            'fields': ('report_type', 'frequency', 'is_active')
        }),
        ('Email Recipients', {
            'fields': ('email_recipients',),
            'description': 'Enter comma-separated email addresses'
        }),
        ('Schedule', {
            'fields': ('next_send', 'last_sent', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportAccess)
class ReportAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'report_type', 'accessed_at', 'export_format')
    list_filter = ('report_type', 'accessed_at', 'export_format')
    search_fields = ('user__username', 'report_type')
    readonly_fields = ('accessed_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
