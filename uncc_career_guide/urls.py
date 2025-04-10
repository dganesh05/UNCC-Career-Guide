from django.contrib import admin
from django.urls import path
from base import views
from base.views import (
    dashboard,  # Import the dashboard function directly 
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
from base.views import mentor_list

# Remove or comment out this function since we want to use the one from views.py
# def uncc_dashboard(request):
#     return render(request, 'uncc-dashboard.html')

# Other view functions can remain if they're still needed
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
    # Use the dashboard function from base/views.py instead of uncc_dashboard
    path('dashboard/', dashboard, name='dashboard'),  # Changed from uncc_dashboard to dashboard
    path('job-board/', uncc_job_board, name='job_board'),
    path('networking-hub/', uncc_networking_hub, name='networking_hub'),
    path('career-events/', uncc_career_events, name='career_events'),
    path('resources/', uncc_resources, name='resources'),
    path('mentorship-hub/', mentorship_hub, name='mentorship_hub'),
    path('onboarding-quiz/', uncc_onboarding_quiz, name='onboarding_quiz'),
    path('generate-resume/', resume_views.generate_resume, name='generate_resume'),
    path('login/', login, name='login'),
    path('mentors/', views.mentor_list, name='mentors'),
]