# File: base/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatMessage
from django.conf import settings
import json
import logging
from datetime import datetime
from .models import Student, Mentor, Alumni
from .search_utility import SearchUtility
from career_advisor.chatbot import CareerAdvisorChatbot
from mistralai.client import MistralClient
from decouple import config
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

# Set up logging
logger = logging.getLogger(__name__)

def dashboard(request):
    """Main dashboard view with dynamic content"""
    # Initialize search utility
    search_utility = SearchUtility()
    
    # Get search query if present
    search_query = request.GET.get('search', '')
    search_results = []
    
    # Define static resource data
    career_resources = [
        {
            'title': 'Resume and Cover Letter Builder',
            'description': 'Create professional documents with our easy-to-use templates.',
            'link': '/resources#resume-builder'
        },
        {
            'title': 'AI-Powered Career Coach',
            'description': 'Get personalized career advice and interview preparation.',
            'link': '/resources#ai-coach'
        },
        {
            'title': 'Skill Development Roadmap',
            'description': 'Track your progress and plan your professional development journey.',
            'link': '/resources#skill-development'
        },
        {
            'title': 'Personalized Career Planning',
            'description': 'Build confidence with customized career path recommendations.',
            'link': '/resources#career-planning'
        }
    ]
    
    additional_resources = [
        {
            'title': 'Resource & Opportunity Dashboard',
            'description': 'Access all career resources and opportunities in one place.',
            'link': '/resources#dashboard'
        },
        {
            'title': 'Testimonials and Case Studies',
            'description': 'Learn from success stories of UNCC graduates and alumni.',
            'link': '/resources#testimonials'
        },
        {
            'title': 'Job Opportunity Aggregation',
            'description': 'Find all relevant job postings customized to your profile.',
            'link': '/job-board'
        },
        {
            'title': 'Login / My Account',
            'description': 'Access your personalized dashboard and saved opportunities.',
            'link': '/login'
        }
    ]
    
    # Perform search if query is present
    if search_query:
        # Collect all data for searching
        search_data = {
            'resources': career_resources,
            'additional_resources': additional_resources
        }
        
        # Execute search
        search_results = search_utility.search(search_query, search_data)
        logger.info(f"Search for '{search_query}' returned {len(search_results)} results")
    
    # Prepare context for template
    context = {
        'career_resources': career_resources,
        'additional_resources': additional_resources,
        'search_results': search_results,
        'search_query': search_query,
        'current_year': datetime.now().year
    }
    
    return render(request, 'uncc-dashboard.html', context)

def job_board(request):
    """View for Job Board page with pagination"""
    # Get filter parameters from request
    job_type = request.GET.get('job_type', '')
    location = request.GET.get('location', '')
    industry = request.GET.get('industry', '')
    experience = request.GET.get('experience', '')
    search_query = request.GET.get('search', '')
    
    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    jobs_per_page = 21  # Display 20 jobs per page
    
    # Create context for template
    context = {
        'current_year': datetime.now().year,
        'search_query': search_query,
        'job_type': job_type,
        'location': location,
        'industry': industry,
        'experience': experience,
        # Pagination context
        'current_page': page,
        'total_pages': total_pages,
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1,
        'next_page': page + 1,
        'page_range': range(max(1, page - 2), min(total_pages + 1, page + 3)),
    }
    
    return render(request, 'uncc-job-board.html', context)

def networking_hub(request):
    """View for Networking Hub page"""
    return render(request, 'uncc-networking-hub.html')

def career_events(request):
    """View for Career Events page"""
    return render(request, 'uncc-career-events.html')

def resources(request):
    """View for Resources page"""
    return render(request, 'uncc-resources.html')

def mentorship_hub(request):
    """View for Mentorship Hub page"""
    return render(request, 'uncc-mentorship-hub.html')

def login(request):
    """View for Login page"""
    return render(request, 'uncc-login-page.html')

def home(request):
    """Home view, redirects to dashboard"""
    return dashboard(request)

def mentor_list(request):
    mentors = Mentor.objects.all()
    return render(request, 'mentors/mentor_list.html', {'mentors': mentors})   

# Initialize CareerAdvisorChatbot
logger.info("Attempting to initialize CareerAdvisorChatbot...")
try:
    chatbot = CareerAdvisorChatbot()
    logger.info("CareerAdvisorChatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize CareerAdvisorChatbot: {str(e)}", exc_info=True)
    chatbot = None

class ChatbotView(View):
    """View for handling chatbot interactions"""
    
    _chatbot = None
    
    @classmethod
    def get_chatbot(cls):
        """Get or initialize the chatbot instance"""
        if cls._chatbot is None:
            try:
                cls._chatbot = CareerAdvisorChatbot()
                logger.info("Successfully initialized chatbot")
            except Exception as e:
                logger.error(f"Failed to initialize chatbot: {str(e)}", exc_info=True)
                return None
        return cls._chatbot
    
    def get(self, request):
        """Handle GET requests"""
        try:
            chatbot = self.get_chatbot()
            if not chatbot:
                return JsonResponse({"error": "Failed to initialize chatbot"}, status=500)
            
            # Return initial context or welcome message
            return JsonResponse({
                "message": "Welcome to the Career Advisor Chatbot! How can I help you today?",
                "status": "success"
            })
        except Exception as e:
            logger.error(f"Error in ChatbotView GET: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)

    def post(self, request):
        try:
            chatbot = self.get_chatbot()
            if not chatbot:
                return JsonResponse({"error": "Failed to initialize chatbot"}, status=500)
            
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            chat_type = data.get('type', 'general')
            
            if not message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)
            
            logger.info(f"Received message: {message} (type: {chat_type})")
            
            context = self._get_career_context(chat_type)
            
            try:
                response = chatbot.get_response(message, context)
                logger.info(f"Generated response: {response['raw'][:100]}...")
                return JsonResponse({
                    "message": response['raw'],  # Send raw text instead of the entire response object
                    "html": response['html'],    # Also send the HTML formatted version
                    "status": "success"
                })
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}", exc_info=True)
                return JsonResponse({"error": f"Error generating response: {str(e)}"}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            logger.error(f"Error in ChatbotView POST: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)
    
    def _get_career_context(self, chat_type):
        """Get career-specific context based on chat type"""
        try:
            if chat_type == 'resume':
                return "You are a career advisor helping with resume writing and optimization."
            elif chat_type == 'interview':
                return "You are a career advisor providing interview preparation advice."
            elif chat_type == 'job_search':
                return "You are a career advisor helping with job search strategies."
            else:
                return "You are a career advisor providing general career guidance."
        except Exception as e:
            logger.error(f"Error getting career context: {str(e)}", exc_info=True)
            return "You are a career advisor providing general career guidance."

def chat_view(request):
    return render(request, 'chat.html') 

def test_chatbot(request):
    """Test endpoint to verify chatbot functionality"""
    try:
        # Check environment and API configuration
        from decouple import config
        from mistralai.client import MistralClient
        
        api_key = config('MISTRAL_API_KEY', default=None)
        if not api_key:
            logger.error("MISTRAL_API_KEY not found in environment variables")
            return HttpResponse("Error: API key not configured", status=500)
            
        # Safely check API configuration
        try:
            client = MistralClient(api_key=api_key)
            # Test with a simple message
            test_response = client.chat(
                model="mistral-tiny",
                messages=[{"role": "user", "content": "Test"}]
            )
            logger.info("API configuration verified successfully")
        except Exception as api_error:
            logger.error(f"API configuration error: {str(api_error)}", exc_info=True)
            return HttpResponse("Error: API configuration invalid", status=500)
        
        # Continue with existing chatbot test
        chatbot = ChatbotView.get_chatbot()
        if not chatbot:
            logger.error("Failed to initialize chatbot")
            return HttpResponse("Error: Failed to initialize chatbot", status=500)
        
        test_message = "Hello, can you help me with career advice?"
        logger.info(f"Sending test message: {test_message}")
        
        try:
            response = chatbot.get_response(test_message)
            logger.info(f"Received test response: {response[:100]}...")
            return HttpResponse(f"Chatbot test response: {response}")
        except Exception as e:
            logger.error(f"Error getting chatbot response: {str(e)}", exc_info=True)
            return HttpResponse(f"Error getting response: {str(e)}", status=500)
            
    except Exception as e:
        logger.error(f"Error in test_chatbot: {str(e)}", exc_info=True)
        return HttpResponse(f"Error: {str(e)}", status=500)
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            account_type = form.cleaned_data.get('account_type')

            if account_type == 'student':
                graduation_year = form.cleaned_data.get('graduation_year')
                Student.objects.create(user=user, graduation_year=graduation_year)
            elif account_type == 'mentor':
                Mentor.objects.create(user=user)
            elif account_type == 'alumni':
                Alumni.objects.create(user=user)

            return redirect('login')  # or wherever you want to send them
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})