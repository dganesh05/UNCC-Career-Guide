from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from base import views
from base.views import (
    dashboard,  # Import the dashboard function directly 
    job_board, 
    networking_hub, 
    career_events,  # Changed from events to career_events
    resources, 
    mentorship_hub,
    login,
    home,
    chat_view  # Added chat_view import
)
from django.shortcuts import render
from resume_generator import views as resume_views
from base.views import mentor_list
from django.conf import settings
from django.conf.urls.static import static

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
    path('jobs/', job_board, name='jobs'),
    path('dashboard/', dashboard, name='dashboard'),
    path('networking/', networking_hub, name='networking_hub'),
    path('events/', career_events, name='events'),  # Changed from events to career_events
    path('resources/', resources, name='resources'),
    path('mentorship/', mentorship_hub, name='mentorship_hub'),  # Changed from 'mentorship' to 'mentorship_hub'
    path('login/', login, name='login'),
    path('mentors/', mentor_list, name='mentors'),  # Changed from 'mentor-list' to 'mentors'
    path('onboarding-quiz/', uncc_onboarding_quiz, name='onboarding_quiz'),
    path('generate-resume/', resume_views.generate_resume, name='generate_resume'),
    path('chat/', chat_view, name='chat'),  # Changed from include('career_chatbot.urls') to direct view
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)