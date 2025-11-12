#!/usr/bin/env python
"""
Script to create sample categories and products for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'montclair_wardrobe.settings')
django.setup()

from django.contrib.auth.models import User
from home.models import Category, Product

# Get admin user
admin = User.objects.get(username='admin')

# Create categories
categories_data = [
    {'name': 'Jewerly', 'icon': 'fas fa-gem', 'description': 'Elegant jewelry pieces'},
    {'name': 'Kids', 'icon': 'fas fa-child', 'description': 'Fashion for children'},
    {'name': 'Ladies Wear', 'icon': 'fas fa-female', 'description': 'Women\'s fashion'},
    {'name': 'Men\'s Wear', 'icon': 'fas fa-male', 'description': 'Men\'s fashion'},
    {'name': 'Msimbi (Babies)', 'icon': 'fas fa-baby', 'description': 'Baby clothing'},
    {'name': 'Shoes', 'icon': 'fas fa-shoe-prints', 'description': 'Footwear collection'},
    {'name': 'Sports Wear', 'icon': 'fas fa-running', 'description': 'Athletic wear'},
    {'name': 'Watches', 'icon': 'fas fa-clock', 'description': 'Timepieces'},
]

print("Creating categories...")
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={
            'icon': cat_data['icon'],
            'description': cat_data['description'],
            'created_by': admin
        }
    )
    if created:
        print(f"✓ Created category: {category.name}")
    else:
        print(f"- Category already exists: {category.name}")

# Create sample products
print("\nCreating sample products...")
products_data = [
    {
        'name': 'Gold Necklace',
        'description': 'Beautiful 18k gold necklace with elegant design',
        'price': 450.00,
        'stock': 5,
        'category': 'Jewerly'
    },
    {
        'name': 'Kids T-Shirt',
        'description': 'Comfortable cotton t-shirt for kids',
        'price': 35.00,
        'stock': 20,
        'category': 'Kids'
    },
    {
        'name': 'Ladies Dress',
        'description': 'Elegant evening dress for special occasions',
        'price': 180.00,
        'stock': 8,
        'category': 'Ladies Wear'
    },
    {
        'name': 'Men\'s Suit',
        'description': 'Professional business suit',
        'price': 350.00,
        'stock': 6,
        'category': 'Men\'s Wear'
    },
    {
        'name': 'Baby Onesie',
        'description': 'Soft cotton onesie for babies',
        'price': 25.00,
        'stock': 15,
        'category': 'Msimbi (Babies)'
    },
    {
        'name': 'Running Shoes',
        'description': 'Comfortable running shoes with great support',
        'price': 120.00,
        'stock': 12,
        'category': 'Shoes'
    },
    {
        'name': 'Sports Jersey',
        'description': 'Breathable sports jersey',
        'price': 45.00,
        'stock': 25,
        'category': 'Sports Wear'
    },
    {
        'name': 'Luxury Watch',
        'description': 'Premium automatic watch',
        'price': 800.00,
        'stock': 3,
        'category': 'Watches'
    },
]

for prod_data in products_data:
    category = Category.objects.get(name=prod_data['category'])
    product, created = Product.objects.get_or_create(
        name=prod_data['name'],
        defaults={
            'description': prod_data['description'],
            'price': prod_data['price'],
            'stock': prod_data['stock'],
            'category': category,
            'seller': admin,
            'status': 'active',
            'approval_status': 'approved'
        }
    )
    if created:
        print(f"✓ Created product: {product.name}")
    else:
        print(f"- Product already exists: {product.name}")

print("\n✅ Sample data setup complete!")
print("\nYou can now login with:")
print("Username: admin")
print("Password: admin123")
