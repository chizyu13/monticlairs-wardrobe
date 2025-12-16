from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from staff_dashboard.models import StaffApproval


class Command(BaseCommand):
    help = 'Create StaffApproval records for existing staff users'

    def handle(self, *args, **options):
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        created_count = 0
        existing_count = 0

        for user in staff_users:
            approval, created = StaffApproval.objects.get_or_create(
                user=user,
                defaults={'is_approved': False}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created StaffApproval for {user.username}')
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'StaffApproval already exists for {user.username}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: Created {created_count} new approvals, '
                f'{existing_count} already existed'
            )
        )
