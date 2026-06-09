"""
budgets/models.py

A Budget is a spending limit for a specific category in a specific month.
Example: "I want to spend max ₹5000 on Food in June 2024"

The system then tracks actual spending vs. the budget and alerts the user.
"""

from django.db import models
from django.contrib.auth.models import User
from transactions.models import Category


class Budget(models.Model):
    """Monthly budget per category."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')

    # Budget amount for the month
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Which month/year does this budget apply to?
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()   # e.g., 2024

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.month}/{self.year}: ₹{self.amount}"

    class Meta:
        # A user can only have ONE budget per category per month
        unique_together = ['user', 'category', 'month', 'year']
        ordering = ['-year', '-month']
