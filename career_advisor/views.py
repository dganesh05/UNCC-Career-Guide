from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json
import logging
import uuid
import traceback
import sys
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import CareerConversation
from .chatbot import CareerAdvisorChatbot

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Initialize CareerAdvisorChatbot
try:
    chatbot = CareerAdvisorChatbot()
    logger.info("CareerAdvisorChatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize CareerAdvisorChatbot: {str(e)}")
    chatbot = None

def chat_view(request):
    """Render the chat interface"""
    return render(request, 'chat.html')

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotView(APIView):
    def get_career_prompt(self, chat_type):
        """Get the appropriate prompt based on chat type"""
        prompts = {
            'general': "You are a helpful career advisor specializing in technology careers. Provide detailed, practical advice with specific examples and steps.",
            'connection_request': "You are a LinkedIn expert. Help craft a personalized connection request that is professional and engaging.",
            'cover_letter': "You are a professional cover letter writer. Help create or review cover letters that highlight relevant skills and experiences.",
            'resume_review': "You are an expert resume reviewer. Analyze the resume and provide specific, actionable feedback for improvement."
        }
        return prompts.get(chat_type, prompts['general'])

    def post(self, request):
        """Handle chat requests"""
        logger.info("Received chat request")
        try:
            data = request.data
            logger.info(f"Request data: {data}")

            if not chatbot:
                logger.error("Chatbot not initialized")
                return Response({
                    'error': 'Chatbot not initialized. Please check your configuration.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            message = data.get('message', '')
            chat_type = data.get('type', 'general')
            session_id = data.get('session_id', '')

            if not message:
                logger.warning("Empty message received")
                return Response({
                    'error': 'Message cannot be empty'
                }, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Processing message: {message[:100]}... with chat type: {chat_type}")

            try:
                # Get career-specific context
                context = self.get_career_prompt(chat_type)
                logger.info("Got career prompt")
                
                # Get response from chatbot
                logger.info("Requesting response from chatbot")
                assistant_message = chatbot.get_response(message, context)
                logger.info(f"Received response from chatbot: {assistant_message[:100]}...")

                if not assistant_message:
                    logger.error("Empty response from chatbot")
                    raise ValueError("Empty response from chatbot")

                return Response({
                    'message': assistant_message,
                    'session_id': session_id
                })

            except Exception as e:
                logger.error(f"Error getting chatbot response: {str(e)}")
                return Response({
                    'error': f'Failed to get response from chatbot: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Error in chat API: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def test_chatbot(request):
    """Test endpoint to verify chatbot functionality"""
    try:
        if not chatbot:
            return HttpResponse("Error: Chatbot not initialized", status=500)
        
        test_message = "Hello, can you help me with career advice?"
        response = chatbot.get_response(test_message)
        
        return HttpResponse(f"Chatbot test response: {response}")
    except Exception as e:
        logger.error(f"Error in test_chatbot: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)
