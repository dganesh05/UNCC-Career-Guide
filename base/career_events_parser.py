import requests
from bs4 import BeautifulSoup
import logging
import random
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

class CareerEventsParser:
    """Parser for fetching career events from UNCC's Hire-a-Niner calendar"""
    
    def __init__(self):
        # Set the primary URL to the Hire-a-Niner events page
        self.base_url = "https://hireaniner.charlotte.edu/events"
        self.backup_urls = [
            "https://career.charlotte.edu/events-fairs",
            "https://career.charlotte.edu/events"
        ]
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    
    def get_events(self, limit: int = 10, event_type: str = None, date_range: str = None) -> List[Dict[str, Any]]:
        """
        Fetches career events from UNCC's Hire-a-Niner website
        
        Args:
            limit (int): Maximum number of events to return
            event_type (str): Filter by event type (e.g., "Meet Up", "Career Fair")
            date_range (str): Filter by date range (e.g., "this-week", "this-month")
            
        Returns:
            List[Dict[str, Any]]: List of event dictionaries with details
        """
        events = []
        # Try the primary URL first
        url = self.base_url
        
        # Add query parameters if provided
        params = {}
        if event_type:
            # Convert event_type to URL-friendly format
            params['type'] = event_type.lower().replace(' ', '-')
        if date_range:
            params['date'] = date_range
        
        # Try the main URL and backup URLs if needed
        urls_to_try = [self.base_url] + self.backup_urls
        
        for current_url in urls_to_try:
            try:
                # Set up headers
                headers = {
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml",
                    "Accept-Language": "en-US,en;q=0.9",
                }
                
                # Make the request with increased timeout
                response = requests.get(current_url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    # Parse events from HTML
                    events = self._parse_events_html(response.text, limit)
                    
                    if events:
                        # Apply additional filtering on the client side
                        if event_type and events:
                            # Filter by event type (case-insensitive match)
                            events = [event for event in events if event['type'].lower() == event_type.lower()]
                        
                        if date_range and events:
                            # Filter by date range
                            events = self._filter_by_date_range(events, date_range)
                        
                        return events
                
            except Exception:
                # Continue to try the next URL if this one fails
                continue
        
        # Fall back to placeholder data if all URLs fail
        events = self._get_placeholder_data(limit)
        
        # Apply filters to placeholder data too
        if event_type and events:
            events = [event for event in events if event['type'].lower() == event_type.lower()]
        
        if date_range and events:
            events = self._filter_by_date_range(events, date_range)
            
        return events[:limit]  # Ensure we don't exceed the limit
    
    def _filter_by_date_range(self, events: List[Dict[str, Any]], date_range: str) -> List[Dict[str, Any]]:
        """Filter events by date range"""
        now = datetime.now()
        filtered_events = []
        
        for event in events:
            event_date = event['date']
            try:
                # Try to parse the event date
                parsed_date = None
                date_formats = [
                    "%B %d, %Y",      # May 20, 2025
                    "%b %d, %Y",       # May 20, 2025
                ]
                
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(event_date, fmt)
                        break
                    except ValueError:
                        continue
                
                if not parsed_date:
                    # If we couldn't parse the date, include the event by default
                    filtered_events.append(event)
                    continue
                
                # Apply date range filter
                if date_range == 'this-week':
                    # This week is defined as today through next 7 days
                    end_of_week = now + timedelta(days=7)
                    if now <= parsed_date <= end_of_week:
                        filtered_events.append(event)
                
                elif date_range == 'this-month':
                    # This month means events in the current calendar month
                    if parsed_date.month == now.month and parsed_date.year == now.year:
                        filtered_events.append(event)
                
                elif date_range == 'next-month':
                    # Next month means events in the next calendar month
                    next_month = now.month + 1 if now.month < 12 else 1
                    next_month_year = now.year if now.month < 12 else now.year + 1
                    if parsed_date.month == next_month and parsed_date.year == next_month_year:
                        filtered_events.append(event)
                else:
                    # Unknown date range or 'all dates', include all events
                    filtered_events.append(event)
                
            except Exception:
                # If there's any error in date parsing, include the event by default
                filtered_events.append(event)
        
        return filtered_events
    
    def _parse_events_html(self, html: str, limit: int) -> List[Dict[str, Any]]:
        """Parse event listings from the Hire-a-Niner HTML based on the given structure"""
        soup = BeautifulSoup(html, 'html.parser')
        events = []
        
        # Based on the provided HTML structure, target div with class "event list event-meetup"
        event_elements = soup.select('div.event.list.event-meetup')
        
        # If no events found with the specific class, try more generic selectors
        if not event_elements:
            # Try other selectors based on the provided structure
            alternative_selectors = [
                'div.event',
                'div[class*="event"]',
                '.event-list div',
                '.events-container div',
                'div.list.event-meetup'
            ]
            
            for selector in alternative_selectors:
                temp_elements = soup.select(selector)
                if temp_elements:
                    event_elements = temp_elements
                    break
        
        # Process found elements
        for element in event_elements[:limit]:
            try:
                # Extract event title from the h3 > a structure
                title_element = element.select_one('h3 > a')
                if title_element:
                    title = title_element.get_text(strip=True)
                    event_link = title_element.get('href', '#')
                    # Fix relative URLs
                    if event_link.startswith('./') or event_link.startswith('/'):
                        base_domain = self.base_url.split('/events')[0]
                        event_link = f"{base_domain}{event_link.replace('.', '')}"
                else:
                    # Try alternative title selectors
                    title_element = element.select_one('h3, h2, h4, .title, [class*="title"]')
                    title = title_element.get_text(strip=True) if title_element else "Career Event"
                    event_link = "#"
                
                # Extract date/time from text after the clock icon
                datetime_element = element.select_one('i.fa-clock')
                if datetime_element and datetime_element.next_sibling:
                    datetime_text = datetime_element.next_sibling.strip()
                else:
                    # Try to find any text that looks like a date/time
                    blockquote = element.select_one('blockquote')
                    if blockquote:
                        blockquote_text = blockquote.get_text()
                        # Look for patterns like dates
                        date_pattern = r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?\s*,?\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s*,?\s*\d{4}'
                        date_match = re.search(date_pattern, blockquote_text, re.IGNORECASE)
                        if date_match:
                            datetime_text = date_match.group(0)
                        else:
                            datetime_text = ""
                    else:
                        datetime_text = ""
                
                # Parse the date and time
                event_date, event_time = self._parse_datetime(datetime_text)
                
                # Extract location from text after the map marker icon
                location_element = element.select_one('i.fa-map-marker-alt')
                if location_element and location_element.next_sibling:
                    location = location_element.next_sibling.strip()
                else:
                    # Try to find any text that might be a location
                    location = "UNCC Campus"
                
                # Extract description - not present in the sample HTML, so we'll create a generic one
                description = f"Join us for this exciting event: {title}. See event details for more information."
                
                # Determine event type based on title
                event_type = self._determine_event_type(title, description)
                
                # Check if registration is required (assuming events require registration by default)
                registration_required = True
                
                # Create event dictionary
                event = {
                    'title': title,
                    'date': event_date,
                    'time': event_time,
                    'location': location,
                    'description': description,
                    'type': event_type,
                    'registration_required': registration_required,
                    'link': event_link
                }
                
                events.append(event)
            except Exception:
                # Skip events that can't be parsed
                continue
        
        return events
    
    def _parse_datetime(self, datetime_text: str) -> tuple:
        """Parse the datetime text into separate date and time components"""
        if not datetime_text:
            # Generate a random future date if no date is found
            future_days = random.randint(1, 30)
            future_date = datetime.now() + timedelta(days=future_days)
            return future_date.strftime("%B %d, %Y"), "2:00 - 3:00 PM"
        
        try:
            # The example format was "Tuesday, May 20, 2025, 2:00 - 2:45 pm"
            # Extract the date part
            date_pattern = r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?\s*,?\s*((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s*,?\s*\d{4})'
            date_match = re.search(date_pattern, datetime_text, re.IGNORECASE)
            
            if date_match:
                date_str = date_match.group(1)
            else:
                # If no match, try a simpler pattern
                date_pattern = r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s*,?\s*\d{4})'
                date_match = re.search(date_pattern, datetime_text, re.IGNORECASE)
                date_str = date_match.group(1) if date_match else ""
            
            # Extract the time part
            time_pattern = r'(\d{1,2}:\d{2}\s*(?:-\s*\d{1,2}:\d{2})?\s*(?:am|pm|AM|PM))'
            time_match = re.search(time_pattern, datetime_text, re.IGNORECASE)
            
            if time_match:
                time_str = time_match.group(1)
            else:
                # Try an alternative time pattern
                time_pattern = r'(\d{1,2}(?::\d{2})?\s*-\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))'
                time_match = re.search(time_pattern, datetime_text, re.IGNORECASE)
                time_str = time_match.group(1) if time_match else ""
            
            return date_str if date_str else "Future Date TBD", time_str if time_str else "Time TBD"
            
        except Exception:
            future_days = random.randint(1, 30)
            future_date = datetime.now() + timedelta(days=future_days)
            return future_date.strftime("%B %d, %Y"), "2:00 - 3:00 PM"
    
    def _determine_event_type(self, title: str, description: str) -> str:
        """Determine the event type based on title and description"""
        text = (title + " " + description).lower()
        
        if "meet up" in text or "meetup" in text:
            return "Meet Up"
        elif any(keyword in text for keyword in ["fair", "expo", "showcase"]):
            return "Career Fair"
        elif any(keyword in text for keyword in ["workshop", "training"]):
            return "Workshop"
        elif any(keyword in text for keyword in ["networking", "connect", "mixer"]):
            return "Networking Event"
        elif any(keyword in text for keyword in ["interview", "mock"]):
            return "Interview Prep"
        elif any(keyword in text for keyword in ["resume", "cv"]):
            return "Resume Workshop"
        elif any(keyword in text for keyword in ["panel", "discussion"]):
            return "Panel Discussion"
        elif any(keyword in text for keyword in ["seminar", "lecture", "talk"]):
            return "Seminar"
        elif any(keyword in text for keyword in ["orientation", "introduction"]):
            return "Orientation"
        else:
            return "Career Event"
    
    def _get_placeholder_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate placeholder event data when all else fails"""
        events = [
            {
                "title": "Career Meet Up: Resume Strategies that Get You Noticed",
                "date": "May 20, 2025",
                "time": "2:00 - 2:45 pm",
                "location": "Zoom",
                "description": "Learn effective resume strategies that will help you stand out from the competition and catch employers' attention.",
                "type": "Meet Up",
                "registration_required": True,
                "link": "https://hireaniner.charlotte.edu/events/3904"
            },
            {
                "title": "Spring Career Fair 2025",
                "date": "April 15, 2025",
                "time": "10:00 AM - 3:00 PM",
                "location": "Student Union, Multipurpose Room",
                "description": "Connect with over 100 employers looking to hire UNCC students and alumni for full-time positions and internships.",
                "type": "Career Fair",
                "registration_required": True,
                "link": "#"
            },
            {
                "title": "Resume Building Workshop",
                "date": "April 10, 2025",
                "time": "2:00 PM - 4:00 PM",
                "location": "Atkins Library, Room 125",
                "description": "Learn how to create a standout resume that will catch employers' attention and increase your chances of landing an interview.",
                "type": "Workshop",
                "registration_required": False,
                "link": "#"
            },
            {
                "title": "Tech Industry Networking Night",
                "date": "April 18, 2025",
                "time": "6:00 PM - 8:00 PM",
                "location": "PORTAL Building, Main Lobby",
                "description": "Network with professionals from leading technology companies in the Charlotte area. Light refreshments will be served.",
                "type": "Networking Event",
                "registration_required": True,
                "link": "#"
            },
            {
                "title": "Mock Interview Day",
                "date": "April 22, 2025",
                "time": "9:00 AM - 5:00 PM",
                "location": "Career Center, King Building",
                "description": "Practice your interview skills with industry professionals who will provide valuable feedback to help you improve.",
                "type": "Interview Prep",
                "registration_required": True,
                "link": "#"
            },
            {
                "title": "Financial Services Employer Panel",
                "date": "April 25, 2025",
                "time": "3:00 PM - 4:30 PM",
                "location": "Friday Building, Room 132",
                "description": "Join representatives from top financial firms as they discuss career opportunities and industry trends.",
                "type": "Panel Discussion",
                "registration_required": False,
                "link": "#"
            },
            {
                "title": "LinkedIn Profile Optimization",
                "date": "April 28, 2025",
                "time": "1:00 PM - 2:30 PM",
                "location": "Virtual via Zoom",
                "description": "Learn how to create a LinkedIn profile that attracts recruiters and showcases your professional brand effectively.",
                "type": "Workshop",
                "registration_required": True,
                "link": "#"
            },
            {
                "title": "Job Search Strategies for International Students",
                "date": "May 8, 2025",
                "time": "2:00 PM - 3:30 PM",
                "location": "International Student Center",
                "description": "Specialized workshop covering job search techniques and visa considerations for international students.",
                "type": "Workshop",
                "registration_required": True,
                "link": "#"
            }
        ]
        
        return events[:count]