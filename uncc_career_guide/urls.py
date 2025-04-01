from django.contrib import admin
from django.urls import path
from base.views import (
    dashboard, 
    job_board, 
    networking_hub, 
    career_events, 
    resources, 
    mentorship_hub,
    login,
    home
)
from django.shortcuts import render
from resume_generator import views as resume_views

def uncc_dashboard(request):
    return render(request, 'uncc-dashboard.html')

def uncc_career_events(request):
    return render(request, 'uncc-career-events.html')

def uncc_job_board(request):
    return render(request, 'uncc-job-board.html')

def uncc_login_page(request):
    return render(request, 'uncc-login-page.html')

def uncc_mentorship_hub(request):
    return render(request, 'uncc-mentorship-hub.html')

def uncc_networking_hub(request):
    return render(request, 'uncc-networking-hub.html')

def uncc_onboarding_quiz(request):
    return render(request, 'uncc-onboarding-quiz.html')

def uncc_resources(request):
    return render(request, 'uncc-resources.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', uncc_dashboard, name='home'),
    path('career-events/', uncc_career_events, name='career-events'),
    path('dashboard/', uncc_dashboard, name='dashboard'),
    path('job-board/', uncc_job_board, name='job-board'),
    path('login/', uncc_login_page, name='login'),
    path('mentorship-hub/', uncc_mentorship_hub, name='mentorship-hub'),
    path('networking-hub/', uncc_networking_hub, name='networking-hub'),
    path('onboarding-quiz/', uncc_onboarding_quiz, name='onboarding-quiz'),
    path('resources/', uncc_resources, name='resources'),
    path('generate-resume/', resume_views.generate_resume, name='generate_resume'),
]

