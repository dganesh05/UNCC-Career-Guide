import os
import logging
from typing import Optional
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
            except Exception as e:
                CareerAdvisorChatbot._initialization_error = str(e)
                logger.error(f"Failed to initialize Mistral AI client: {str(e)}", exc_info=True)
                raise
    
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
    
    def get_response(self, message: str, context: Optional[str] = None) -> str:
        """Get response from Mistral AI"""
        try:
            messages = []
            
            # Add context if provided
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
                model="mistral-small",  # You can change to mistral-medium or mistral-large if needed
                messages=messages
            )
            
            return response.messages[-1].content
            
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