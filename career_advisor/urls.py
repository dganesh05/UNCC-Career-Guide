from django.urls import path
from . import views

app_name = 'career_advisor'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/chat/', views.ChatbotView.as_view(), name='chat_api'),
    path('test/', views.test_chatbot, name='test_chatbot'),
] 