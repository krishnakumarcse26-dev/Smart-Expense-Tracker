"""
smartexpense/urls.py — The Master URL Router

Django reads this file first when ANY request comes in.
It then delegates to each app's own urls.py.

Think of this as a phone switchboard:
- Request comes in → check which "extension" (URL pattern) matches → route to correct app.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import landing_page

urlpatterns = [
    # Django admin panel — powerful built-in management interface
    path('admin/', admin.site.urls),

    # Landing page — handled by accounts app (index view)
    path('', landing_page, name='landing'),

    # Authentication routes: /accounts/login/, /accounts/register/, etc.
    path('accounts/', include('accounts.urls')),

    # Django's built-in auth URLs for password reset flow
    # Provides: password_reset, password_reset_done, password_reset_confirm, password_reset_complete
    path('accounts/', include('django.contrib.auth.urls')),

    # Transactions: /transactions/
    path('transactions/', include('transactions.urls')),

    # Budgets: /budgets/
    path('budgets/', include('budgets.urls')),

    # Savings Goals: /goals/
    path('goals/', include('goals.urls')),

    # Subscriptions: /subscriptions/
    path('subscriptions/', include('subscriptions.urls')),

    # Analytics & Dashboard: /analytics/
    path('analytics/', include('analytics.urls')),

    # Reports & Exports: /reports/
    path('reports/', include('reports.urls')),
]

# In development, serve media files (uploaded images etc.) via Django itself.
# In production, your web server (Nginx/Render) handles this.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
