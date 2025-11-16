"""
RAG (Retrieval-Augmented Generation) service using Azure AI Search and Azure OpenAI.
Implements the classic RAG pattern for enhanced AI responses grounded in your data.
"""
import logging
from typing import Dict, List, Optional, Any
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    """
    RAG service that retrieves relevant documents from Azure AI Search 
    and uses them to enhance AI responses.
    """
    
    def __init__(self):
        """Initialize the RAG service with Azure AI Search client."""
        self.config = Config()
        
        if not self.config.ENABLE_RAG:
            logger.info("RAG is disabled in configuration")
            self.search_client = None
            return
        
        try:
            # Initialize Azure AI Search client
            # Following Azure best practices: prefer managed identity in production
            if self.config.AZURE_SEARCH_KEY:
                credential = AzureKeyCredential(self.config.AZURE_SEARCH_KEY)
                logger.info("Using API key authentication for Azure AI Search")
            else:
                credential = DefaultAzureCredential()
                logger.info("Using managed identity authentication for Azure AI Search")
            
            self.search_client = SearchClient(
                endpoint=self.config.AZURE_SEARCH_ENDPOINT,
                index_name=self.config.AZURE_SEARCH_INDEX,
                credential=credential
            )
            
            logger.info(f"RAG service initialized with index: {self.config.AZURE_SEARCH_INDEX}")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            self.search_client = None
            raise
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for the query using Azure OpenAI.
        This is required for vector search in hybrid mode.
        """
        try:
            from openai import AzureOpenAI
            
            # Initialize OpenAI client for embeddings
            openai_client = AzureOpenAI(
                api_key=self.config.AZURE_OPENAI_API_KEY,
                api_version="2024-02-01",
                azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT
            )
            
            # Generate embedding using Azure OpenAI text embedding model
            response = openai_client.embeddings.create(
                input=query,
                model="text-embedding-ada-002"  # Standard embedding model
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.warning(f"Failed to generate query embedding: {e}")
            # Return empty list to disable vector search
            return []
    
    def search_documents(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents in Azure AI Search.
        
        Args:
            query: User's search query
            top_k: Number of top results to return (defaults to config value)
            
        Returns:
            List of relevant documents with their content and metadata
        """
        if not self.search_client:
            logger.warning("RAG service not available - returning empty results")
            return []
        
        top_k = top_k or self.config.RAG_TOP_K
        
        try:
            logger.info(f"Searching for: '{query}' (top {top_k} results)")
            
            # Configure search parameters based on search type
            if self.config.RAG_SEARCH_TYPE == "hybrid":
                # True hybrid search: combines full-text and vector search
                try:
                    query_embedding = self._get_query_embedding(query)
                    if query_embedding:  # Only add vector query if embedding generation succeeded
                        search_params = {
                            "search_text": query,  # Full-text search
                            "vector_queries": [{
                                "kind": "vector",  # Required parameter
                                "vector": query_embedding,
                                "k_nearest_neighbors": top_k,
                                "fields": "contentVector"  # Adjust field name based on your index
                            }],
                            "top": top_k,
                            "include_total_count": True,
                            "query_type": "semantic",
                            "semantic_configuration_name": "default"
                        }
                    else:
                        # Fallback to semantic search without vector if embedding fails
                        search_params = {
                            "search_text": query,
                            "top": top_k,
                            "include_total_count": True,
                            "query_type": "semantic",
                            "semantic_configuration_name": "default"
                        }
                    results = self.search_client.search(**search_params)
                    logger.info("Using true hybrid search (full-text + vector + semantic)")
                except Exception as hybrid_error:
                    logger.warning(f"Hybrid search failed: {hybrid_error}")
                    # Fall back to semantic search only
                    try:
                        search_params = {
                            "search_text": query,
                            "top": top_k,
                            "include_total_count": True,
                            "query_type": "semantic",
                            "semantic_configuration_name": "default"
                        }
                        results = self.search_client.search(**search_params)
                        logger.info("Using semantic search (fallback from hybrid)")
                    except Exception as semantic_error:
                        logger.warning(f"Semantic search failed: {semantic_error}")
                        # Final fallback to simple search
                        search_params = {
                            "search_text": query,
                            "top": top_k,
                            "include_total_count": True
                        }
                        results = self.search_client.search(**search_params)
                        logger.info("Using simple search (final fallback)")
            elif self.config.RAG_SEARCH_TYPE == "semantic":
                # Semantic search only
                try:
                    search_params = {
                        "search_text": query,
                        "top": top_k,
                        "include_total_count": True,
                        "query_type": "semantic",
                        "semantic_configuration_name": "default"
                    }
                    results = self.search_client.search(**search_params)
                    logger.info("Using semantic search")
                except Exception as semantic_error:
                    logger.warning(f"Semantic search failed: {semantic_error}")
                    # Fall back to simple search
                    search_params = {
                        "search_text": query,
                        "top": top_k,
                        "include_total_count": True
                    }
                    results = self.search_client.search(**search_params)
                    logger.info("Using simple search (fallback from semantic)")
            else:
                # Use simple search
                search_params = {
                    "search_text": query,
                    "top": top_k,
                    "include_total_count": True
                }
                results = self.search_client.search(**search_params)
                logger.info("Using simple search")
            
            # Process and format results
            documents = []
            for result in results:
                doc = {
                    "content": self._extract_content(result),
                    "score": getattr(result, '@search.score', 0),
                    "metadata": self._extract_metadata(result)
                }
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def _extract_content(self, search_result: Dict[str, Any]) -> str:
        """
        Extract main content from search result.
        Customize this based on your index schema.
        """
        # First check for common content fields
        content_fields = ['content', 'text', 'body', 'description', 'summary']
        
        for field in content_fields:
            if field in search_result and search_result[field]:
                return str(search_result[field])
        
        # Check for your specific index fields (product catalog)
        if 'chunk' in search_result and search_result['chunk']:
            content_parts = []
            
            # Add title if available
            if 'title' in search_result and search_result['title']:
                content_parts.append(f"Title: {search_result['title']}")
            
            # Add main chunk content
            content_parts.append(str(search_result['chunk']))
            
            return " | ".join(content_parts)
        
        # Fallback: return all text fields concatenated
        text_content = []
        for key, value in search_result.items():
            if isinstance(value, str) and not key.startswith('@'):
                text_content.append(f"{key}: {value}")
        
        return " | ".join(text_content) if text_content else "No content available"
    
    def _extract_metadata(self, search_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from search result.
        Customize this based on your index schema.
        """
        # Common metadata fields
        metadata_fields = ['title', 'source', 'url', 'filename', 'category', 'tags', 'date']
        
        metadata = {}
        for field in metadata_fields:
            if field in search_result and search_result[field]:
                metadata[field] = search_result[field]
        
        # Add search-specific metadata
        if '@search.score' in search_result:
            metadata['search_score'] = search_result['@search.score']
        
        return metadata
    
    def create_context_prompt(self, documents: List[Dict[str, Any]], user_query: str) -> str:
        """
        Create a context-enriched prompt for the LLM using retrieved documents.
        
        Args:
            documents: List of retrieved documents
            user_query: Original user query
            
        Returns:
            Enhanced prompt with context
        """
        if not documents:
            return f"User query: {user_query}"
        
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc['content'][:2000]  # Increased limit to capture more content
            source = doc.get('metadata', {}).get('source', f'Document {i}')
            context_parts.append(f"[Source {i}: {source}]\n{content}\n")
        
        context = "\n".join(context_parts)
        
        # Create enhanced prompt
        enhanced_prompt = f"""You are a helpful AI assistant. Use the following context information to answer the user's question. If the context doesn't contain relevant information, say so and provide a general response.

CONTEXT:
{context}

USER QUESTION: {user_query}

Instructions:
- Base your answer primarily on the provided context
- If you reference specific information, mention the source
- If the context is insufficient, acknowledge this and provide what help you can
- Be conversational and helpful"""

        return enhanced_prompt
    
    def is_available(self) -> bool:
        """Check if RAG service is available and properly configured."""
        return self.search_client is not None and self.config.ENABLE_RAG