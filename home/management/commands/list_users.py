from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import Profile


class Command(BaseCommand):
    help = 'List all registered users in the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed user information',
        )
        parser.add_argument(
            '--staff-only',
            action='store_true',
            help='Show only staff users',
        )
        parser.add_argument(
            '--customers-only',
            action='store_true',
            help='Show only customer users',
        )

    def handle(self, *args, **options):
        # Filter users based on options
        users = User.objects.all()
        
        if options['staff_only']:
            users = users.filter(is_staff=True)
            self.stdout.write(self.style.SUCCESS('\n=== STAFF USERS ===\n'))
        elif options['customers_only']:
            users = users.filter(is_staff=False, is_superuser=False)
            self.stdout.write(self.style.SUCCESS('\n=== CUSTOMER USERS ===\n'))
        else:
            self.stdout.write(self.style.SUCCESS('\n=== ALL USERS ===\n'))
        
        # Display summary
        total = users.count()
        active = users.filter(is_active=True).count()
        
        self.stdout.write(f"Total: {total} users")
        self.stdout.write(f"Active: {active} users\n")
        
        # Display user list
        if options['detailed']:
            for user in users:
                self.stdout.write(self.style.WARNING(f"\n{'='*60}"))
                self.stdout.write(f"ID: {user.id}")
                self.stdout.write(f"Username: {user.username}")
                self.stdout.write(f"Email: {user.email}")
                self.stdout.write(f"Name: {user.first_name} {user.last_name}")
                self.stdout.write(f"Staff: {'Yes' if user.is_staff else 'No'}")
                self.stdout.write(f"Superuser: {'Yes' if user.is_superuser else 'No'}")
                self.stdout.write(f"Active: {'Yes' if user.is_active else 'No'}")
                self.stdout.write(f"Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
                
                # Profile info
                try:
                    profile = user.profile
                    self.stdout.write(f"Phone: {profile.phone_number or 'Not set'}")
                    self.stdout.write(f"Location: {profile.location or 'Not set'}")
                    if profile.bio:
                        bio_preview = profile.bio[:50] + '...' if len(profile.bio) > 50 else profile.bio
                        self.stdout.write(f"Bio: {bio_preview}")
                except Profile.DoesNotExist:
                    self.stdout.write(self.style.ERROR("Profile: Not found"))
        else:
            # Simple list
            self.stdout.write(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Staff':<8} {'Active':<8} {'Joined'}")
            self.stdout.write('-' * 90)
            
            for user in users:
                staff = '✓' if user.is_staff else '✗'
                active = '✓' if user.is_active else '✗'
                joined = user.date_joined.strftime('%Y-%m-%d')
                
                self.stdout.write(
                    f"{user.id:<5} {user.username:<20} {user.email:<30} "
                    f"{staff:<8} {active:<8} {joined}"
                )
        
        self.stdout.write(self.style.SUCCESS(f"\n\nTotal users displayed: {total}"))
