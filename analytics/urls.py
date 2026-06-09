from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forecast/', views.forecast_view, name='forecast'),
    path('what-if/', views.what_if_view, name='what_if'),
    path('health-score/', views.health_score_view, name='health_score'),
]
