from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import Profile

class Command(BaseCommand):
    help = 'Fix duplicate profile issues by ensuring each user has exactly one profile'

    def handle(self, *args, **options):
        self.stdout.write('Fixing duplicate profiles...')
        
        # Get all users
        users = User.objects.all()
        fixed = 0
        created = 0
        
        for user in users:
            try:
                # Try to get the profile
                profile = Profile.objects.filter(user=user).first()
                
                if profile:
                    # Delete any duplicate profiles for this user
                    duplicates = Profile.objects.filter(user=user).exclude(id=profile.id)
                    if duplicates.exists():
                        count = duplicates.count()
                        duplicates.delete()
                        self.stdout.write(f'Deleted {count} duplicate profile(s) for user: {user.username}')
                        fixed += count
                else:
                    # Create profile if it doesn't exist
                    Profile.objects.create(user=user)
                    self.stdout.write(f'Created profile for user: {user.username}')
                    created += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing user {user.username}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nFixed {fixed} duplicate profiles'))
        self.stdout.write(self.style.SUCCESS(f'Created {created} missing profiles'))
        self.stdout.write(self.style.SUCCESS('Done!'))
