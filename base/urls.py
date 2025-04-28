from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('resource-dashboard/', views.resource_dashboard, name='resource_dashboard'),
    path('career-confidence-boost/', views.career_confidence_boost, name='career_confidence_boost'),
    path('visualize-trajectory/', views.visualize_trajectory, name='visualize_trajectory'),
]
