from django.urls import path
from . import views
urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/excel/', views.export_excel, name='export_excel'),
]
