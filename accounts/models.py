"""
accounts/models.py — User Profile Model

Django's built-in User model already gives us:
  - username, email, password (hashed), first_name, last_name
  - is_active, is_staff, date_joined, last_login

We EXTEND it with a UserProfile model using a OneToOneField.
This is the recommended pattern — never modify the built-in User model.

Database Relationship:
  User (Django built-in) ←──── OneToOne ────→ UserProfile
  One user has exactly one profile. One profile belongs to exactly one user.
"""

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extended user information.
    Each field maps to a column in the database table.
    """
    # OneToOneField: creates a unique constraint + foreign key
    # on_delete=CASCADE: if the User is deleted, this profile is also deleted
    # related_name='profile': lets us do user.profile to access this from User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # TextField: variable-length text (no max length)
    bio = models.TextField(blank=True, null=True)

    # ImageField: stores file path in DB, actual file goes to MEDIA_ROOT/profile_pics/
    # blank=True, null=True: this field is optional
    avatar = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # CharField with choices: enforces only these values in the database
    CURRENCY_CHOICES = [
        ('INR', '₹ Indian Rupee'),
        ('USD', '$ US Dollar'),
        ('EUR', '€ Euro'),
        ('GBP', '£ British Pound'),
    ]
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')

    # DateTimeField: auto_now_add=True sets this ONCE when the record is created
    created_at = models.DateTimeField(auto_now_add=True)

    # DateTimeField: auto_now=True updates this EVERY time the record is saved
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation — shown in Django admin and shell"""
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
