from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from base import views
from base.views import (
    dashboard,
    job_board, 
    networking_hub, 
    career_events,
    resources, 
    mentorship_hub,
    login,
    home,
    chat_view
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
    path('dashboard/', dashboard, name='dashboard'),
    path('job-board/', job_board, name='job_board'),
    path('networking/', networking_hub, name='networking'),
    path('events/', career_events, name='events'),
    path('resources/', resources, name='resources'),
    path('mentorship/', mentorship_hub, name='mentorship'),
    path('login/', login, name='login'),
    path('career-advisor/', include('career_advisor.urls')),
    path('chat/', chat_view, name='chat'),
    path('api/chat/', views.ChatbotView.as_view(), name='chat_api'),
    path('generate-resume/', resume_views.generate_resume, name='generate_resume'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('base.urls')),
    path('signup/', views.signup, name='signup'),
    path('mentors/', views.mentor_list, name='mentor_list'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)