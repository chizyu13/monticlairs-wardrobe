import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from home.models import Category


class Command(BaseCommand):
    help = 'Sync categories from static/images folder structure'

    def handle(self, *args, **options):
        static_images_path = os.path.join(settings.BASE_DIR, 'static', 'images')
        
        if not os.path.exists(static_images_path):
            self.stdout.write(
                self.style.ERROR(f'Static images path does not exist: {static_images_path}')
            )
            return

        # Get or create a system user for category creation
        system_user, created = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@montclairwardrobe.com',
                'first_name': 'System',
                'last_name': 'User',
                'is_active': False
            }
        )

        categories_created = 0
        categories_updated = 0

        for item in os.listdir(static_images_path):
            item_path = os.path.join(static_images_path, item)
            if os.path.isdir(item_path):
                category_name = item
                
                # Check if category already exists
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'description': f'Products in the {category_name} category',
                        'created_by': system_user
                    }
                )
                
                if created:
                    categories_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created category: {category_name}')
                    )
                else:
                    categories_updated += 1
                    self.stdout.write(
                        self.style.WARNING(f'Category already exists: {category_name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Sync complete! Created: {categories_created}, '
                f'Already existed: {categories_updated}'
            )
        )