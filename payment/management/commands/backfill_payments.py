"""
Management command to create Payment records for existing Checkouts
that don't have associated Payment records.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from home.models import Checkout
from payment.models import Payment
import time


class Command(BaseCommand):
    help = 'Create Payment records for existing Checkouts without payments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating records',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No records will be created'))
        
        # Get all checkouts
        checkouts = Checkout.objects.all().select_related('user')
        total_checkouts = checkouts.count()
        
        self.stdout.write(f'Found {total_checkouts} total checkouts')
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for checkout in checkouts:
            try:
                # Check if payment already exists for this checkout
                transaction_id = checkout.transaction_id
                
                if transaction_id:
                    # Check if payment with this reference exists
                    if Payment.objects.filter(reference=transaction_id).exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'Skipping checkout {checkout.id} - Payment already exists'
                            )
                        )
                        skipped_count += 1
                        continue
                
                # Generate transaction reference if not exists
                if not transaction_id:
                    transaction_id = f"{checkout.payment_method.upper()}_{checkout.user.id}_{int(time.time())}_{checkout.id}"
                
                # Calculate total amount (sum of orders + delivery fee)
                orders = checkout.orders.all()
                order_total = sum(order.total_price for order in orders)
                total_amount = order_total + checkout.delivery_fee
                
                if not dry_run:
                    with transaction.atomic():
                        # Create payment record
                        payment = Payment.objects.create(
                            user=checkout.user,
                            method=checkout.payment_method,
                            amount=total_amount,
                            reference=transaction_id,
                            status=checkout.payment_status if checkout.payment_status else 'pending',
                            phone_number=checkout.phone_number,
                            location=checkout.location,
                            gps_location=checkout.gps_location,
                            room_number=checkout.room_number,
                            created_at=checkout.created_at,
                            updated_at=checkout.updated_at
                        )
                        
                        # Update checkout with transaction_id if it didn't have one
                        if not checkout.transaction_id:
                            checkout.transaction_id = transaction_id
                            checkout.save(update_fields=['transaction_id'])
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Created payment {payment.id} for checkout {checkout.id} '
                                f'(User: {checkout.user.username}, Amount: ZMW {total_amount})'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'[DRY RUN] Would create payment for checkout {checkout.id} '
                            f'(User: {checkout.user.username}, Amount: ZMW {total_amount}, '
                            f'Method: {checkout.payment_method})'
                        )
                    )
                
                created_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing checkout {checkout.id}: {str(e)}'
                    )
                )
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('SUMMARY:'))
        self.stdout.write(f'Total checkouts: {total_checkouts}')
        self.stdout.write(self.style.SUCCESS(f'Payments created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Skipped (already exists): {skipped_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        
        if dry_run:
            self.stdout.write('\n' + self.style.WARNING('This was a DRY RUN - no records were created'))
            self.stdout.write('Run without --dry-run to actually create the payment records')
