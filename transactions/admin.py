from django.contrib import admin
from .models import Transaction, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category_type', 'color']
    list_filter = ['category_type']
    search_fields = ['name', 'user__username']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'transaction_type', 'category', 'date']
    list_filter = ['transaction_type', 'date']
    search_fields = ['title', 'user__username']
    date_hierarchy = 'date'
