"""
Management command to clean up expired stock reservations.
Run with: python manage.py cleanup_reservations
Can be scheduled to run periodically (e.g., every 5 minutes via cron)
"""

from django.core.management.base import BaseCommand
from home.models import StockReservation


class Command(BaseCommand):
    help = 'Clean up expired stock reservations'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up expired stock reservations...')
        
        expired_count = StockReservation.cleanup_expired_reservations()
        
        if expired_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked {expired_count} reservation(s) as expired'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No expired reservations found')
            )
