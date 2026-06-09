from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'amount', 'frequency', 'renewal_date', 'status']
    list_filter = ['frequency', 'status']
