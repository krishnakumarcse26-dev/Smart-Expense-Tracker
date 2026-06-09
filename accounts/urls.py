"""
accounts/urls.py — URL patterns for authentication

Each path() maps a URL to a view function.
path('login/', login_view, name='login')
  → URL: /accounts/login/
  → Calls: login_view(request)
  → Name: use {% url 'login' %} in templates to generate the URL
     (avoids hardcoding URLs — if URL changes, templates auto-update)
"""

from django.urls import path
from . import views

urlpatterns = [
    
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
