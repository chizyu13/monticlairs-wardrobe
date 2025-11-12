from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import Category
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Synchronize categories with folder structure'

    def handle(self, *args, **options):
        # Get or create admin user for category creation
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please create a superuser first.'))
            return

        static_images_path = os.path.join(settings.BASE_DIR, 'static', 'images')
        
        if not os.path.exists(static_images_path):
            self.stdout.write(self.style.ERROR(f'Static images path does not exist: {static_images_path}'))
            return

        # Mapping of folder names to proper category names
        folder_to_category = {
            'Watches': 'Watches',
            'Jewerly': 'Jewelry',  # Note: folder has typo, but we'll use correct name
            'Kids': 'Kids',
            'Ladies-Wear': 'Ladies Wear',
            'Mens-Wear': 'Men\'s Wear',
            'Baby-Wear': 'Msimbi (Babies)',
            'Shoes': 'Shoes',
            'Sports-Wear': 'Sports Wear',
        }

        created_count = 0
        updated_count = 0

        for item in os.listdir(static_images_path):
            item_path = os.path.join(static_images_path, item)
            if os.path.isdir(item_path):
                # Get the proper category name
                category_name = folder_to_category.get(item, item)
                
                # Create or get category
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'description': f'Products in the {category_name} category',
                        'created_by': admin_user
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created category: {category_name}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Category already exists: {category_name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Sync complete! Created: {created_count}, Existing: {updated_count}'
            )
        )
        
        # List all categories
        self.stdout.write('\nAll categories:')
        for cat in Category.objects.all():
            self.stdout.write(f'  - {cat.name} (ID: {cat.id})')