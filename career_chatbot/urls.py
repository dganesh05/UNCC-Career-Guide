from django.urls import path
from base.views import ChatbotView, chat_view

urlpatterns = [
    path('', chat_view, name='chat'),
    path('api/chat/', ChatbotView.as_view(), name='chat-api'),
] 