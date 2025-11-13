from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        # Only create profile if it doesn't exist
        # Use get_or_create to prevent duplicates
        try:
            Profile.objects.get_or_create(user=instance)
        except Exception as e:
            # Log error but don't crash
            print(f"Profile creation error in signal: {e}")
    else:
        # Only save if profile exists
        try:
            if hasattr(instance, 'profile'):
                instance.profile.save()
        except Exception as e:
            print(f"Profile save error in signal: {e}")
