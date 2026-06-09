"""
goals/models.py

A SavingsGoal represents something the user is saving towards.
Example: "Save ₹50,000 for a Laptop by December 2024"

The app tracks progress and projects a completion date.
"""

from django.db import models
from django.contrib.auth.models import User


class SavingsGoal(models.Model):
    """A financial goal with a target amount and deadline."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    target_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # current_amount: how much has been saved so far (manually updated by user)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    target_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    # Icon to represent the goal visually
    icon = models.CharField(max_length=50, default='bi-piggy-bank')
    color = models.CharField(max_length=7, default='#0d6efd')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def progress_percentage(self):
        """Calculate what % of the goal is complete. Property = computed on the fly, not stored."""
        if self.target_amount <= 0:
            return 0
        percentage = (self.current_amount / self.target_amount) * 100
        return min(round(float(percentage), 1), 100)  # Cap at 100%

    @property
    def remaining_amount(self):
        return max(self.target_amount - self.current_amount, 0)

    def __str__(self):
        return f"{self.name} - {self.progress_percentage}% complete"

    class Meta:
        ordering = ['-created_at']
