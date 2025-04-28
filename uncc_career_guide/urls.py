"""
URL Configuration for UNCC Career Guide project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from base.views import (
    # Core views
    home, dashboard, custom_login, custom_logout, signup, edit_profile,
    # Resource views
    resources, resource_dashboard, career_confidence_boost, visualize_trajectory,
    # Career development views
    job_board, networking_hub, career_events, mentorship_hub,
    # Community views
    mentor_list, mentor_detail, alumni_list, alumni_detail,
    # Communication views
    chat_view, send_message, get_messages,
    # API views
    ChatbotView
)
from resume_generator import views as resume_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Core pages
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('signup/', signup, name='signup'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    
    # Resource pages
    path('resources/', resources, name='resources'),
    path('resource-dashboard/', resource_dashboard, name='resource_dashboard'),
    path('career-confidence-boost/', career_confidence_boost, name='career_confidence_boost'),
    path('visualize-trajectory/', visualize_trajectory, name='visualize_trajectory'),
    
    # Career development pages
    path('job-board/', job_board, name='job_board'),
    path('networking/', networking_hub, name='networking'),
    path('events/', career_events, name='events'),
    path('mentorship/', mentorship_hub, name='mentorship'),
    
    # Community pages
    path('mentors/', mentor_list, name='mentor_list'),
    path('mentor/<int:mentor_id>/', mentor_detail, name='mentor_detail'),
    path('alumni/', alumni_list, name='alumni_list'),
    path('alumni/<int:alumni_id>/', alumni_detail, name='alumni_detail'),
    
    # Communication features
    path('chat/', chat_view, name='chat'),
    path('messages/send/', send_message, name='send_message'),
    path('messages/<int:recipient_id>/', get_messages, name='get_messages'),
    
    # API endpoints
    path('api/chat/', ChatbotView.as_view(), name='chat_api'),
    
    # Additional apps
    path('career-advisor/', include('career_advisor.urls')),
    path('generate-resume/', resume_views.generate_resume, name='generate_resume'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('base.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
