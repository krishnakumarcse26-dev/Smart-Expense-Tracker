"""
transactions/models.py — The Core Financial Data Model

This is the heart of the application.
Every rupee that flows in or out is stored here.

ER Relationship:
  User ──── (has many) ──── Transaction
  User ──── (has many) ──── Category

Data Isolation: Every query MUST filter by user=request.user
This ensures User A NEVER sees User B's data.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """
    Expense/Income categories (e.g., Food, Transport, Salary).
    Each user has their own categories — true data isolation.
    """
    # ForeignKey: many categories belong to one user
    # on_delete=CASCADE: deleting user deletes all their categories
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    name = models.CharField(max_length=100)

    # Icon class from Bootstrap Icons (e.g., 'bi-cart', 'bi-house')
    icon = models.CharField(max_length=50, default='bi-tag')

    # Hex color code for chart visualization (e.g., '#FF6384')
    color = models.CharField(max_length=7, default='#6c757d')

    CATEGORY_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('both', 'Both'),
    ]
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES, default='both')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    class Meta:
        verbose_name_plural = "Categories"
        # Each user can only have one category with a given name
        unique_together = ['user', 'name']
        ordering = ['name']


class Transaction(models.Model):
    """
    A single financial transaction — income or expense.

    Index strategy:
    - user + date: most queries filter by user and date range
    - user + transaction_type: for income/expense totals
    These indexes make queries 10-100x faster on large datasets.
    """
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    # Link to the user who owns this transaction
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')

    # ForeignKey to Category with SET_NULL: deleting a category doesn't delete transactions
    # null=True, blank=True: transaction can exist without a category
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transactions'
    )

    title = models.CharField(max_length=200)

    # DecimalField: exact decimal arithmetic (important for money!)
    # NEVER use FloatField for money — floating point errors cause bugs
    # max_digits=12: up to 999,999,999.99
    # decimal_places=2: two decimal places (paise)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)

    # DateField: just the date (no time) — when did this transaction occur?
    date = models.DateField(default=timezone.now)

    notes = models.TextField(blank=True, null=True)

    # When was this record created in our system?
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.transaction_type})"

    class Meta:
        # Default ordering: newest first
        ordering = ['-date', '-created_at']

        # Database indexes for performance
        # Without indexes, Django does a full table scan on every query.
        # With indexes, it jumps directly to relevant rows.
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['user', 'category']),
        ]
