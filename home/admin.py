from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import Product, Category, Checkout, Profile, Order, Sale, StockHistory, StockReservation, Store

# Unregister the default UserAdmin
User = get_user_model()
admin.site.unregister(User)  # Unregister the default User admin

# Register Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'seller', 'category', 'status', 'stock', 'created_at', 'updated_at']
    search_fields = ['name', 'description', 'seller__username']
    list_filter = ['status', 'category', 'seller', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_editable = ['price', 'status', 'stock']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 20
    autocomplete_fields = ['seller', 'category']
    actions = ['mark_as_sold', 'mark_as_active', 'reduce_stock']
    prepopulated_fields = {'name': ('name',)}  # Note: This is unusual; typically used with slugs

    def mark_as_sold(self, request, queryset):
        updated = queryset.update(status='sold', stock=0)
        self.message_user(request, f"{updated} product(s) marked as sold and stock set to 0.")
    mark_as_sold.short_description = "Mark selected products as sold and clear stock"

    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} product(s) marked as active.")
    mark_as_active.short_description = "Mark selected products as active"

    def reduce_stock(self, request, queryset):
        for product in queryset:
            if product.stock > 0:
                product.reduce_stock(1)
        self.message_user(request, "Stock reduced by 1 for selected products with available stock.")
    reduce_stock.short_description = "Reduce stock by 1 for selected products"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('seller', 'category')

# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_by', 'created_at', 'updated_at', 'product_count']
    search_fields = ['name', 'description', 'created_by__username']
    list_filter = ['created_at', 'updated_at', 'created_by']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 20
    autocomplete_fields = ['created_by']
    fields = ['name', 'description', 'image', 'icon', 'created_by', 'created_at', 'updated_at']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

# Register Checkout model
@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'location', 'payment_method', 'payment_status', 'delivery_fee', 'created_at', 'order_count']
    search_fields = ['user__username', 'phone_number', 'transaction_id']
    list_filter = ['location', 'payment_method', 'payment_status', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 20
    autocomplete_fields = ['user']
    actions = ['mark_paid']

    def order_count(self, obj):
        return obj.order_set.count()
    order_count.short_description = "Orders"

    def mark_paid(self, request, queryset):
        updated = queryset.update(payment_status='paid')
        self.message_user(request, f"{updated} checkout(s) marked as paid.")
    mark_paid.short_description = "Mark selected checkouts as paid"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Register Profile model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'phone_number', 'bio_summary', 'created_at']
    search_fields = ['user__username', 'location', 'phone_number', 'bio']
    list_filter = ['location']
    ordering = ['user__username']
    readonly_fields = ['created_at']
    list_per_page = 20
    autocomplete_fields = ['user']

    def bio_summary(self, obj):
        return obj.bio[:50] + "..." if obj.bio and len(obj.bio) > 50 else obj.bio or "-"
    bio_summary.short_description = "Bio Summary"

    def created_at(self, obj):
        return obj.user.date_joined
    created_at.short_description = "Created At"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Register Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'total_price', 'status', 'checkout', 'created_at']
    search_fields = ['user__username', 'product__name']
    list_filter = ['status', 'created_at', 'checkout']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 20
    autocomplete_fields = ['user', 'product', 'checkout']
    list_editable = ['quantity', 'status']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product', 'checkout')

# Register Sale model
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'seller', 'buyer', 'quantity', 'total_amount', 'sale_date']
    search_fields = ['product__name', 'seller__username', 'buyer__username']
    list_filter = ['sale_date', 'seller', 'buyer']
    ordering = ['-sale_date']
    readonly_fields = ['sale_date']
    date_hierarchy = 'sale_date'
    list_per_page = 20
    autocomplete_fields = ['product', 'seller', 'buyer']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'seller', 'buyer')

# Custom User Admin
class CustomUserAdmin(DefaultUserAdmin):
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')

# Register the custom User admin
admin.site.register(User, CustomUserAdmin)

# Register StockHistory model
@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'change_type', 'quantity_change', 'stock_before', 
                    'stock_after', 'changed_by', 'created_at']
    search_fields = ['product__name', 'reason', 'changed_by__username']
    list_filter = ['change_type', 'created_at', 'changed_by']
    ordering = ['-created_at']
    readonly_fields = ['product', 'change_type', 'quantity_change', 'stock_before', 
                      'stock_after', 'reason', 'changed_by', 'order', 'reservation', 'created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    autocomplete_fields = ['product', 'changed_by', 'order', 'reservation']
    
    def has_add_permission(self, request):
        # Prevent manual creation of stock history records
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of stock history records
        return False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'changed_by', 'order', 'reservation'
        )

# Register StockReservation model
@admin.register(StockReservation)
class StockReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'status', 'expires_at', 
                    'is_expired_display', 'created_at']
    search_fields = ['user__username', 'product__name']
    list_filter = ['status', 'created_at', 'expires_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'is_expired_display']
    date_hierarchy = 'created_at'
    list_per_page = 50
    autocomplete_fields = ['user', 'product']
    actions = ['mark_as_expired', 'mark_as_cancelled']
    
    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.short_description = 'Is Expired'
    is_expired_display.boolean = True
    
    def mark_as_expired(self, request, queryset):
        count = 0
        for reservation in queryset:
            if reservation.status == 'active':
                reservation.mark_as_expired()
                count += 1
        self.message_user(request, f"{count} reservation(s) marked as expired.")
    mark_as_expired.short_description = "Mark selected reservations as expired"
    
    def mark_as_cancelled(self, request, queryset):
        count = 0
        for reservation in queryset:
            if reservation.status == 'active':
                reservation.mark_as_cancelled()
                count += 1
        self.message_user(request, f"{count} reservation(s) marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected reservations as cancelled"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')


# Register Store model
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone_number', 'is_active', 'is_pickup_point', 'manager', 'created_at']
    search_fields = ['name', 'address', 'city', 'phone_number']
    list_filter = ['is_active', 'is_pickup_point', 'city', 'created_at']
    ordering = ['city', 'name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 20
    autocomplete_fields = ['manager']
    list_editable = ['is_active', 'is_pickup_point']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'city', 'manager')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'whatsapp_number', 'email')
        }),
        ('Location Coordinates', {
            'fields': ('latitude', 'longitude'),
            'description': 'Enter GPS coordinates for map display'
        }),
        ('Operating Hours', {
            'fields': ('opening_hours',)
        }),
        ('Settings', {
            'fields': ('is_active', 'is_pickup_point')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('manager')
