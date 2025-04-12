from django.contrib import admin
from .models import Cart
from home.models import Product  # Import Product for autocomplete

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at', 'get_total_price')
    search_fields = ('user__username', 'product__name')
    list_filter = ('added_at', 'user', 'product')
    ordering = ('-added_at',)
    list_per_page = 20
    date_hierarchy = 'added_at'
    autocomplete_fields = ['user', 'product']  # Autocomplete for user and product
    readonly_fields = ('added_at',)
    list_editable = ('quantity',)  # Allow inline editing of quantity
    actions = ['clear_selected_carts', 'increase_quantity', 'decrease_quantity']

    def get_total_price(self, obj):
        return f"ZMW {obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'

    def clear_selected_carts(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} cart item(s) cleared successfully.")
    clear_selected_carts.short_description = "Clear selected cart items"

    def increase_quantity(self, request, queryset):
        updated = 0
        for cart_item in queryset:
            if cart_item.product.is_in_stock() and cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
                updated += 1
        self.message_user(request, f"Quantity increased for {updated} cart item(s).")
    increase_quantity.short_description = "Increase quantity by 1"

    def decrease_quantity(self, request, queryset):
        updated = 0
        for cart_item in queryset:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                updated += 1
            elif cart_item.quantity == 1:
                cart_item.delete()
                updated += 1
        self.message_user(request, f"Quantity decreased or removed for {updated} cart item(s).")
    decrease_quantity.short_description = "Decrease quantity by 1 or remove if 1"

    def get_queryset(self, request):
        # Optimize with select_related for user and product
        return super().get_queryset(request).select_related('user', 'product')