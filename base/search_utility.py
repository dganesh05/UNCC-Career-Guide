import re
from django.db.models import Q

class SearchUtility:
    """
    Utility for searching across different types of content
    
    This search utility can search through:
    1. Job opportunities
    2. Career events
    3. Resources
    4. Any other content types added in the future
    """
    
    def __init__(self):
        """Initialize the Search Utility"""
        pass
    
    def search(self, query, data):
        """
        Search for the query in the provided data
        
        Args:
            query: The search query string
            data: Dictionary containing different types of content to search through
                 Expected format: {
                     'opportunities': [...],
                     'events': [...],
                     'resources': [...],
                     'additional_resources': [...]
                 }
        
        Returns:
            Dictionary of search results by type
        """
        if not query:
            return []
        
        # Normalize query
        query = query.lower().strip()
        terms = set(re.findall(r'\w+', query))  # Split into words and remove duplicates
        
        results = []
        
        # Search through opportunities
        opportunities = data.get('opportunities', [])
        for opportunity in opportunities:
            score = self._calculate_match_score(opportunity, terms, 'opportunity')
            if score > 0:
                results.append({
                    'type': 'job',
                    'title': opportunity.get('title', ''),
                    'company': opportunity.get('company', ''),
                    'link': f"/job-board?job={opportunity.get('title', '').replace(' ', '-')}",
                    'score': score
                })
        
        # Search through events
        events = data.get('events', [])
        for event in events:
            score = self._calculate_match_score(event, terms, 'event')
            if score > 0:
                results.append({
                    'type': 'event',
                    'title': event.get('title', ''),
                    'date': event.get('date', ''),
                    'link': f"/events?event={event.get('title', '').replace(' ', '-')}",
                    'score': score
                })
        
        # Search through resources
        resources = data.get('resources', [])
        for resource in resources:
            score = self._calculate_match_score(resource, terms, 'resource')
            if score > 0:
                results.append({
                    'type': 'resource',
                    'title': resource.get('title', ''),
                    'link': resource.get('link', '#'),
                    'score': score
                })
        
        # Search through additional resources
        additional_resources = data.get('additional_resources', [])
        for resource in additional_resources:
            score = self._calculate_match_score(resource, terms, 'resource')
            if score > 0:
                results.append({
                    'type': 'resource',
                    'title': resource.get('title', ''),
                    'link': resource.get('link', '#'),
                    'score': score
                })
        
        # Sort results by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _calculate_match_score(self, item, terms, item_type):
        """
        Calculate a match score for an item against search terms
        
        Higher scores indicate better matches.
        
        Args:
            item: The item to score
            terms: Set of search terms
            item_type: Type of item ('opportunity', 'event', 'resource')
        
        Returns:
            Match score (0 if no match)
        """
        score = 0
        
        if item_type == 'opportunity':
            # Check title (highest weight)
            title = item.get('title', '').lower()
            for term in terms:
                if term in title:
                    score += 3
                    # Exact title match gets bonus
                    if title == term:
                        score += 5
            
            # Check company
            company = item.get('company', '').lower()
            for term in terms:
                if term in company:
                    score += 2
            
            # Check field/keywords
            field = item.get('field', '').lower()
            for term in terms:
                if term in field:
                    score += 2
            
            # Check description
            description = item.get('description', '').lower()
            for term in terms:
                if term in description:
                    score += 1
            
            # Check location
            location = item.get('location', '').lower()
            for term in terms:
                if term in location:
                    score += 1
        
        elif item_type == 'event':
            # Check title (highest weight)
            title = item.get('title', '').lower()
            for term in terms:
                if term in title:
                    score += 3
                    # Exact title match gets bonus
                    if title == term:
                        score += 5
            
            # Check description
            description = item.get('description', '').lower()
            for term in terms:
                if term in description:
                    score += 2
            
            # Check location
            location = item.get('location', '').lower()
            for term in terms:
                if term in location:
                    score += 1
        
        elif item_type == 'resource':
            # Check title (highest weight)
            title = item.get('title', '').lower()
            for term in terms:
                if term in title:
                    score += 3
                    # Exact title match gets bonus
                    if title == term:
                        score += 5
            
            # Check description
            description = item.get('description', '').lower()
            for term in terms:
                if term in description:
                    score += 2
        
        return score
    
    def search_database_models(self, query, models_to_search):
        """
        Search through Django database models
        
        This method can be used when the data is stored in a database.
        
        Args:
            query: The search query string
            models_to_search: List of (model, fields) tuples to search through
                           Each tuple has:
                           - model: A Django model
                           - fields: List of field names to search
        
        Returns:
            Dictionary of search results by model
        """
        results = {}
        
        for model, fields in models_to_search:
            # Build Q object for OR conditions across fields
            q_objects = Q()
            
            for field in fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            # Execute the query
            model_results = model.objects.filter(q_objects)
            results[model.__name__] = model_results
        
        return results


# Usage example
if __name__ == "__main__":
    # Sample data
    data = {
        'opportunities': [
            {
                'title': 'Software Engineer',
                'company': 'Digital Bank',
                'location': 'Charlotte, NC',
                'description': 'Join our team to develop cutting-edge solutions.',
                'field': 'Computer Science'
            },
            {
                'title': 'Data Analyst',
                'company': 'Tech Solutions Inc.',
                'location': 'Remote',
                'description': 'Analyze data to provide insights.',
                'field': 'Data Science'
            }
        ],
        'events': [
            {
                'title': 'Spring Career Fair',
                'description': 'Meet with employers looking to hire UNCC students.',
                'location': 'Student Union'
            },
            {
                'title': 'Resume Workshop',
                'description': 'Get feedback on your resume.',
                'location': 'Atkins Library'
            }
        ],
        'resources': [
            {
                'title': 'Resume Builder',
                'description': 'Create professional resumes.',
                'link': '/resources#resume-builder'
            }
        ]
    }
    
    # Create search utility
    search_utility = SearchUtility()
    
    # Search for a query
    results = search_utility.search('data science', data)
    
    # Print results
    for result in results:
        print(f"Type: {result['type']}, Title: {result['title']}, Score: {result['score']}")