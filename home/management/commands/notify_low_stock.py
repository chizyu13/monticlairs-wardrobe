"""
Management command to send low stock notifications to sellers.
Run with: python manage.py notify_low_stock
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from home.models import Product
from collections import defaultdict


class Command(BaseCommand):
    help = 'Send low stock notifications to product sellers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold',
            type=int,
            default=5,
            help='Stock threshold for low stock warning (default: 5)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails'
        )

    def handle(self, *args, **options):
        threshold = options['threshold']
        dry_run = options['dry_run']

        self.stdout.write(f'Checking for products with stock <= {threshold}...')

        # Get all active products with low stock
        low_stock_products = Product.objects.filter(
            Q(stock__gt=0) & Q(stock__lte=threshold),
            status='active',
            approval_status='approved'
        ).select_related('seller', 'category')

        if not low_stock_products.exists():
            self.stdout.write(self.style.SUCCESS('No low stock products found.'))
            return

        # Group products by seller
        seller_products = defaultdict(list)
        for product in low_stock_products:
            seller_products[product.seller].append(product)

        # Send notifications to each seller
        emails_sent = 0
        for seller, products in seller_products.items():
            if not seller.email:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping {seller.username} - no email address'
                    )
                )
                continue

            # Prepare email content
            subject = f'Low Stock Alert - {len(products)} Product(s) Running Low'
            
            product_list = '\n'.join([
                f'  - {p.name}: {p.stock} unit(s) remaining'
                for p in products
            ])
            
            message = f"""
Hello {seller.get_full_name() or seller.username},

This is an automated notification to inform you that the following products in your inventory are running low on stock:

{product_list}

Please restock these items to avoid running out of inventory.

You can manage your products at: {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'your-site.com'}/products/

Best regards,
Montclair Wardrobe Team
            """.strip()

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'\n[DRY RUN] Would send email to {seller.email}:'
                    )
                )
                self.stdout.write(f'Subject: {subject}')
                self.stdout.write(f'Message:\n{message}\n')
            else:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[seller.email],
                        fail_silently=False,
                    )
                    emails_sent += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Sent notification to {seller.email} for {len(products)} product(s)'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Failed to send email to {seller.email}: {str(e)}'
                        )
                    )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[DRY RUN] Would have sent {len(seller_products)} email(s)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully sent {emails_sent} notification email(s)'
                )
            )
