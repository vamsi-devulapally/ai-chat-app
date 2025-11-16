"""
Configuration management for the AI Chat Assistant.
Handles environment variables and application settings securely.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for managing application settings."""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str = os.getenv(
        "AZURE_OPENAI_ENDPOINT", 
        "https://az-ai-foundry-instance.cognitiveservices.azure.com/"
    )
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    
    # Azure AI Search Configuration (for RAG)
    AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    AZURE_SEARCH_KEY: Optional[str] = os.getenv("AZURE_SEARCH_KEY")
    AZURE_SEARCH_INDEX: str = os.getenv("AZURE_SEARCH_INDEX", "")
    
    # RAG Configuration
    ENABLE_RAG: bool = os.getenv("ENABLE_RAG", "true").lower() == "true"
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))  # Number of search results to retrieve
    RAG_SEARCH_TYPE: str = os.getenv("RAG_SEARCH_TYPE", "hybrid")  # "hybrid", "vector", or "text"
    
    # Application Configuration
    APP_TITLE: str = os.getenv("APP_TITLE", "AI Chat Assistant")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    CONVERSATION_HISTORY_LIMIT: int = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "50"))
    
    # Request Configuration
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration settings."""
        if not cls.AZURE_OPENAI_ENDPOINT:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required")
        
        if not cls.AZURE_OPENAI_API_KEY:
            raise ValueError("AZURE_OPENAI_API_KEY is required")
        
        if not cls.AZURE_OPENAI_DEPLOYMENT:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT is required")
        
        # Validate RAG configuration if enabled
        if cls.ENABLE_RAG:
            if not cls.AZURE_SEARCH_ENDPOINT:
                raise ValueError("AZURE_SEARCH_ENDPOINT is required when RAG is enabled")
            if not cls.AZURE_SEARCH_KEY:
                raise ValueError("AZURE_SEARCH_KEY is required when RAG is enabled")
            if not cls.AZURE_SEARCH_INDEX:
                raise ValueError("AZURE_SEARCH_INDEX is required when RAG is enabled")
        
        return True