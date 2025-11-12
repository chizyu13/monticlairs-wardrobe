from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from getpass import getpass


class Command(BaseCommand):
    help = 'Reset password for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument(
            '--password',
            type=str,
            help='New password (if not provided, will prompt)',
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            return
        
        # Get password
        if options['password']:
            new_password = options['password']
        else:
            new_password = getpass('Enter new password: ')
            confirm_password = getpass('Confirm password: ')
            
            if new_password != confirm_password:
                self.stdout.write(self.style.ERROR('Passwords do not match!'))
                return
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Password successfully reset for user: {username}'))
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Staff: {"Yes" if user.is_staff else "No"}')
