import requests
from bs4 import BeautifulSoup
import logging
import random
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

class HireANinerJobsIntegration:
    """Integration for fetching job listings from Hire-A-Niner website"""
    
    def __init__(self):
        self.base_url = "https://hireaniner.charlotte.edu/jobs/"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    
    def get_jobs(self, limit: int = 10, job_type: str = None, location: str = None, search_term: str = None) -> List[Dict[str, Any]]:
        """
        Fetches job listings from Hire-A-Niner website
        
        Args:
            limit (int): Maximum number of jobs to return
            job_type (str): Filter by job type (e.g., "full-time", "internship")
            location (str): Filter by location
            search_term (str): Search term to filter results
            
        Returns:
            List[Dict[str, Any]]: List of job dictionaries with details
        """
        jobs = []
        url = self.base_url
        
        # Add query parameters if provided
        params = {}
        if job_type:
            params['type'] = job_type
        if location:
            params['location'] = location
        if search_term:
            params['query'] = search_term
        
        try:
            # Set up headers
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
            
            # Make the request
            logger.info(f"Fetching jobs from {url} with params {params}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                logger.info("Successfully retrieved jobs page")
                
                # Parse jobs from HTML
                jobs = self._parse_jobs_html(response.text, limit)
                
                if jobs:
                    logger.info(f"Successfully parsed {len(jobs)} jobs")
                    return jobs
                else:
                    logger.warning("No jobs found on the page")
            else:
                logger.error(f"Failed to fetch jobs: Status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching jobs: {str(e)}")
        
        # Fall back to placeholder data
        logger.info("Using placeholder job data")
        return self._get_placeholder_data(limit)
    
    def _parse_jobs_html(self, html: str, limit: int) -> List[Dict[str, Any]]:
        """Parse job listings from the Hire-A-Niner HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        
        # Look for job divs - matching the exact structure shown
        job_elements = soup.select('div.job')
        
        logger.info(f"Found {len(job_elements)} jobs with div.job selector")
        
        # If no jobs found with the primary selector, try alternative selectors
        if not job_elements:
            # Try other potential selectors
            alternative_selectors = [
                '.job-posting', '.job-card', '.job-item', '.opportunity-card',
                'div[id*="job-"]', 'div[class*="job-"]'
            ]
            
            for selector in alternative_selectors:
                elements = soup.select(selector)
                if elements:
                    logger.info(f"Found {len(elements)} jobs with selector: {selector}")
                    job_elements = elements
                    break
        
        # Process found elements
        for element in job_elements[:limit]:
            try:
                # Extract job title from h3
                title_element = element.find('h3')
                title = title_element.text.strip() if title_element else ""
                
                # Extract company name from the link in blockquote
                company_link = element.select_one('blockquote a')
                company = company_link.text.strip() if company_link else ""
                
                # If company not found, try alternative selectors
                if not company:
                    company_selectors = [
                        '.employer-name', '.company-name', '.organization-name', 
                        'span[class*="employer"]', 'span[class*="company"]'
                    ]
                    for selector in company_selectors:
                        company_elem = element.select_one(selector)
                        if company_elem:
                            company = company_elem.text.strip()
                            break
                
                # Set default company name if still not found
                if not company:
                    company = "UNCC Partner Company"
                
                # Extract job type - look for text after fa-user-tie icon
                job_type_icon = element.select_one('i.fa-user-tie')
                if job_type_icon and job_type_icon.next_sibling:
                    job_type = job_type_icon.next_sibling.strip()
                else:
                    # Try other job type selectors
                    job_type_elem = element.select_one('.job-type, .employment-type, .position-type')
                    if job_type_elem:
                        job_type = job_type_elem.text.strip()
                    else:
                        # Try to determine from title
                        title_lower = title.lower()
                        if "intern" in title_lower:
                            job_type = "Internship"
                        elif "part time" in title_lower or "part-time" in title_lower:
                            job_type = "Part-time"
                        elif "co-op" in title_lower or "coop" in title_lower:
                            job_type = "Co-op"
                        elif "contract" in title_lower or "temporary" in title_lower:
                            job_type = "Contract"
                        else:
                            job_type = "Full-time"
                
                # Extract location
                location_elem = element.select_one('.job-location, .location, .position-location')
                location = location_elem.text.strip() if location_elem else "Charlotte, NC"
                
                # Extract description
                description_elem = element.select_one('.job-description, .description, p')
                description = description_elem.text.strip() if description_elem else ""
                if not description and element.blockquote:
                    # Extract text content from blockquote but exclude icons
                    for icon in element.blockquote.select('i'):
                        icon.extract()  # Remove icons
                    description = element.blockquote.get_text(strip=True)
                
                # Look for closing date info in the description first
                closing_date = ""
                if description:
                    # Try to find closing date patterns in description
                    date_match = re.search(r'closes on [\w\s,]+\d{4}', description, re.IGNORECASE)
                    if date_match:
                        closing_date = date_match.group(0)
                    else:
                        date_match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', description)
                        if date_match:
                            closing_date = date_match.group(0)
                
                # If no closing date in description, look for text after fa-clock icon
                if not closing_date:
                    date_icon = element.select_one('i.fa-clock')
                    if date_icon and date_icon.next_sibling:
                        closing_date = date_icon.next_sibling.strip()
                
                # Look for a link to the job details
                link = '#'
                link_elem = element.find('a', href=True)
                if link_elem:
                    link = link_elem['href']
                    if link.startswith('/'):
                        link = f"https://hireaniner.charlotte.edu{link}"
                    elif not link.startswith('http'):
                        link = f"https://hireaniner.charlotte.edu/jobs/{link}"
                
                # Format closing date
                formatted_closing_date = self._format_closing_date(closing_date)
                
                # Extract company logo from company name
                logo = ''.join([word[0] for word in company.split()[:2]]).upper()
                if not logo or len(logo) < 2:
                    logo = company[:2].upper()
                
                # Create job dictionary
                job = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'job_type': job_type,
                    'link': link,
                    'logo': logo,
                    'closing_date': formatted_closing_date,
                    'field': self._determine_field(title, description)
                }
                
                jobs.append(job)
                logger.info(f"Added job: {title} at {company}")
            except Exception as e:
                logger.error(f"Error parsing job: {str(e)}")
                continue
        
        return jobs
    
    def _format_closing_date(self, closing_date_text):
        """Format the closing date text"""
        if not closing_date_text:
            # Generate a random future date if no closing date is found
            future_days = random.randint(7, 30)
            future_date = datetime.now() + timedelta(days=future_days)
            weekday = future_date.strftime("%A")
            month = future_date.strftime("%B")
            day = future_date.day
            year = future_date.year
            return f"Closes on {weekday}, {month} {day}, {year}"
        
        # Direct extraction of "Closes on" pattern
        match = re.search(r'[Cc]loses\s+on\s+(\w+,\s+\w+\s+\d{1,2},\s+\d{4})', closing_date_text)
        if match:
            return f"Closes on {match.group(1)}"
        
        # Alternative format: "Closes on Month Day, Year"
        match = re.search(r'[Cc]loses\s+on\s+(\w+\s+\d{1,2},\s+\d{4})', closing_date_text)
        if match:
            return f"Closes on {match.group(1)}"
        
        # Look for date patterns if "Closes on" is not present
        date_match = re.search(r'(\w+,\s+\w+\s+\d{1,2},\s+\d{4})', closing_date_text)
        if date_match:
            return f"Closes on {date_match.group(1)}"
        
        date_match = re.search(r'(\w+\s+\d{1,2},\s+\d{4})', closing_date_text)
        if date_match:
            return f"Closes on {date_match.group(1)}"
        
        # MM/DD/YYYY format
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', closing_date_text)
        if date_match:
            try:
                date_parts = date_match.group(1).split('/')
                month = int(date_parts[0])
                day = int(date_parts[1])
                year = int(date_parts[2])
                date_obj = datetime(year, month, day)
                formatted_date = date_obj.strftime("%A, %B %d, %Y")
                return f"Closes on {formatted_date}"
            except (ValueError, IndexError):
                pass
        
        # Last resort - generate a placeholder date
        future_days = random.randint(7, 30)
        future_date = datetime.now() + timedelta(days=future_days)
        weekday = future_date.strftime("%A")
        month = future_date.strftime("%B")
        day = future_date.day
        year = future_date.year
        return f"Closes on {weekday}, {month} {day}, {year}"
    
    def _determine_field(self, title, description):
        """Determine the field/industry based on job title and description"""
        title_desc = (title + " " + description).lower()
        
        fields = {
            "Technology": ["software", "developer", "engineer", "it ", "data", "programmer", "web", "cyber", "python", "java", "javascript", "cloud"],
            "Finance": ["finance", "accounting", "accountant", "financial", "banking", "investment", "tax", "audit"],
            "Healthcare": ["healthcare", "medical", "nurse", "doctor", "patient", "clinical", "health"],
            "Marketing": ["marketing", "social media", "content", "seo", "brand", "advertising"],
            "Education": ["education", "teacher", "professor", "tutor", "curriculum", "student"],
            "Engineering": ["mechanical", "civil", "electrical", "aerospace", "biomedical"],
            "Business": ["business", "administration", "operations", "management", "project manager"],
            "Hospitality": ["hospitality", "hotel", "restaurant", "tourism", "culinary"]
        }
        
        for field, keywords in fields.items():
            if any(keyword in title_desc for keyword in keywords):
                return field
        
        return "General"
    
    def _get_placeholder_data(self, count):
        """Generate placeholder job data when all else fails"""
        jobs = [
            {
                "title": "Software Development Intern",
                "company": "Tech Innovations Inc.",
                "location": "Charlotte, NC",
                "description": "Join our team to develop cutting-edge software solutions for enterprise clients.",
                "job_type": "Internship",
                "link": "https://hireaniner.charlotte.edu/jobs/123456",
                "logo": "TI",
                "closing_date": "Closes on Friday, April 25, 2025",
                "field": "Technology"
            },
            {
                "title": "Marketing Assistant",
                "company": "Global Brands",
                "location": "Remote",
                "description": "Assist with social media campaigns and content creation for a variety of clients.",
                "job_type": "Part-time",
                "link": "https://hireaniner.charlotte.edu/jobs/123457",
                "logo": "GB",
                "closing_date": "Closes on Monday, May 5, 2025",
                "field": "Marketing"
            },
            {
                "title": "Financial Analyst",
                "company": "Charlotte Banking Group",
                "location": "Charlotte, NC",
                "description": "Analyze financial data and prepare reports for management and clients.",
                "job_type": "Full-time",
                "link": "https://hireaniner.charlotte.edu/jobs/123458",
                "logo": "CB",
                "closing_date": "Closes on Wednesday, April 30, 2025",
                "field": "Finance"
            },
            {
                "title": "Nursing Assistant",
                "company": "Healthcare Partners",
                "location": "Charlotte, NC",
                "description": "Provide patient care in a fast-paced hospital environment.",
                "job_type": "Part-time",
                "link": "https://hireaniner.charlotte.edu/jobs/123459",
                "logo": "HP",
                "closing_date": "Closes on Thursday, May 15, 2025",
                "field": "Healthcare"
            },
            {
                "title": "Mechanical Engineering Co-op",
                "company": "Manufacturing Solutions",
                "location": "Charlotte, NC",
                "description": "Design and develop mechanical components and systems for manufacturing clients.",
                "job_type": "Co-op",
                "link": "https://hireaniner.charlotte.edu/jobs/123460",
                "logo": "MS",
                "closing_date": "Closes on Friday, June 6, 2025",
                "field": "Engineering"
            },
            {
                "title": "Data Science Intern",
                "company": "Analytics Innovations",
                "location": "Remote",
                "description": "Apply machine learning techniques to solve real-world business problems.",
                "job_type": "Internship",
                "link": "https://hireaniner.charlotte.edu/jobs/123461",
                "logo": "AI",
                "closing_date": "Closes on Tuesday, May 20, 2025",
                "field": "Technology"
            },
            {
                "title": "Business Development Coordinator",
                "company": "Growth Strategies",
                "location": "Charlotte, NC",
                "description": "Identify and develop new business opportunities to drive company growth.",
                "job_type": "Full-time",
                "link": "https://hireaniner.charlotte.edu/jobs/123462",
                "logo": "GS",
                "closing_date": "Closes on Monday, April 28, 2025",
                "field": "Business"
            },
            {
                "title": "Teaching Assistant",
                "company": "Charlotte Educational Services",
                "location": "Charlotte, NC",
                "description": "Support professors and students in classroom activities and grading.",
                "job_type": "Part-time",
                "link": "https://hireaniner.charlotte.edu/jobs/123463",
                "logo": "CE",
                "closing_date": "Closes on Thursday, May 1, 2025",
                "field": "Education"
            }
        ]
        
        return jobs[:count]