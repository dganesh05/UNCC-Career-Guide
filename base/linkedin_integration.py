import requests
import json
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import random

class LinkedInJobsIntegration:
    """
    Class for fetching job opportunities from LinkedIn
    
    This integration provides two approaches:
    1. Using a third-party API service (recommended for production)
    2. Using a custom web scraper (fallback option)
    """
    
    def __init__(self, api_key=None):
        """Initialize the LinkedIn Jobs Integration"""
        self.api_key = api_key or os.environ.get('LINKEDIN_API_KEY')
        self.base_url = "https://api.scrapingdog.com/linkedin"  # Example third-party API
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    
    def get_featured_opportunities(self, count=3, keywords=None, location="Charlotte, NC"):
        """
        Get featured job opportunities from LinkedIn
        
        Args:
            count: Number of jobs to fetch
            keywords: Search keywords (e.g., "data science", "software engineer")
            location: Job location (e.g., "Charlotte, NC")
            
        Returns:
            List of job opportunities
        """
        # Try the API approach first
        if self.api_key:
            try:
                return self._fetch_with_api(count, keywords, location)
            except Exception as e:
                print(f"API error: {e}. Falling back to scraper.")
        
        # Fall back to scraper approach
        try:
            return self._fetch_with_scraper(count, keywords, location)
        except Exception as e:
            print(f"Scraper error: {e}. Returning placeholder data.")
            # Return placeholder data as a last resort
            return self._get_placeholder_data(count)
    
    def _fetch_with_api(self, count, keywords, location):
        """Fetch job data using a third-party API service"""
        params = {
            "api_key": self.api_key,
            "count": count
        }
        
        if keywords:
            params["keywords"] = keywords
        
        if location:
            params["location"] = location
        
        # Make request to the API
        response = requests.get(f"{self.base_url}/jobs", params=params)
        
        if response.status_code == 200:
            return self._process_api_response(response.json(), count)
        else:
            raise Exception(f"API returned status code {response.status_code}")
    
    def _process_api_response(self, data, count):
        """Process API response data into our standard format"""
        jobs = []
        
        for job_data in data.get("jobs", [])[:count]:
            # Extract company name and create logo placeholder
            company = job_data.get("company", "Unknown Company")
            logo = company[0:2] if company else "UN"
            
            # Format salary information
            salary = self._format_salary(job_data.get("salary", {}))
            
            # Calculate days ago
            posted_date = job_data.get("postedAt", "")
            days_ago = self._calculate_days_ago(posted_date)
            
            # Create job object
            job = {
                "title": job_data.get("title", "Unknown Position"),
                "company": company,
                "location": job_data.get("location", "Unknown Location"),
                "salary": salary,
                "description": job_data.get("description", "")[:150] + "...",
                "posted_days_ago": days_ago,
                "job_type": job_data.get("jobType", "Full-time"),
                "field": job_data.get("industry", "General"),
                "logo": logo
            }
            
            jobs.append(job)
        
        return jobs
    
    def _fetch_with_scraper(self, count, keywords, location):
        """Fetch job data using a custom web scraper (fallback approach)"""
        # Note: This is a simplified example and should be expanded for production use
        # In a real implementation, you would handle pagination, more robust parsing, etc.
        
        # Construct search URL
        search_query = f"{keywords} {location}".strip().replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}"
        
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # Make request to LinkedIn
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return self._parse_linkedin_html(response.text, count)
        else:
            raise Exception(f"Scraper returned status code {response.status_code}")
    
    def _parse_linkedin_html(self, html, count):
        """Parse LinkedIn HTML to extract job data"""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        
        # Find job cards
        job_cards = soup.select('.job-search-card')[:count]
        
        for card in job_cards:
            # Extract job details
            title_elem = card.select_one('.job-search-card__title')
            company_elem = card.select_one('.job-search-card__company-name')
            location_elem = card.select_one('.job-search-card__location')
            posted_elem = card.select_one('.job-search-card__listdate')
            
            title = title_elem.text.strip() if title_elem else "Unknown Position"
            company = company_elem.text.strip() if company_elem else "Unknown Company"
            location = location_elem.text.strip() if location_elem else "Unknown Location"
            
            # Create logo placeholder from company initials
            logo = ''.join([word[0] for word in company.split()[:2]]) if company else "UN"
            
            # Calculate days ago from posted date
            posted_text = posted_elem.get('datetime') if posted_elem else ""
            days_ago = self._calculate_days_ago(posted_text)
            
            # Generate a random salary range (for demo purposes)
            salary = self._generate_random_salary()
            
            # Job type and field (these would need to be extracted from the job details page in a real implementation)
            job_type = "Full-time"
            field = "General"
            
            # Create job object
            job = {
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "description": "Click to view job details...",
                "posted_days_ago": days_ago,
                "job_type": job_type,
                "field": field,
                "logo": logo
            }
            
            jobs.append(job)
        
        return jobs
    
    def _get_placeholder_data(self, count):
        """Generate placeholder job data when all else fails"""
        jobs = [
            {
                "title": "Software Engineer",
                "company": "Digital Bank",
                "location": "Charlotte, NC",
                "salary": "$80,000-100,000/year",
                "description": "Join our innovative team to develop cutting-edge financial technology solutions.",
                "posted_days_ago": 2,
                "job_type": "Full-time",
                "field": "Computer Science",
                "logo": "DB"
            },
            {
                "title": "Data Analyst",
                "company": "Tech Solutions Inc.",
                "location": "Remote",
                "salary": "$65,000-75,000/year",
                "description": "Analyze customer data to provide insights and recommendations for product improvement.",
                "posted_days_ago": 7,
                "job_type": "Full-time",
                "field": "Data Science",
                "logo": "TS"
            },
            {
                "title": "UX Designer",
                "company": "Creative Agency",
                "location": "Charlotte, NC",
                "salary": "$70,000-85,000/year",
                "description": "Design user interfaces for web and mobile applications with a focus on user experience.",
                "posted_days_ago": 3,
                "job_type": "Full-time",
                "field": "Design",
                "logo": "CA"
            },
            {
                "title": "Marketing Specialist",
                "company": "Global Brands",
                "location": "Charlotte, NC",
                "salary": "$55,000-65,000/year",
                "description": "Develop and implement marketing strategies for consumer product lines.",
                "posted_days_ago": 5,
                "job_type": "Full-time",
                "field": "Marketing",
                "logo": "GB"
            },
            {
                "title": "Project Manager",
                "company": "Construction Partners",
                "location": "Charlotte, NC",
                "salary": "$85,000-95,000/year",
                "description": "Oversee construction projects from planning to completion, ensuring on-time and on-budget delivery.",
                "posted_days_ago": 1,
                "job_type": "Full-time",
                "field": "Construction",
                "logo": "CP"
            }
        ]
        
        return jobs[:count]
    
    def _format_salary(self, salary_data):
        """Format salary information to a readable string"""
        if not salary_data:
            return "Salary not specified"
        
        min_salary = salary_data.get("min", 0)
        max_salary = salary_data.get("max", 0)
        
        if min_salary == 0 and max_salary == 0:
            return "Salary not specified"
        
        if min_salary == 0:
            return f"Up to ${max_salary:,}/year"
        
        if max_salary == 0:
            return f"From ${min_salary:,}/year"
        
        return f"${min_salary:,}-{max_salary:,}/year"
    
    def _calculate_days_ago(self, date_str):
        """Calculate days ago from a date string"""
        if not date_str:
            return random.randint(1, 7)
        
        try:
            # Try to parse LinkedIn date format
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            days_ago = (datetime.now() - date_obj).days
            return max(1, days_ago)  # At least 1 day ago
        except:
            # If parsing fails, return a random recent number
            return random.randint(1, 7)
    
    def _generate_random_salary(self):
        """Generate a random salary range for demo purposes"""
        base_salaries = {
            "entry": (45000, 65000),
            "mid": (65000, 95000),
            "senior": (95000, 140000)
        }
        
        level = random.choice(list(base_salaries.keys()))
        min_salary, max_salary = base_salaries[level]
        
        # Add some randomness
        min_salary = min_salary + random.randint(-5000, 5000)
        max_salary = max_salary + random.randint(-5000, 5000)
        
        # Round to nearest thousand
        min_salary = round(min_salary / 1000) * 1000
        max_salary = round(max_salary / 1000) * 1000
        
        return f"${min_salary:,}-{max_salary:,}/year"


# Usage example
if __name__ == "__main__":
    # Initialize with API key if available
    api_key = "your_api_key_here"  # Replace with your actual API key
    linkedin = LinkedInJobsIntegration(api_key)
    
    # Get featured job opportunities
    jobs = linkedin.get_featured_opportunities(
        count=3,
        keywords="software engineer",
        location="Charlotte, NC"
    )
    
    # Print the results
    print(json.dumps(jobs, indent=2))