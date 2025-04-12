from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'seller', 'category', 'status', 'created_at', 'updated_at')
    search_fields = ('name', 'category', 'seller__username')
    list_filter = ('status', 'category')

admin.site.register(Product, ProductAdmin)
