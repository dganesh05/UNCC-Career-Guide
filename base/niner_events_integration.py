import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import logging
import os
import time
import json
import traceback

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
            logger.info("=" * 50)
            logger.info("Starting event fetch from Hire-A-Niner")
            
            # Create a debug directory if it doesn't exist
            debug_dir = os.path.join(os.getcwd(), 'debug_logs')
            os.makedirs(debug_dir, exist_ok=True)
            
            # Construct the URL (add event type filter if provided)
            url = self.base_url
            if event_type:
                url += f"?type={event_type}"
            
            logger.info(f"Fetching events from URL: {url}")
            
            # Set up headers for the request
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
            }
            
            logger.info("Making HTTP request...")
            start_time = time.time()
            
            # Make the request to the events page with increased timeout
            response = requests.get(url, headers=headers, timeout=45)
            
            end_time = time.time()
            logger.info(f"Request completed in {end_time-start_time:.2f} seconds")
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response size: {len(response.text)} bytes")
            
            # Save response to debug file
            debug_file = os.path.join(debug_dir, 'hireaniner_response.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f"Saved response HTML to {debug_file}")
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the events from the HTML
                logger.info("Parsing events from HTML...")
                events = self._parse_events_html(response.text, count)
                
                if events:
                    logger.info(f"Successfully parsed {len(events)} events")
                    # Log event details
                    for i, event in enumerate(events):
                        logger.info(f"Event {i+1}: {event.get('title')} on {event.get('date')}")
                    
                    # Save events to debug file
                    debug_file = os.path.join(debug_dir, 'parsed_events.json')
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        json.dump(events, f, indent=4)
                    logger.info(f"Saved parsed events to {debug_file}")
                    
                    return events
                else:
                    logger.warning("No events found in the HTML")
            else:
                logger.error(f"Failed to fetch events: Status code {response.status_code}")
                logger.error(f"Response content snippet: {response.text[:500]}...")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching events: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching events: {str(e)}")
            logger.error(traceback.format_exc())
        
        # Fall back to placeholder data
        logger.info("Using placeholder event data")
        return self._get_placeholder_data(count)
    
    def _parse_events_html(self, html, count):
        """Parse events from the Hire-A-Niner HTML"""
        logger.info("Starting HTML parsing")
        soup = BeautifulSoup(html, 'html.parser')
        events = []
        
        # Try multiple selector patterns to find event panels
        selector_patterns = [
            'div.event.list.event-panel',
            'div.event-panel',
            'div[class*="event-panel"]',
            'div[class*="event list"]',
            'div.event',
            '.event-card',
            '.events-list > div',
            '.event-container',
            '.event-item'
        ]
        
        found_panels = []
        for pattern in selector_patterns:
            panels = soup.select(pattern)
            logger.info(f"Selector '{pattern}' found {len(panels)} elements")
            if panels:
                found_panels.extend(panels)
        
        # Remove duplicates (in case different selectors matched the same elements)
        unique_panels = []
        for panel in found_panels:
            if panel not in unique_panels:
                unique_panels.append(panel)
        
        logger.info(f"Found {len(unique_panels)} unique event panels")
        
        # If no panels found with our selectors, try a more general approach
        if not unique_panels:
            logger.info("No event panels found with specific selectors, trying general approach")
            
            # Look for h3 elements with links - these are likely event titles
            title_elements = soup.select('h3 a')
            logger.info(f"Found {len(title_elements)} h3 elements with links")
            
            # For each title element, try to find the parent container
            for title_element in title_elements[:count]:
                parent = title_element
                for _ in range(5):  # Go up to 5 levels up to find container
                    parent = parent.parent
                    if parent is None:
                        break
                    if parent.name == 'div':
                        unique_panels.append(parent)
                        break
        
        # Process the found panels to extract event details
        for panel in unique_panels[:count]:
            try:
                # First look for title as h3 > a
                title_element = panel.select_one('h3 a')
                if title_element:
                    title = title_element.get_text(strip=True)
                else:
                    # Try any h3
                    title_element = panel.select_one('h3')
                    if title_element:
                        title = title_element.get_text(strip=True)
                    else:
                        # Try looking for any prominent text that might be a title
                        for tag in panel.find_all(['strong', 'b', 'h4', 'h5', 'h6']):
                            if tag.get_text(strip=True):
                                title = tag.get_text(strip=True)
                                break
                        else:
                            # If we still can't find a title, use the first text block
                            texts = [t.strip() for t in panel.stripped_strings]
                            title = texts[0] if texts else "Unnamed Event"
                
                logger.info(f"Found event title: {title}")
                
                # Extract date/time information
                date_text = ""
                
                # First try to find date by using the clock icon
                clock_icon = panel.select_one('i.far.fa-clock, i[class*="clock"]')
                if clock_icon:
                    # Try to get text after the icon
                    for sibling in clock_icon.next_siblings:
                        if isinstance(sibling, str) and sibling.strip():
                            date_text = sibling.strip()
                            break
                
                # If no date from clock icon, try matching date patterns in the entire text
                if not date_text:
                    all_text = panel.get_text()
                    # Try various date formats
                    date_patterns = [
                        # Thursday, April 3, 2025
                        r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
                        # April 3, 2025
                        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
                        # 04/03/2025
                        r'\d{1,2}/\d{1,2}/\d{4}',
                        # Any time pattern like 10:00 AM
                        r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)'
                    ]
                    
                    for pattern in date_patterns:
                        matches = re.findall(pattern, all_text)
                        if matches:
                            if isinstance(matches[0], tuple):
                                # If regex captured groups, join them
                                date_text = ' '.join(matches[0])
                            else:
                                date_text = matches[0]
                            break
                
                logger.info(f"Found date text: {date_text}")
                
                # Extract location information
                location = ""
                
                # Try to find location by using the map marker icon
                location_icon = panel.select_one('i.fas.fa-map-marker-alt, i[class*="map-marker"]')
                if location_icon:
                    # Try to get text after the icon
                    for sibling in location_icon.next_siblings:
                        if isinstance(sibling, str) and sibling.strip():
                            location = sibling.strip()
                            break
                
                # If no location from marker icon, try looking for location patterns
                if not location:
                    all_text = panel.get_text()
                    location_patterns = [
                        r'at\s+([A-Za-z\s]+Building)',
                        r'in\s+([A-Za-z\s]+Room)',
                        r'Location:\s+([^\n]+)',
                        r'Venue:\s+([^\n]+)'
                    ]
                    
                    for pattern in location_patterns:
                        match = re.search(pattern, all_text)
                        if match:
                            location = match.group(1).strip()
                            break
                
                logger.info(f"Found location: {location}")
                
                # Extract a description (if available)
                description = "See event details for more information."
                desc_element = panel.select_one('p, div[class*="desc"], div[class*="content"]')
                if desc_element and desc_element.get_text(strip=True):
                    # Make sure we're not getting the title or date again
                    desc_text = desc_element.get_text(strip=True)
                    if desc_text != title and not re.search(r'\d{1,2}:\d{2}', desc_text):
                        description = desc_text
                        if len(description) > 150:
                            description = description[:147] + "..."
                
                # Parse date and time
                date, time = self._extract_date_time(date_text, panel.get_text())
                
                # Create event object
                event = {
                    "title": title,
                    "description": description,
                    "date": date,
                    "time": time,
                    "location": location if location else "See event details"
                }
                
                events.append(event)
                logger.info(f"Successfully added event: {title}")
            except Exception as e:
                logger.error(f"Error parsing event: {str(e)}")
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"Finished parsing, found {len(events)} events")
        
        # If no events could be parsed, use placeholder data
        if not events:
            logger.warning("No events could be parsed, will use placeholder data")
            return self._get_placeholder_data(count)
        
        return events
    
    def _extract_date_time(self, date_text, full_text):
        """Extract and format date and time from text"""
        logger.info(f"Extracting date/time from: '{date_text}'")
        
        # Default values
        date = "TBD" 
        time = "TBD"
        
        # Try to extract date from date_text or full_text
        text_to_check = date_text if date_text else full_text
        
        # Try various date patterns
        date_patterns = [
            # Thursday, April 3, 2025
            (r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
             lambda m: f"{m.group(2)} {m.group(3)}, {m.group(4)}"),
            
            # April 3, 2025
            (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
             lambda m: f"{m.group(1)} {m.group(2)}, {m.group(3)}"),
            
            # 04/03/2025
            (r'(\d{1,2})/(\d{1,2})/(\d{4})',
             lambda m: self._format_numeric_date(m.group(1), m.group(2), m.group(3)))
        ]
        
        for pattern, formatter in date_patterns:
            match = re.search(pattern, text_to_check)
            if match:
                date = formatter(match)
                break
        
        # Try to extract time
        time_patterns = [
            # 10:00 AM - 2:00 PM
            (r'(\d{1,2}:\d{2})\s*(AM|PM|am|pm)?\s*(?:-|to)\s*(\d{1,2}:\d{2})\s*(AM|PM|am|pm)?',
             lambda m: self._format_time_range(m.group(1), m.group(2), m.group(3), m.group(4))),
            
            # 10:00 AM
            (r'(\d{1,2}:\d{2})\s*(AM|PM|am|pm)',
             lambda m: f"{m.group(1)} {m.group(2).upper() if m.group(2) else ''}"),
            
            # 10 AM - 2 PM
            (r'(\d{1,2})\s*(AM|PM|am|pm)\s*(?:-|to)\s*(\d{1,2})\s*(AM|PM|am|pm)',
             lambda m: f"{m.group(1)} {m.group(2).upper()} - {m.group(3)} {m.group(4).upper()}")
        ]
        
        for pattern, formatter in time_patterns:
            match = re.search(pattern, text_to_check)
            if match:
                time = formatter(match)
                break
        
        logger.info(f"Extracted date: '{date}', time: '{time}'")
        return date, time
    
    def _format_numeric_date(self, month, day, year):
        """Format numeric date (MM/DD/YYYY) as Month DD, YYYY"""
        try:
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime("%B %d, %Y")
        except ValueError:
            return f"{month}/{day}/{year}"
    
    def _format_time_range(self, start_time, start_ampm, end_time, end_ampm):
        """Format time range in a consistent way"""
        # Handle missing AM/PM indicators
        if start_ampm is None and end_ampm is not None:
            start_ampm = end_ampm
        elif end_ampm is None and start_ampm is not None:
            end_ampm = start_ampm
        
        # Ensure AM/PM is uppercase
        if start_ampm:
            start_ampm = start_ampm.upper()
        if end_ampm:
            end_ampm = end_ampm.upper()
        
        return f"{start_time} {start_ampm or ''} - {end_time} {end_ampm or ''}".strip()
    
    def _get_placeholder_data(self, count):
        """Generate placeholder event data when all else fails"""
        logger.info("Generating placeholder event data")
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