from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_customer_name', 'product', 'created_at', 'is_closed')
    list_filter = ('created_at', 'is_closed')
    search_fields = ('user__username', 'guest_name', 'guest_email')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_customer_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return obj.guest_name or 'Guest'
    get_customer_name.short_description = 'Customer'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender_name', 'is_admin', 'created_at')
    list_filter = ('is_admin', 'created_at')
    search_fields = ('sender_name', 'message', 'session__guest_name')
    readonly_fields = ('created_at',)
