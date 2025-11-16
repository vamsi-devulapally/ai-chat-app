"""
Azure OpenAI client wrapper with RAG (Retrieval-Augmented Generation) support.
Integrates Azure AI Search for enhanced responses grounded in your data.
"""
import logging
from typing import Dict, List, Optional
from openai import AzureOpenAI
from config import Config
from rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureAIClient:
    """
    Azure OpenAI client with RAG (Retrieval-Augmented Generation) support.
    Integrates Azure AI Search for enhanced responses grounded in your data.
    """
    
    def __init__(self):
        """Initialize the Azure OpenAI client and RAG service."""
        self.config = Config()
        self.config.validate()
        
        try:
            # Initialize Azure OpenAI client
            self.client = AzureOpenAI(
                azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT,
                api_key=self.config.AZURE_OPENAI_API_KEY,
                api_version="2024-02-01"
            )
            
            # Initialize RAG service
            self.rag_service = RAGService()
            
            if self.rag_service.is_available():
                logger.info("Azure OpenAI client with RAG initialized successfully")
            else:
                logger.info("Azure OpenAI client initialized (RAG disabled)")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI client: {e}")
            raise
    
    def send_message(self, message: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Send a message to Azure OpenAI and get response.
        
        Args:
            message: User input message
            conversation_history: Previous conversation context
            
        Returns:
            Dict containing the AI response and metadata
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
        
        try:
            # Enhance message with RAG if available
            enhanced_message = self._enhance_with_rag(message) if self.rag_service.is_available() else message
            
            # Prepare messages for the API
            messages = self._prepare_messages(enhanced_message, conversation_history or [])
            
            logger.info(f"Sending request to Azure OpenAI: {len(enhanced_message)} characters")
            
            # Make the API call using the OpenAI SDK
            response = self.client.chat.completions.create(
                model=self.config.AZURE_OPENAI_DEPLOYMENT,  # This is the deployment name
                messages=messages,
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE,
                stream=False
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            logger.info("Successfully received response from Azure OpenAI")
            
            return {
                "content": content.strip() if content else "I apologize, but I couldn't generate a response.",
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error communicating with Azure OpenAI: {e}")
            
            # Provide user-friendly error messages
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                error_msg = "Authentication failed. Please check your API key."
            elif "404" in error_msg or "not found" in error_msg.lower():
                error_msg = f"Model deployment '{self.config.AZURE_OPENAI_DEPLOYMENT}' not found. Please verify your deployment name."
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                error_msg = "Rate limit exceeded. Please wait and try again."
            elif "timeout" in error_msg.lower():
                error_msg = "Request timed out. Please try again."
            
            return {
                "content": f"I apologize, but I encountered an error: {error_msg}",
                "success": False,
                "error": error_msg
            }
    
    def _prepare_messages(self, message: str, conversation_history: List[Dict]) -> List[Dict]:
        """
        Prepare message format for Azure OpenAI API.
        
        Args:
            message: Current user message
            conversation_history: Previous conversation messages
            
        Returns:
            List of formatted messages for the API
        """
        messages = []
        
        # Add system message for context
        messages.append({
            "role": "system",
            "content": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses."
        })
        
        # Add conversation history (limit to prevent token overflow)
        recent_history = conversation_history[-self.config.CONVERSATION_HISTORY_LIMIT:]
        messages.extend(recent_history)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": message
        })
        
        return messages
    
    def _enhance_with_rag(self, message: str) -> str:
        """
        Enhance user message with relevant context from Azure AI Search.
        
        Args:
            message: Original user message
            
        Returns:
            Enhanced message with context or original message if RAG fails
        """
        try:
            # Search for relevant documents
            documents = self.rag_service.search_documents(message)
            
            if documents:
                # Create context-enriched prompt
                enhanced_message = self.rag_service.create_context_prompt(documents, message)
                logger.info(f"Enhanced message with {len(documents)} relevant documents")
                logger.info(f"Enhanced Mesage: {enhanced_message}")
                return enhanced_message
            else:
                logger.info("No relevant documents found, using original message")
                return message
                
        except Exception as e:
            logger.error(f"Error enhancing message with RAG: {e}")
            return message