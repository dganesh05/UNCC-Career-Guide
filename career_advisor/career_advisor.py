import os
import logging
import markdown
from typing import Optional, Dict
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from decouple import config

logger = logging.getLogger(__name__)

class CareerAdvisorChatbot:
    """Career advisor chatbot using Mistral AI"""
    
    _instance = None
    _is_initialized = False
    _initialization_error = None
    
    def __init__(self):
        """Initialize the Mistral AI client"""
        if not CareerAdvisorChatbot._is_initialized:
            try:
                self._initialize_client()
                self._setup_career_context()
            except Exception as e:
                CareerAdvisorChatbot._initialization_error = str(e)
                logger.error(f"Failed to initialize Mistral AI client: {str(e)}", exc_info=True)
                raise

    def _setup_career_context(self):
        """Setup the career advisor context and guidelines"""
        self.career_context = """You are CareerBot, a comprehensive AI career assistant specializing in technology and software engineering careers. 
        You provide detailed, actionable advice while maintaining a friendly and encouraging tone. Your expertise covers:

        1. Resume Writing & Optimization
        - Format and structure best practices for tech resumes
        - Creating impactful bullet points using the STAR method
        - Tailoring resumes for specific roles and companies
        - Technical skills presentation and keywords optimization
        - ATS (Applicant Tracking System) optimization tips

        2. Cover Letter Crafting
        - Structure and formatting guidelines
        - Personalizing content for specific companies
        - Highlighting relevant experiences and skills
        - Maintaining professional yet engaging tone
        - Addressing specific job requirements

        3. LinkedIn Profile Optimization
        - Creating compelling headlines and summaries
        - Writing effective experience descriptions
        - Keyword optimization for recruiter searches
        - Building a professional online presence
        - Networking strategies and connection requests

        4. Job Search Strategies
        - Identifying target companies and roles
        - Using job boards and company websites effectively
        - Organizing and tracking applications
        - Timing and follow-up strategies
        - Salary research and negotiation

        5. Professional Networking
        - Building and maintaining professional relationships
        - Crafting networking messages and emails
        - Following up after meetings or events
        - Utilizing LinkedIn and other platforms effectively
        - Industry event participation strategies

        6. Interview Preparation
        - Technical interview preparation
        - Behavioral question strategies (STAR method)
        - Company research and preparation
        - Common interview questions and answers
        - Follow-up and thank you notes

        7. Elevator Pitch Development
        - Crafting concise personal introductions
        - Adapting pitch for different audiences
        - Highlighting unique value propositions
        - Professional story-telling techniques

        8. Professional Communication
        - Email writing and etiquette
        - Follow-up messages
        - Meeting requests
        - Thank you notes
        - Networking messages

        Guidelines for Interaction:
        - Provide specific, actionable advice with examples
        - Break down complex topics into manageable steps
        - Use a friendly, encouraging tone
        - Ask clarifying questions when needed
        - Share relevant industry best practices
        - Provide context for your recommendations
        - Use emojis occasionally to maintain a friendly tone
        - Focus on practical, implementable solutions

        Remember to:
        - Be encouraging and supportive
        - Maintain professionalism while being approachable
        - Provide specific examples and templates when helpful
        - Guide users through complex topics step-by-step
        - Suggest follow-up questions or areas to explore
        - Share industry insights and trends when relevant

        Always maintain a balance between being helpful and professional while keeping responses concise and actionable."""

    def _initialize_client(self):
        """Initialize the Mistral AI client with API key"""
        try:
            api_key = config('MISTRAL_API_KEY')
            if not api_key:
                raise ValueError("MISTRAL_API_KEY not found in environment variables")
            
            self.client = MistralClient(api_key=api_key)
            
            # Test the client with a simple message
            test_response = self.client.chat(
                model="mistral-tiny",
                messages=[{"role": "user", "content": "Test"}]
            )
            logger.info("Mistral AI client initialized successfully")
            CareerAdvisorChatbot._is_initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing Mistral AI client: {str(e)}", exc_info=True)
            raise

    def _format_response(self, content: str) -> Dict[str, str]:
        """Format the response content into raw and HTML versions"""
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(content)
            
            return {
                'raw': content,
                'html': html_content
            }
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}", exc_info=True)
            return {
                'raw': content,
                'html': f"<p>{content}</p>"
            }
    
    def get_response(self, message: str, context: Optional[str] = None) -> Dict[str, str]:
        """Get response from Mistral AI"""
        try:
            messages = []
            
            # Always include the career advisor context
            messages.append(
                ChatMessage(role="system", content=self.career_context)
            )
            
            # Add additional context if provided
            if context:
                messages.append(
                    ChatMessage(role="system", content=context)
                )
            
            # Add user message
            messages.append(
                ChatMessage(role="user", content=message)
            )
            
            # Get response from Mistral AI
            response = self.client.chat(
                model="mistral-small",
                messages=messages
            )
            
            content = response.messages[-1].content
            return self._format_response(content)
            
        except Exception as e:
            logger.error(f"Error getting response from Mistral AI: {str(e)}", exc_info=True)
            raise
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # No specific cleanup needed for Mistral AI
            pass
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", exc_info=True)