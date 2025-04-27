import os
import logging
import re
import markdown
from typing import Optional, List, Dict, Union
from mistralai.client import MistralClient
from pydantic import BaseModel
from decouple import config

logger = logging.getLogger(__name__)

class Message(BaseModel):
    """Message model for chat requests"""
    role: str
    content: str

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content
        }

class FormattedResponse:
    """Class to handle formatted chatbot responses"""
    def __init__(self, content: str):
        self.raw_content = content
        self.html_content = self._convert_to_html()
    
    def _convert_to_html(self) -> str:
        """Convert markdown content to HTML with proper formatting"""
        try:
            # Pre-process numbered lists to ensure proper formatting
            processed_content = self.raw_content
            
            # Convert numbered lists with bold titles
            processed_content = re.sub(
                r'(\d+)\.\s+\*\*([^:]+):\*\*',
                r'<div class="step-number">\1.</div><div class="step-content"><strong>\2:</strong>',
                processed_content
            )
            
            # Convert regular bold text
            processed_content = re.sub(
                r'\*\*([^*]+)\*\*',
                r'<strong>\1</strong>',
                processed_content
            )
            
            # Convert bullet points
            processed_content = re.sub(
                r'^\*\s+(.+)$',
                r'<li>\1</li>',
                processed_content,
                flags=re.MULTILINE
            )
            
            # Wrap bullet points in ul tags
            if '<li>' in processed_content:
                processed_content = f'<ul>{processed_content}</ul>'
            
            # Add paragraph tags for better spacing
            paragraphs = processed_content.split('\n\n')
            processed_content = ''.join([f'<p>{p}</p>' if not (p.startswith('<ul>') or p.startswith('<div>')) 
                                      else p for p in paragraphs if p.strip()])
            
            return processed_content
        except Exception as e:
            logger.error(f"Error converting content to HTML: {str(e)}")
            return f"<p>{self.raw_content}</p>"

class CareerAdvisorChatbot:
    """Career advisor chatbot using Mistral AI"""
    
    _instance = None
    _client = None
    _is_initialized = False
    _initialization_error = None
    
    def __new__(cls):
        """Ensure singleton pattern"""
        if cls._instance is None:
            cls._instance = super(CareerAdvisorChatbot, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Mistral AI client"""
        if not CareerAdvisorChatbot._is_initialized:
            try:
                self._initialize_client()
            except Exception as e:
                CareerAdvisorChatbot._initialization_error = str(e)
                logger.error(f"Failed to initialize Mistral AI client: {str(e)}", exc_info=True)
                raise
    
    def _initialize_client(self):
        """Initialize the Mistral AI client with API key"""
        try:
            api_key = config('MISTRAL_API_KEY', default='dummy-key-for-development')
            CareerAdvisorChatbot._client = MistralClient(api_key=api_key)
            CareerAdvisorChatbot._is_initialized = True
            logger.info("Successfully initialized Mistral AI client")
        except Exception as e:
            logger.error(f"Failed to initialize Mistral AI client: {str(e)}")
            CareerAdvisorChatbot._client = None
            CareerAdvisorChatbot._is_initialized = False
    
    @property
    def client(self):
        """Get the Mistral AI client instance"""
        if not CareerAdvisorChatbot._client:
            raise ValueError("Mistral AI client not initialized")
        return CareerAdvisorChatbot._client
    
    def get_response(self, message: str, context: Optional[str] = None) -> Dict[str, str]:
        """Get formatted response from Mistral AI"""
        try:
            from mistralai.models.chat_completion import ChatMessage
            messages = []
            
            if context:
                messages.append(ChatMessage(role="system", content=context))
            
            messages.append(ChatMessage(role="user", content=message))
            
            logger.debug(f"Sending messages to Mistral AI: {messages}")
            
            response = self.client.chat(
                model="mistral-small",
                messages=messages
            )
            
            # Extract content from Mistral's response
            if hasattr(response, 'choices') and len(response.choices) > 0:
                raw_content = response.choices[0].message.content
            else:
                logger.error("Unexpected response format from Mistral AI")
                raw_content = "I apologize, but I encountered an error processing your request."
            
            formatted_response = FormattedResponse(raw_content)
            
            # Return a string-based response dictionary
            response_dict = {
                "raw": str(raw_content),
                "html": str(formatted_response.html_content)
            }
            
            return response_dict
            
        except Exception as e:
            logger.error(f"Error getting response from Mistral AI: {str(e)}", exc_info=True)
            raise
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            CareerAdvisorChatbot._client = None
            CareerAdvisorChatbot._is_initialized = False
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", exc_info=True)

    # Fix the _make_chat_request method to avoid recursive call
    def _make_chat_request(self, messages, safe_mode=True):
        formatted_messages = [
            msg if isinstance(msg, dict) else msg.to_dict()  # Use to_dict() instead of dict()
            for msg in messages
        ]
        return self.client.chat(  # Changed from self._make_chat_request to self.client.chat
            model="mistral-small",  # Use consistent model name
            messages=formatted_messages,
            safe_mode=safe_mode
        )