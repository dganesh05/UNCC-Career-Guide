from django.urls import path
from .views import home  # Import the home view from views.py

urlpatterns = [
    path('', home, name='home'),
]