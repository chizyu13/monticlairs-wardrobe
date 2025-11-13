from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        # Only create profile if it doesn't exist
        Profile.objects.get_or_create(user=instance)
    else:
        # Only save if profile exists
        if hasattr(instance, 'profile'):
            instance.profile.save()
