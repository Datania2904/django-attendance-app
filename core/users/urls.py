from django.urls import path
from .views import employee_dashboard,teams_view

urlpatterns = [
    path('dashboard/', employee_dashboard, name='employee_dashboard'),
    path('teams/', teams_view, name='teams'),
]