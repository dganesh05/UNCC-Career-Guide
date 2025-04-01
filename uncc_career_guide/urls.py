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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('job-board/', job_board, name='job_board'),
    path('networking-hub/', networking_hub, name='networking_hub'),
    path('career-events/', career_events, name='career_events'),
    path('resources/', resources, name='resources'),
    path('mentorship-hub/', mentorship_hub, name='mentorship_hub'),
    path('login/', login, name='login'),
]