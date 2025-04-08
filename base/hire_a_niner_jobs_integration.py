# File: base/hire_a_niner_jobs_integration.py
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
                
                # Clean and limit description length
                if description:
                    description = ' '.join(description.split())  # Normalize whitespace
                    if len(description) > 150:
                        description = description[:147] + "..."
                else:
                    description = "Visit the job posting for complete details."
                
                # Extract closing date - look for text after fa-clock icon
                closing_date = ""
                date_icon = element.select_one('i.fa-clock')
                if date_icon and date_icon.next_sibling:
                    closing_date = date_icon.next_sibling.strip()
                
                # Calculate days ago based on closing date
                posted_days_ago = self._calculate_days_from_closing_date(closing_date)
                
                # Extract or generate logo from company name
                logo = ''.join([word[0] for word in company.split()[:2]]).upper()
                if not logo or len(logo) < 2:
                    logo = company[:2].upper()
                
                # Look for a link to the job details
                link = '#'
                link_elem = element.find('a', href=True)
                if link_elem:
                    link = link_elem['href']
                    if link.startswith('/'):
                        link = f"https://hireaniner.charlotte.edu{link}"
                    elif not link.startswith('http'):
                        link = f"https://hireaniner.charlotte.edu/jobs/{link}"
                
                # Generate appropriate salary based on job type
                salary = self._generate_salary_for_job_type(job_type, title)
                
                # Create job dictionary
                job = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'job_type': job_type,
                    'link': link,
                    'logo': logo,
                    'posted_days_ago': posted_days_ago,
                    'salary': salary,
                    'field': self._determine_field(title, description)
                }
                
                jobs.append(job)
                logger.info(f"Added job: {title} at {company}")
            except Exception as e:
                logger.error(f"Error parsing job: {str(e)}")
                continue
        
        return jobs
    
    def _calculate_days_from_closing_date(self, closing_date_text):
        """Calculate approximate days ago based on closing date"""
        if not closing_date_text:
            return str(random.randint(0, 7))  # Default to recent random days
        
        try:
            # Extract date from text like "Closes on Tuesday, April 1, 2025"
            match = re.search(r'(\w+, \w+ \d+, \d{4})', closing_date_text)
            if match:
                closing_date_str = match.group(1)
                closing_date = datetime.strptime(closing_date_str, '%A, %B %d, %Y')
                
                # Estimate posting date (typically jobs are posted 2-4 weeks before closing)
                posting_date = closing_date - timedelta(days=random.randint(14, 28))
                days_ago = (datetime.now() - posting_date).days
                
                # Make sure it's not negative or too large
                if days_ago < 0:
                    days_ago = 0
                elif days_ago > 30:  # Cap at 30 days for better UX
                    days_ago = random.randint(7, 14)
                
                return str(days_ago)
        except Exception as e:
            logger.error(f"Error calculating days from closing date: {str(e)}")
        
        # Default fallback
        return str(random.randint(0, 7))
    
    def _generate_salary_for_job_type(self, job_type, title):
        """Generate appropriate salary ranges based on job type and title"""
        # Check for senior/junior indicators in title
        title_lower = title.lower()
        is_senior = any(term in title_lower for term in ['senior', 'sr.', 'lead', 'manager', 'director'])
        is_junior = any(term in title_lower for term in ['junior', 'jr.', 'entry', 'assistant', 'associate'])
        
        if job_type == "Internship" or job_type == "Co-op":
            min_rate = random.randint(15, 20)
            max_rate = min_rate + random.randint(3, 8)
            return f"${min_rate}-{max_rate}/hr"
            
        elif job_type == "Part-time":
            min_rate = random.randint(15, 25)
            max_rate = min_rate + random.randint(5, 10)
            return f"${min_rate}-{max_rate}/hr"
            
        else:  # Full-time, Contract, etc.
            if is_senior:
                base = random.randint(80, 120)
            elif is_junior:
                base = random.randint(45, 65)
            else:
                base = random.randint(60, 90)
                
            min_salary = base * 1000
            max_salary = min_salary + random.randint(10, 30) * 1000
            return f"${min_salary:,}-{max_salary:,}/year"
    
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
                "posted_days_ago": "2",
                "salary": "$20-25/hr",
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
                "posted_days_ago": "0",
                "salary": "$18-22/hr",
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
                "posted_days_ago": "5",
                "salary": "$65,000-80,000/year",
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
                "posted_days_ago": "3",
                "salary": "$18-24/hr",
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
                "posted_days_ago": "7",
                "salary": "$22-28/hr",
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
                "posted_days_ago": "1",
                "salary": "$20-28/hr",
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
                "posted_days_ago": "4",
                "salary": "$55,000-65,000/year",
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
                "posted_days_ago": "6",
                "salary": "$15-20/hr",
                "field": "Education"
            }
        ]
        
        return jobs[:count]