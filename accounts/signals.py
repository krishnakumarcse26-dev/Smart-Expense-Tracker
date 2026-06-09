"""
accounts/signals.py — Django Signals

Signals are Django's event system.
"When X happens, automatically do Y."

Here we use post_save on the User model:
  → Whenever a User is saved, check if it's new.
  → If new, automatically create a UserProfile for them.

Why signals instead of doing this in the view?
  Because signals work no matter HOW the user is created —
  via registration form, admin panel, management commands, tests, etc.
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    sender: the model class that sent the signal (User)
    instance: the actual User object that was saved
    created: True if this is a NEW user, False if existing user was updated
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile is saved whenever user is saved."""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
