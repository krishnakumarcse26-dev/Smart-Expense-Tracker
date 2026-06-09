"""
subscriptions/models.py

Tracks recurring payments like Netflix, Spotify, etc.
The app alerts users about upcoming renewals.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Subscription(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='monthly')

    # Next renewal date
    renewal_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    notes = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='bi-credit-card')
    color = models.CharField(max_length=7, default='#6f42c1')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def days_until_renewal(self):
        """How many days until the next renewal?"""
        today = timezone.now().date()
        delta = self.renewal_date - today
        return delta.days

    @property
    def monthly_cost(self):
        """Normalize cost to monthly for comparison."""
        multipliers = {
            'daily': 30,
            'weekly': 4.33,
            'monthly': 1,
            'quarterly': 1/3,
            'yearly': 1/12,
        }
        return round(float(self.amount) * multipliers.get(self.frequency, 1), 2)

    def __str__(self):
        return f"{self.name} - ₹{self.amount}/{self.frequency}"

    class Meta:
        ordering = ['renewal_date']
