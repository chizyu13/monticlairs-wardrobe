import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Manage category images - copy, organize, and set up category photos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['list', 'copy', 'setup'],
            default='list',
            help='Action to perform: list (show current images), copy (copy image to category), setup (create sample images)'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Category name (e.g., "Jewelry", "Kids")'
        )
        parser.add_argument(
            '--image',
            type=str,
            help='Source image filename in static/images/'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='category',
            help='Name for the category image (default: category)'
        )

    def handle(self, *args, **options):
        static_images_path = os.path.join(settings.BASE_DIR, 'static', 'images')
        
        if options['action'] == 'list':
            self.list_categories(static_images_path)
        elif options['action'] == 'copy':
            self.copy_image(static_images_path, options)
        elif options['action'] == 'setup':
            self.setup_sample_images(static_images_path)

    def list_categories(self, static_images_path):
        """List all categories and their current images"""
        self.stdout.write(self.style.SUCCESS('Category Status:'))
        self.stdout.write('-' * 50)
        
        for item in os.listdir(static_images_path):
            item_path = os.path.join(static_images_path, item)
            if os.path.isdir(item_path) and item != 'defaults':
                images = []
                try:
                    files = os.listdir(item_path)
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            images.append(file)
                except OSError:
                    pass
                
                status = f"✅ {len(images)} images" if images else "❌ No images"
                self.stdout.write(f"{item:20} {status}")
                if images:
                    for img in images[:3]:  # Show first 3 images
                        self.stdout.write(f"{'':22} - {img}")
                    if len(images) > 3:
                        self.stdout.write(f"{'':22} ... and {len(images) - 3} more")

    def copy_image(self, static_images_path, options):
        """Copy an image from static/images to a category folder"""
        if not options['category'] or not options['image']:
            self.stdout.write(
                self.style.ERROR('Both --category and --image are required for copy action')
            )
            return

        source_path = os.path.join(static_images_path, options['image'])
        category_path = os.path.join(static_images_path, options['category'])
        
        if not os.path.exists(source_path):
            self.stdout.write(
                self.style.ERROR(f'Source image not found: {options["image"]}')
            )
            return

        if not os.path.exists(category_path):
            self.stdout.write(
                self.style.ERROR(f'Category folder not found: {options["category"]}')
            )
            return

        # Get file extension
        _, ext = os.path.splitext(options['image'])
        dest_filename = f"{options['name']}{ext}"
        dest_path = os.path.join(category_path, dest_filename)

        try:
            shutil.copy2(source_path, dest_path)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Copied {options["image"]} to {options["category"]}/{dest_filename}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to copy image: {e}')
            )

    def setup_sample_images(self, static_images_path):
        """Set up sample category images using existing images"""
        self.stdout.write(self.style.SUCCESS('Setting up sample category images...'))
        
        # Get available images from the main static/images folder
        available_images = []
        for file in os.listdir(static_images_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                available_images.append(file)
        
        if not available_images:
            self.stdout.write(
                self.style.WARNING('No images found in static/images/ to use as samples')
            )
            return

        # Category mappings - you can customize these
        category_mappings = {
            'Jewerly': 'jewelry',
            'Kids': 'kids', 
            'Ladies Wear': 'ladies',
            "Men's Wear": 'mens',
            'Msimbi (Babies)': 'babies',
            'Shoes': 'shoes',
            'Sports Wear': 'sports',
            'Watches': 'watches'
        }

        for category, keyword in category_mappings.items():
            category_path = os.path.join(static_images_path, category)
            if os.path.exists(category_path):
                # Check if category already has images
                existing_images = [f for f in os.listdir(category_path) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                
                if existing_images:
                    self.stdout.write(f"⏭️  {category} already has images, skipping")
                    continue

                # Find a suitable image (you can improve this logic)
                suitable_image = None
                for img in available_images:
                    if keyword.lower() in img.lower():
                        suitable_image = img
                        break
                
                # If no keyword match, use the first available image
                if not suitable_image and available_images:
                    suitable_image = available_images[0]
                
                if suitable_image:
                    source_path = os.path.join(static_images_path, suitable_image)
                    _, ext = os.path.splitext(suitable_image)
                    dest_path = os.path.join(category_path, f"category{ext}")
                    
                    try:
                        shutil.copy2(source_path, dest_path)
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Added sample image to {category}")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Failed to add image to {category}: {e}")
                        )

        self.stdout.write(self.style.SUCCESS('\n🎉 Sample setup complete!'))
        self.stdout.write('You can now:')
        self.stdout.write('1. Replace sample images with better category photos')
        self.stdout.write('2. Use --action copy to add specific images to categories')
        self.stdout.write('3. Add multiple images to each category folder')