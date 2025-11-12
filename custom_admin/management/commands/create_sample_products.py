from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import Category, Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample products for testing category filtering'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please create a superuser first.'))
            return

        # Sample products data
        sample_products = [
            {
                'name': 'Luxury Gold Watch',
                'description': 'Premium gold-plated watch with leather strap',
                'price': Decimal('299.99'),
                'category': 'Watches',
                'stock': 5
            },
            {
                'name': 'Sport Digital Watch',
                'description': 'Water-resistant digital watch perfect for sports',
                'price': Decimal('89.99'),
                'category': 'Watches',
                'stock': 10
            },
            {
                'name': 'Classic Analog Watch',
                'description': 'Timeless analog watch with stainless steel band',
                'price': Decimal('159.99'),
                'category': 'Watches',
                'stock': 8
            },
            {
                'name': 'Diamond Necklace',
                'description': 'Beautiful diamond necklace for special occasions',
                'price': Decimal('499.99'),
                'category': 'Jewelry',
                'stock': 3
            },
            {
                'name': 'Running Shoes',
                'description': 'Comfortable running shoes for daily exercise',
                'price': Decimal('79.99'),
                'category': 'Shoes',
                'stock': 15
            },
            {
                'name': 'Kids T-Shirt',
                'description': 'Colorful cotton t-shirt for children',
                'price': Decimal('19.99'),
                'category': 'Kids',
                'stock': 20
            }
        ]

        created_count = 0

        for product_data in sample_products:
            try:
                # Get the category
                category = Category.objects.get(name=product_data['category'])
                
                # Check if product already exists
                if not Product.objects.filter(name=product_data['name']).exists():
                    product = Product.objects.create(
                        name=product_data['name'],
                        description=product_data['description'],
                        price=product_data['price'],
                        category=category,
                        stock=product_data['stock'],
                        seller=admin_user,
                        status='active',
                        approval_status='approved'
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created product: {product.name} in {category.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Product already exists: {product_data["name"]}')
                    )
                    
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Category not found: {product_data["category"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} sample products!')
        )
        
        # Show products by category
        self.stdout.write('\nProducts by category:')
        for category in Category.objects.all():
            products = Product.objects.filter(category=category, status='active', approval_status='approved')
            self.stdout.write(f'  {category.name}: {products.count()} products')
            for product in products:
                self.stdout.write(f'    - {product.name} (ZMW {product.price})')