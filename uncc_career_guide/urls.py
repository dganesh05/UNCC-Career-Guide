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
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('job-board/', job_board, name='job_board'),
    path('networking-hub/', networking_hub, name='networking_hub'),
    path('career-events/', career_events, name='career_events'),
    path('resources/', resources, name='resources'),
    path('mentorship-hub/', mentorship_hub, name='mentorship_hub'),
    path('onboarding-quiz/', uncc_onboarding_quiz, name='onboarding-quiz'),
    path('generate-resume/', resume_views.generate_resume, name='generate_resume'),
    path('login/', login, name='login'),
]
