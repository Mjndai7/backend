from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a Profile instance for the User when a new User is created or the User is saved.

    Parameters:
        sender: The model class that sent the signal (User in this case).
        instance: The User instance that was just created or saved.
        created: A boolean indicating if the User was just created.

    Returns:
        None
    """
    if created or not hasattr(instance, 'profile'):
        Profile.objects.get_or_create(owner=instance)
    else:
        instance.profile.save()

@receiver(post_save, sender=User)
def save_user_profile_and_seo(sender, instance, **kwargs):
    """
    Signal handler to save the Profile instance for the User when the User is saved.

    Parameters:
        sender: The model class that sent the signal (User in this case).
        instance: The User instance that was just saved.

    Returns:
        None
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
