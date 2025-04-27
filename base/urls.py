from django.urls import path
from . import views

urlpatterns = [
    path ('dashboard/', views.resource_dashboard, name='resource_dashboard'),
    path ('career/', views.career_confidence_boost, name='career_confidence_boost'),
    path('career_trajectory/', views.visualize_trajectory, name='career_trajectory'),
]