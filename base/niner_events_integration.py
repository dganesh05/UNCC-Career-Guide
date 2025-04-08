# File: base/niner_events_integration.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)

class NinerCareerEventsIntegration:
    """Integration for fetching events from Hire-A-Niner website"""
    
    def __init__(self):
        self.base_url = "https://hireaniner.charlotte.edu/events/"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    
    def get_upcoming_events(self, count=2, event_type=None):
        """
        Get upcoming career events from Hire-A-Niner
        
        Args:
            count: Number of events to fetch
            event_type: Type of event to filter (optional)
            
        Returns:
            List of upcoming events
        """
        try:
            # Construct the URL (add event type filter if provided)
            url = self.base_url
            if event_type:
                url += f"?type={event_type}"
            
            # Set up headers for the request
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
            
            # Make the request to the events page
            logger.info(f"Fetching events from {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            # Check if the request was successful
            if response.status_code == 200:
                logger.info("Successfully retrieved events page")
                
                # Parse the events from the HTML
                events = self._parse_events_html(response.text, count)
                
                if events:
                    logger.info(f"Successfully parsed {len(events)} events")
                    return events
                else:
                    logger.warning("No events found on the page")
            else:
                logger.error(f"Failed to fetch events: Status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching events: {str(e)}")
        
        # Fall back to placeholder data
        logger.info("Using placeholder event data")
        return self._get_placeholder_data(count)
    
    def _parse_events_html(self, html, count):
        """Parse events from the Hire-A-Niner HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        events = []
        
        # Look for event listings on the page
        # We'll try multiple selector patterns that might match event containers
        event_elements = []
        
        # Try various selectors based on common patterns for event listings
        selectors = [
            'div.event-card', 'div.event-box', 'div.event-container', 
            'div.job-card', 'article.event', 'div.card', 
            'tr.event-row', 'div[id*="event"]', 'div[class*="event"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} events with selector: {selector}")
                event_elements.extend(elements)
                if len(event_elements) >= count:
                    break
        
        # If no elements found with specific selectors, try a more generic approach
        if not event_elements:
            logger.info("No events found with specific selectors, trying generic approach")
            
            # Look for any div containing dates or event-like text
            for div in soup.find_all('div'):
                text = div.get_text().lower()
                if (any(keyword in text for keyword in ['event', 'workshop', 'fair', 'session']) and 
                    (re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', text) or 
                     re.search(r'\d{1,2}/\d{1,2}', text))):
                    event_elements.append(div)
            
            logger.info(f"Found {len(event_elements)} events with generic approach")
        
        # Process found elements
        for element in event_elements[:count]:
            try:
                # Extract event details using various strategies
                
                # Strategy 1: Look for structured elements with specific classes
                title = self._extract_text(element, ['h1', 'h2', 'h3', 'h4', '.event-title', '.title', 'a[href*="events"]', 'a strong', 'b', 'strong'])
                date_text = self._extract_text(element, ['.date', '.event-date', 'time', '.datetime', 'span[class*="date"]'])
                location = self._extract_text(element, ['.location', '.event-location', '.venue', 'span[class*="location"]'])
                description = self._extract_text(element, ['p', '.description', '.details', 'div[class*="desc"]'])
                
                # Strategy 2: If specific elements not found, look at the full text
                if not title or not date_text:
                    full_text = element.get_text(strip=True)
                    
                    # If no title found, try to extract from full text
                    if not title:
                        # Look for patterns that might be event titles - usually capitalized text not preceded by a date
                        title_match = re.search(r'([A-Z][a-zA-Z0-9\s:&\'-]+?)(?:\s*\(|\s*-|\s*\||\s*•|\s*on\s)', full_text)
                        if title_match:
                            title = title_match.group(1).strip()
                        else:
                            # Fall back to the first line of text
                            lines = full_text.split('\n')
                            if lines:
                                title = lines[0].strip()
                    
                    # If no date found, try to extract from full text
                    if not date_text:
                        # Look for date patterns
                        date_match = re.search(r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}', full_text, re.IGNORECASE)
                        if date_match:
                            date_text = date_match.group(0)
                        else:
                            # Try numeric date format (MM/DD/YYYY)
                            date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', full_text)
                            if date_match:
                                date_text = date_match.group(0)
                
                # Clean and limit description length
                if description:
                    # Remove extra whitespace
                    description = re.sub(r'\s+', ' ', description).strip()
                    # Limit length
                    description = description[:150] + "..." if len(description) > 150 else description
                else:
                    description = "No description available"
                
                # Extract and format date and time
                date, time = self._extract_date_time(date_text, element.get_text())
                
                # If we couldn't extract a title, skip this event
                if not title:
                    logger.warning("Skipping event with no title")
                    continue
                
                # Create event object
                event = {
                    "title": title,
                    "description": description,
                    "date": date,
                    "time": time,
                    "location": location if location else "See event details"
                }
                
                events.append(event)
                logger.info(f"Added event: {title}")
            except Exception as e:
                logger.error(f"Error parsing event: {str(e)}")
                continue
        
        return events
    
    def _extract_text(self, element, selectors):
        """Extract text from an element using multiple possible selectors"""
        for selector in selectors:
            try:
                selected = element.select(selector)
                if selected:
                    return selected[0].get_text(strip=True)
                
                # Try direct find if select doesn't work
                if '.' in selector:  # It's a class
                    class_name = selector[1:]  # Remove the leading dot
                    found = element.find(class_=class_name)
                    if found:
                        return found.get_text(strip=True)
            except Exception:
                pass
        
        return ""
    
    def _extract_date_time(self, date_text, full_text):
        """Extract and format date and time from text"""
        # Default values
        date = "TBD" 
        time = "TBD"
        
        # Try to extract date from date_text
        if date_text:
            # Try to find month/day/year pattern
            date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', date_text)
            if date_match:
                month, day, year = date_match.groups()
                if len(year) == 2:
                    year = f"20{year}"  # Assume 20xx for 2-digit years
                try:
                    date_obj = datetime(int(year), int(month), int(day))
                    date = date_obj.strftime("%B %d, %Y")
                except ValueError:
                    pass
            
            # Try to find month name pattern
            if date == "TBD":
                date_match = re.search(r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})', date_text, re.IGNORECASE)
                if date_match:
                    month, day, year = date_match.groups()
                    date = f"{month} {day}, {year}"
        
        # If date is still TBD, try with full text
        if date == "TBD" and full_text:
            # Try month/day/year pattern
            date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', full_text)
            if date_match:
                month, day, year = date_match.groups()
                if len(year) == 2:
                    year = f"20{year}"
                try:
                    date_obj = datetime(int(year), int(month), int(day))
                    date = date_obj.strftime("%B %d, %Y")
                except ValueError:
                    pass
            
            # Try month name pattern
            if date == "TBD":
                date_match = re.search(r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})', full_text, re.IGNORECASE)
                if date_match:
                    month, day, year = date_match.groups()
                    date = f"{month} {day}, {year}"
        
        # Try to extract time
        time_match = re.search(r'(\d{1,2}:\d{2})\s*(AM|PM|am|pm)?\s*(?:-|to)\s*(\d{1,2}:\d{2})\s*(AM|PM|am|pm)?', full_text)
        if time_match:
            start_time, start_ampm, end_time, end_ampm = time_match.groups()
            
            # Handle missing AM/PM
            if start_ampm is None and end_ampm is not None:
                start_ampm = end_ampm
            elif end_ampm is None and start_ampm is not None:
                end_ampm = start_ampm
            
            if start_ampm:
                start_ampm = start_ampm.upper()
            if end_ampm:
                end_ampm = end_ampm.upper()
            
            time = f"{start_time} {start_ampm or ''} - {end_time} {end_ampm or ''}".strip()
        elif not time_match:
            # Try other time formats (e.g., "5 PM - 8 PM")
            time_match = re.search(r'(\d{1,2})\s*(AM|PM|am|pm)\s*(?:-|to)\s*(\d{1,2})\s*(AM|PM|am|pm)', full_text)
            if time_match:
                start_hour, start_ampm, end_hour, end_ampm = time_match.groups()
                time = f"{start_hour} {start_ampm.upper()} - {end_hour} {end_ampm.upper()}"
        
        return date, time
    
    def _get_placeholder_data(self, count):
        """Generate placeholder event data when all else fails"""
        events = [
            {
                "title": "Spring Career Fair 2025",
                "description": "Meet with over 100 employers looking to hire UNCC students and alumni.",
                "date": "March 18, 2025",
                "time": "10:00 AM - 3:00 PM",
                "location": "Student Union, Multipurpose Room"
            },
            {
                "title": "Resume Workshop",
                "description": "Get personalized feedback on your resume from career counselors and industry professionals.",
                "date": "March 25, 2025",
                "time": "2:00 PM - 4:00 PM",
                "location": "Atkins Library, Room 125"
            },
            {
                "title": "Tech Industry Panel",
                "description": "Learn from professionals in the tech industry about career paths and opportunities.",
                "date": "April 5, 2025",
                "time": "1:00 PM - 3:00 PM",
                "location": "College of Computing, Room 340"
            }
        ]
        
        return events[:count]