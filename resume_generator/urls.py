from django.urls import path
from . import views

app_name = 'resume_generator'

urlpatterns = [
    path('', views.generate_resume, name='generate_resume'),
]