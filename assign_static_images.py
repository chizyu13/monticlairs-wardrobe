#!/usr/bin/env python
"""
Script to assign static images from static/images folders to products
"""
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'montclair_wardrobe.settings')
django.setup()

from home.models import Product, Category

# Mapping of category names to their image folders
category_image_mapping = {
    'Jewerly': 'images/Jewerly',
    'Kids': 'images/Kids',
    'Ladies Wear': 'images/Ladies-Wear',
    'Men\'s Wear': 'images/Mens-Wear',
    'Msimbi (Babies)': 'images/Baby-Wear',
    'Shoes': 'images/Shoes',
    'Sports Wear': 'images/Sports-Wear',
    'Watches': 'images/Watches',
}

# Get available images for each category
category_images = {}
for category_name, folder_path in category_image_mapping.items():
    full_path = os.path.join('static', folder_path)
    if os.path.exists(full_path):
        images = [f for f in os.listdir(full_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        category_images[category_name] = [f"{folder_path}/{img}" for img in images]
        print(f"Found {len(images)} images for {category_name}")
    else:
        print(f"Warning: Folder not found for {category_name}: {full_path}")
        category_images[category_name] = []

print("\n" + "="*60)
print("Assigning images to products...")
print("="*60 + "\n")

# Assign images to products
updated_count = 0
for product in Product.objects.all():
    if product.category and product.category.name in category_images:
        available_images = category_images[product.category.name]
        if available_images:
            # Assign a random image from the category
            product.static_image = random.choice(available_images)
            product.save()
            print(f"✓ {product.name} → {product.static_image}")
            updated_count += 1
        else:
            print(f"⚠ No images available for {product.name} ({product.category.name})")
    else:
        print(f"⚠ {product.name} has no category or category not mapped")

print("\n" + "="*60)
print(f"✅ Updated {updated_count} products with static images!")
print("="*60)
print("\nYou can now:")
print("1. Run: python manage.py runserver")
print("2. Visit your homepage to see the images")
print("3. Change images in admin panel by editing the 'Static Image Path' field")
