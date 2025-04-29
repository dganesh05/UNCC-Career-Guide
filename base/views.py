# File: base/views.py
from django.shortcuts import render, redirect, get_object_or_404
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
from .hire_a_niner_jobs_integration import HireANinerJobsIntegration
from .career_events_parser import CareerEventsParser
from career_advisor.chatbot import CareerAdvisorChatbot
from mistralai.client import MistralClient
from decouple import config
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import MentorForm, StudentForm, AlumniForm
from django.contrib.auth import logout
from django.contrib.auth import login  
from .models import Message
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from .models import ResourceOpportunity, CareerStep

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
    
    # Get featured job opportunities
    try:
        # Initialize the HireANinerJobsIntegration for featured opportunities
        jobs_integration = HireANinerJobsIntegration()
        featured_opportunities = jobs_integration.get_jobs(limit=3)  # Get 3 featured jobs
        logger.info(f"Found {len(featured_opportunities)} featured job opportunities")
    except Exception as e:
        logger.error(f"Error fetching featured opportunities: {str(e)}", exc_info=True)
        featured_opportunities = []  # Empty list if there's an error
    
    # Perform search if query is present
    if search_query:
        # Collect all data for searching
        search_data = {
            'opportunities': featured_opportunities,
            'resources': career_resources,
            'additional_resources': additional_resources,
            'events': []  # This could be populated with events if needed
        }
        
        # Execute search
        search_results = search_utility.search(search_query, search_data)
        logger.info(f"Search for '{search_query}' returned {len(search_results)} results")
    
    # Prepare context for template
    context = {
        'career_resources': career_resources,
        'additional_resources': additional_resources,
        'featured_opportunities': featured_opportunities,
        'search_results': search_results,
        'search_query': search_query,
        'current_year': datetime.now().year
    }
    
    return render(request, 'uncc-dashboard.html', context)

def job_board(request):
    """View for Job Board page with enhanced filtering and pagination"""
    # Get filter parameters from request
    job_type = request.GET.get('job_type', '')
    location = request.GET.get('location', '')
    industry = request.GET.get('industry', '')
    search_query = request.GET.get('search', '')
    
    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    jobs_per_page = 18  # Display 6 jobs per page for better grid layout
    
    try:
        # Initialize and use the HireANinerJobsIntegration
        jobs_integration = HireANinerJobsIntegration()
        
        # Pass the filter parameters to the integration
        all_jobs = jobs_integration.get_jobs(
            limit=250,  # Get a larger set to filter from
            job_type=job_type,
            location=location,
            search_term=search_query
        )
        
        # Apply additional filtering by industry
        if industry:
            # Case-insensitive filtering by field/industry
            all_jobs = [job for job in all_jobs if industry.lower() in job.get('field', '').lower()]
        
        # Calculate total jobs and pages
        total_jobs = len(all_jobs)
        total_pages = max(1, (total_jobs + jobs_per_page - 1) // jobs_per_page)
        
        # Ensure page number is valid
        page = max(1, min(page, total_pages))
        
        # Get the jobs for the current page
        start_idx = (page - 1) * jobs_per_page
        end_idx = start_idx + jobs_per_page
        jobs = all_jobs[start_idx:end_idx]
        
    except Exception as e:
        # In case of any error, return empty data
        jobs = []
        total_jobs = 0
        total_pages = 1
        page = 1
    
    # Create dynamic page range for pagination (show only ~5 pages around current)
    page_radius = 2  # Show 2 pages before and after current page
    page_range = range(
        max(1, page - page_radius),
        min(total_pages + 1, page + page_radius + 1)
    )
    
    # Create context for template
    context = {
        'jobs': jobs,
        'job_count': total_jobs,
        'search_query': search_query,
        'job_type': job_type,
        'location': location,
        'industry': industry,
        # Pagination context
        'current_page': page,
        'total_pages': total_pages,
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1,
        'next_page': page + 1,
        'page_range': page_range,
        'current_year': datetime.now().year
    }
    
    return render(request, 'uncc-job-board.html', context)

def networking_hub(request):
    """View for Networking Hub page"""
    return render(request, 'uncc-networking-hub.html')

def career_events(request):
    """View for Career Events page using Hire-a-Niner data"""
    # Get filter parameters
    event_type = request.GET.get('event_type', '')
    date_range = request.GET.get('date_range', '')
    
    try:
        # Initialize and use the CareerEventsParser
        events_parser = CareerEventsParser()
        events = events_parser.get_events(
            limit=40,
            event_type=event_type,
            date_range=date_range
        )
    except Exception as e:
        events = []
    
    # Create context for template
    context = {
        'events': events,
        'event_type': event_type,
        'date_range': date_range,
        'current_year': datetime.now().year
    }
    
    return render(request, 'uncc-career-events.html', context)

def resources(request):
    """View for Resources page with integrated dashboard"""
    # Get resources from admin
    resources = ResourceOpportunity.objects.all()
    category_filter = request.GET.get('category')

    if category_filter:
        resources = resources.filter(category=category_filter)

    categories = [choice[0] for choice in ResourceOpportunity.CATEGORY_CHOICES]

    context = {
        'resources': resources,
        'categories': categories,
        'selected_category': category_filter,
        'current_year': datetime.now().year
    }
    return render(request, 'uncc-resources.html', context)

def mentorship_hub(request):
    """View for Mentorship Hub page"""
    return render(request, 'uncc-mentorship-hub.html')


def custom_login(request):
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
            profile_type = form.cleaned_data['account_type']

            if profile_type == 'mentor':
                Mentor.objects.create(user=user, full_name=f"{user.first_name} {user.last_name}")
            elif profile_type == 'student':
                graduation_year = form.cleaned_data.get('graduation_year')
                Student.objects.create(
                    user=user,
                    full_name=f"{user.first_name} {user.last_name}",
                    graduation_year=graduation_year
                )
            elif profile_type == 'alumni':
                Alumni.objects.create(user=user, full_name=f"{user.first_name} {user.last_name}")

            
            login(request, user)
            return redirect('edit_profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def edit_profile(request):
    user = request.user
    profile = None
    form_class = None

    
    if hasattr(user, 'mentor'):
        profile = user.mentor
        form_class = MentorForm
    elif hasattr(user, 'student'):
        profile = user.student
        form_class = StudentForm
    elif hasattr(user, 'alumni'):
        profile = user.alumni
        form_class = AlumniForm
    else:
        return redirect('home')  

   
    if request.method == 'POST':
        form = form_class(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  
    else:
        form = form_class(instance=profile)

    return render(request, 'registration/edit_profile.html', {'form': form})


def custom_logout(request):
    logout(request)
    return redirect('home') 

def mentor_detail(request, mentor_id):
    mentor = get_object_or_404(Mentor, id=mentor_id)
    return render(request, 'mentors/mentor_detail.html', {'mentor': mentor})
    
@login_required
def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content')

        if not recipient_id or not content:
            logger.error(f"Invalid data: recipient_id={recipient_id}, content={content}")
            return JsonResponse({'error': 'Recipient and content are required.'}, status=400)

        try:
            recipient = get_object_or_404(User, id=recipient_id)
            Message.objects.create(sender=request.user, recipient=recipient, content=content)
            logger.info(f"Message sent: sender={request.user}, recipient={recipient}, content={content}")
            return JsonResponse({'success': 'Message sent successfully.'})
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return JsonResponse({'error': 'An error occurred while sending the message.'}, status=500)

@login_required
def get_messages(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=recipient) |
        Q(sender=recipient, recipient=request.user)
    ).order_by('timestamp')

    messages_data = [
        {
            'sender': message.sender.username,
            'recipient': message.recipient.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': message.is_read,
        }
        for message in messages
    ]

    return JsonResponse({'messages': messages_data})

def alumni_list(request):
    alumni = Alumni.objects.all()  # Fetch all alumni from the database
    return render(request, 'alumni/alumni_list.html', {'alumni': alumni})

def alumni_detail(request, alumni_id):
    alumnus = get_object_or_404(Alumni, id=alumni_id)
    return render(request, 'alumni/alumni_detail.html', {'alumnus': alumnus})

def resource_dashboard(request):
    resources = ResourceOpportunity.objects.all()  # Fetch all opportunities
    category_filter = request.GET.get('category')

    if category_filter:
        resources = resources.filter(category=category_filter)

    categories = [choice[0] for choice in ResourceOpportunity.CATEGORY_CHOICES]

    context = {
        'resources': resources,
        'categories': categories,
        'selected_category': category_filter
    }
    return render(request, 'uncc-resource-dashboard.html', context)

def career_confidence_boost(request):
    return render (request, 'uncc-career-confidence-boost.html')

def visualize_trajectory(request):
    role = request.GET.get('role', 'Software Developer')  # Default for now
    steps = CareerStep.objects.filter(role=role)
    roles = CareerStep.objects.values_list('role', flat=True).distinct()

    return render(request, 'uncc_career_trajectory.html', {
        'steps': steps,
        'roles': roles,
        'selected_role': role
    })