"""
accounts/admin.py — Register models with Django Admin

Django Admin (/admin/) gives you a full management UI for free.
Register your models here to manage them through the admin panel.
Accessible at: http://127.0.0.1:8000/admin/
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Show profile fields inline on the User admin page."""
    model = UserProfile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    """Extend the default UserAdmin with the UserProfile inline."""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']


# Unregister the default User admin, then register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.site_header = "SmartExpense Admin"
admin.site.site_title = "SmartExpense"
admin.site.index_title = "Financial Platform Administration"
