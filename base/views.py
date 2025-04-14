from django.shortcuts import render, redirect
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatMessage
from django.conf import settings
import openai
from decouple import config
import json
import logging

# Create your views here.

logger = logging.getLogger(__name__)

# Initialize OpenAI client
try:
    api_key = config('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in environment variables")
    client = openai.OpenAI(api_key=api_key)
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

class ChatbotView(APIView):
    def get_career_prompt(self, chat_type):
        prompts = {
            'general': "You are a helpful career advisor. Provide detailed and practical career advice.",
            'connection_request': "You are a LinkedIn expert. Help craft a personalized connection request that is professional and engaging.",
            'cover_letter': "You are a professional cover letter writer. Help create or review cover letters that highlight relevant skills and experiences.",
            'resume_review': "You are an expert resume reviewer. Analyze the resume and provide specific, actionable feedback for improvement."
        }
        return prompts.get(chat_type, prompts['general'])

    def post(self, request):
        try:
            if not client:
                return Response({
                    'error': 'OpenAI client not initialized. Please check your API key.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            data = request.data
            message = data.get('message', '')
            chat_type = data.get('type', 'general')
            session_id = data.get('session_id', '')

            # Save user message
            ChatMessage.objects.create(
                content=message,
                role='user',
                session_id=session_id
            )

            # Get conversation history
            history = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
            messages = [{"role": msg.role, "content": msg.content} for msg in history]

            # Add system message with specific career prompt
            messages.insert(0, {
                "role": "system",
                "content": self.get_career_prompt(chat_type)
            })

            # Get response from OpenAI
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )

            assistant_message = response.choices[0].message.content

            # Save assistant response
            ChatMessage.objects.create(
                content=assistant_message,
                role='assistant',
                session_id=session_id
            )

            return Response({
                'message': assistant_message,
                'session_id': session_id
            })

        except Exception as e:
            logger.error(f"Error in chat API: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def chat_view(request):
    return render(request, 'career_chatbot/chat.html') 