# File: base/views.py
from django.shortcuts import render
from datetime import datetime
import logging
from .linkedin_integration import LinkedInJobsIntegration
from .niner_events_integration import NinerCareerEventsIntegration
from .search_utility import SearchUtility
# Set up logging
logger = logging.getLogger(__name__)

def dashboard(request):
    """Main dashboard view with dynamic content"""
    # Initialize integrations
    linkedin = LinkedInJobsIntegration()
    search_utility = SearchUtility()
    
    # Get search query if present
    search_query = request.GET.get('search', '')
    search_results = []
    
    try:
        # Fetch featured opportunities
        featured_opportunities = linkedin.get_featured_opportunities(count=3)
        logger.info(f"Successfully fetched {len(featured_opportunities)} opportunities from LinkedIn")
    except Exception as e:
        logger.error(f"Error fetching LinkedIn opportunities: {str(e)}")
        featured_opportunities = []
    
    # Create a new instance each time to avoid any caching issues
    niner_events = NinerCareerEventsIntegration()
    
    try:
        # Fetch upcoming events with better error reporting
        logger.info("=" * 40)
        logger.info("FETCHING EVENTS FOR DASHBOARD")
        
        # Get events with increased timeout
        upcoming_events = niner_events.get_upcoming_events(count=2)
        
        if upcoming_events:
            logger.info(f"Dashboard view received {len(upcoming_events)} events")
            
            # Log first event details for debugging
            if len(upcoming_events) > 0:
                event = upcoming_events[0]
                logger.info(f"First event: {event.get('title')} on {event.get('date')}")
        else:
            logger.warning("No events were returned to dashboard view")
            upcoming_events = []
    except Exception as e:
        logger.error(f"Error in dashboard when fetching events: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Explicitly generate placeholder data
        niner_events = NinerCareerEventsIntegration()
        upcoming_events = niner_events._get_placeholder_data(2)
        logger.info("Using placeholder events due to error")
    
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
    
    # Ensure we have events data no matter what
    if not upcoming_events:
        niner_events = NinerCareerEventsIntegration()
        upcoming_events = niner_events._get_placeholder_data(2)
        logger.info("Using placeholder events as fallback")
    
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
    
    # Log what we're sending to the template
    logger.info(f"Sending {len(upcoming_events)} events to template")
    
    return render(request, 'uncc-dashboard.html', context)

def job_board(request):
    """View for Job Board page"""
    return render(request, 'uncc-job-board.html')

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

def debug_events(request):
    """A view to debug the events fetching functionality"""
    from django.http import JsonResponse
    
    # Initialize the integration
    niner_events = NinerCareerEventsIntegration()
    
    try:
        # Fetch events
        logger.info("Debugging events fetch")
        events = niner_events.get_upcoming_events(count=5)
        
        # Return events as JSON for debugging
        return JsonResponse({
            'success': True,
            'event_count': len(events),
            'events': events
        })
    except Exception as e:
        import traceback
        logger.error(f"Error in debug_events view: {str(e)}")
        logger.error(traceback.format_exc())
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })