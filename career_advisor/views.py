from django.shortcuts import render, redirect
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
from base.models import ChatMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CHAT_CONTEXTS = {
    'general': "You are a helpful career advisor specializing in technology careers. Provide detailed, practical advice with specific examples and steps.",
    'resume': "You are an expert resume reviewer. Help with formatting, content, and tailoring resumes for specific roles. Provide tips for creating strong bullet points and summaries. Focus on tech industry best practices.",
    'cover_letter': "You are a professional cover letter writer. Help create or review cover letters that highlight relevant skills and experiences. Provide specific guidance on structure, tone, and content tailored to tech roles.",
    'linkedin': "You are a LinkedIn profile optimization expert. Help craft compelling headlines, summaries, and experience descriptions. Provide advice on networking strategies and profile visibility in the tech industry.",
    'job_search': "You are a tech career strategist. Share tips on finding job opportunities, identifying the right companies, and organizing the job search. Focus on tech industry trends and job search platforms.",
    'networking': "You are a tech industry networking expert. Guide on connecting with professionals, reaching out to recruiters, and expanding professional networks. Help draft professional communication and build meaningful connections.",
    'interview': "You are an interview preparation specialist for tech roles. Provide advice on technical and behavioral interviews, common questions, and best practices. Share specific examples and preparation strategies.",
    'elevator_pitch': "You are a personal branding expert. Help craft concise and impactful introductions for networking or interviews. Focus on highlighting technical skills and achievements effectively.",
    'communication': "You are a professional communication coach. Assist with writing emails, messages, and other professional communications. Provide guidance on tone, structure, and etiquette in tech industry contexts."
}

# Initialize CareerAdvisorChatbot
try:
    chatbot = CareerAdvisorChatbot()
    logger.info("CareerAdvisorChatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize CareerAdvisorChatbot: {str(e)}")
    chatbot = None

def get_chat_context(chat_type):
    """Get the appropriate context based on chat type"""
    return CHAT_CONTEXTS.get(chat_type, CHAT_CONTEXTS['general'])

def chat_view(request):
    """Render the chat interface and handle form submissions"""
    session_id = request.session.get('chat_session_id', str(uuid.uuid4()))
    
    # Handle AJAX requests
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
            chat_type = data.get('chat_type', 'general')
            
            # Handle session reset
            if data.get('reset_session'):
                # Generate new session ID
                session_id = str(uuid.uuid4())
                request.session['chat_session_id'] = session_id
                request.session['chat_type'] = chat_type
                
                return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Get chat type from POST, session, or default to 'general'
    chat_type = request.POST.get('chat_type', request.session.get('chat_type', 'general'))
    request.session['chat_type'] = chat_type
    
    return render(request, 'chat.html', {
        'messages': ChatMessage.objects.filter(session_id=session_id),
        'chat_type': chat_type
    })

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotView(APIView):
    def post(self, request):
        """Handle chat API requests"""
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
                # Get context based on chat type
                context = CHAT_CONTEXTS.get(chat_type, CHAT_CONTEXTS['general'])
                logger.info(f"Using context for chat type: {chat_type}")
                
                # Save user message
                ChatMessage.objects.create(
                    content=message,
                    role='user',
                    session_id=session_id
                )
                
                # Get response from chatbot
                response = chatbot.get_response(message, context)
                response_content = response.get('raw', '')
                
                # Save assistant message
                ChatMessage.objects.create(
                    content=response_content,
                    role='assistant',
                    session_id=session_id
                )
                
                return Response({
                    'message': response_content,
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
        context = get_chat_context('general')
        response = chatbot.get_response(test_message, context)
        
        return HttpResponse(f"Chatbot test response: {response}")
    except Exception as e:
        logger.error(f"Error in test_chatbot: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)
