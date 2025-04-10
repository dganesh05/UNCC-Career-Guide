# File: base/views.py
from django.shortcuts import render
from datetime import datetime
import logging
from .models import Mentor

# Import our integration classes
from .linkedin_integration import LinkedInJobsIntegration
from .niner_events_integration import NinerCareerEventsIntegration
from .hire_a_niner_jobs_integration import HireANinerJobsIntegration
from .search_utility import SearchUtility

# Set up logging
logger = logging.getLogger(__name__)

def dashboard(request):
    """Main dashboard view with dynamic content"""
    # Initialize integrations
    linkedin = LinkedInJobsIntegration()
    niner_events = NinerCareerEventsIntegration()
    niner_jobs = HireANinerJobsIntegration()
    search_utility = SearchUtility()
    
    # Get search query if present
    search_query = request.GET.get('search', '')
    search_results = []
    
    try:
        # Fetch featured opportunities - now using Hire a Niner integration
        featured_opportunities = niner_jobs.get_jobs(limit=3)
        logger.info(f"Successfully fetched {len(featured_opportunities)} opportunities from Hire A Niner")
    except Exception as e:
        logger.error(f"Error fetching Hire A Niner jobs: {str(e)}")
        # Fall back to LinkedIn if Hire A Niner fails
        try:
            featured_opportunities = linkedin.get_featured_opportunities(count=3)
            logger.info(f"Fallback: Successfully fetched {len(featured_opportunities)} opportunities from LinkedIn")
        except Exception as e2:
            logger.error(f"Error fetching LinkedIn opportunities: {str(e2)}")
            featured_opportunities = []
    
    try:
        # Fetch upcoming events from Niner Career Events
        upcoming_events = niner_events.get_upcoming_events(count=2)
        logger.info(f"Successfully fetched {len(upcoming_events)} events from Niner Career")
    except Exception as e:
        logger.error(f"Error fetching Niner events: {str(e)}")
        upcoming_events = []
    
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
            'opportunities': featured_opportunities,
            'events': upcoming_events,
            'resources': career_resources,
            'additional_resources': additional_resources
        }
        
        # Execute search
        search_results = search_utility.search(search_query, search_data)
        logger.info(f"Search for '{search_query}' returned {len(search_results)} results")
    
    # Prepare context for template
    context = {
        'featured_opportunities': featured_opportunities,
        'upcoming_events': upcoming_events,
        'career_resources': career_resources,
        'additional_resources': additional_resources,
        'search_results': search_results,
        'search_query': search_query,
        'current_year': datetime.now().year
    }
    
    return render(request, 'uncc-dashboard.html', context)

def job_board(request):
    """View for Job Board page"""
    # Initialize job integration
    niner_jobs = HireANinerJobsIntegration()
    
    # Get filter parameters from request
    job_type = request.GET.get('job_type', '')
    location = request.GET.get('location', '')
    industry = request.GET.get('industry', '')
    experience = request.GET.get('experience', '')
    search_query = request.GET.get('search', '')
    
    try:
        # Fetch jobs with filters
        if job_type or location or search_query:
            logger.info(f"Fetching filtered jobs: type={job_type}, location={location}, search={search_query}")
            jobs = niner_jobs.get_jobs(
                limit=20, 
                job_type=job_type, 
                location=location,
                search_term=search_query
            )
        else:
            logger.info("Fetching all jobs")
            jobs = niner_jobs.get_jobs(limit=20)
        
        job_count = len(jobs)
        logger.info(f"Found {job_count} jobs")
    except Exception as e:
        logger.error(f"Error fetching jobs: {str(e)}")
        jobs = []
        job_count = 0
    
    # Get recommended jobs (simplified - in production this would use user preferences)
    try:
        recommended_jobs = niner_jobs.get_jobs(limit=4)
    except Exception as e:
        logger.error(f"Error fetching recommended jobs: {str(e)}")
        recommended_jobs = []
    
    # Create context for template
    context = {
        'jobs': jobs,
        'job_count': job_count,
        'recommended_jobs': recommended_jobs,
        'current_year': datetime.now().year,
        'search_query': search_query,
        'job_type': job_type,
        'location': location,
        'industry': industry,
        'experience': experience
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