"""
AI Chat Assistant - Streamlit Application
A modern chat interface that integrates with Azure AI Foundry for intelligent conversations.
"""
import streamlit as st
import time
from typing import List, Dict
from azure_ai_client import AzureAIClient
from config import Config
import logging

# Configure page settings
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_custom_css():
    """Apply custom CSS for modern chat interface styling."""
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    
    /* Chat message containers */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        display: flex;
        align-items: flex-start;
        animation: fadeIn 0.3s ease-in;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
        flex-direction: row-reverse;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #333;
        margin-right: 2rem;
        border-left: 4px solid #007acc;
    }
    
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        margin: 0 0.5rem;
        flex-shrink: 0;
    }
    
    .user-avatar {
        background: rgba(255, 255, 255, 0.2);
    }
    
    .assistant-avatar {
        background: #007acc;
        color: white;
    }
    
    .message-content {
        flex: 1;
        line-height: 1.5;
    }
    
    /* Input area styling */
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #007acc;
        box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: transform 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Header styling */
    .chat-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 1rem;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #007acc;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
    }
    
    /* Error message styling */
    .error-message {
        background: #ffebee;
        color: #c62828;
        border: 1px solid #ffcdd2;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Success message styling */
    .success-message {
        background: #e8f5e8;
        color: #2e7d32;
        border: 1px solid #c8e6c9;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "azure_client" not in st.session_state:
        try:
            from azure_ai_client import AzureAIClient
            st.session_state.azure_client = AzureAIClient()
            st.session_state.demo_mode = False
            logger.info("Azure AI client initialized successfully")
        except Exception as e:
            # Fall back to demo mode if real client fails
            from demo_client import DemoAzureAIClient
            st.session_state.azure_client = DemoAzureAIClient()
            st.session_state.demo_mode = True
            st.session_state.client_error = str(e)
            logger.warning(f"Using demo mode due to: {e}")

def display_message(role: str, content: str, avatar: str = None):
    """Display a chat message with proper styling."""
    message_class = "user-message" if role == "user" else "assistant-message"
    avatar_class = "user-avatar" if role == "user" else "assistant-avatar"
    avatar_icon = "👤" if role == "user" else "🤖"
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message-avatar {avatar_class}">
            {avatar_icon}
        </div>
        <div class="message-content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_typing_indicator():
    """Display typing indicator animation."""
    st.markdown("""
    <div class="chat-message assistant-message">
        <div class="message-avatar assistant-avatar">🤖</div>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_error_message(message: str):
    """Display error message with proper styling."""
    st.markdown(f"""
    <div class="error-message">
        <strong>⚠️ Error:</strong> {message}
    </div>
    """, unsafe_allow_html=True)

def display_success_message(message: str):
    """Display success message with proper styling."""
    st.markdown(f"""
    <div class="success-message">
        <strong>✅ Success:</strong> {message}
    </div>
    """, unsafe_allow_html=True)

def get_conversation_history() -> List[Dict]:
    """Get formatted conversation history for API calls."""
    history = []
    for msg in st.session_state.messages:
        history.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    return history

def send_message_to_ai(user_message: str) -> str:
    """Send message to Azure AI and return response."""
    try:
        if not st.session_state.azure_client:
            raise Exception("Azure AI client is not initialized. Please check your configuration.")
        
        # Get conversation history
        conversation_history = get_conversation_history()
        
        # Send message to Azure AI (works for both real and demo client)
        response = st.session_state.azure_client.send_message(
            message=user_message,
            conversation_history=conversation_history
        )
        
        if response.get("success", True):
            return response.get("content", "I apologize, but I couldn't generate a response.")
        else:
            error_msg = response.get("error", "Unknown error occurred")
            raise Exception(f"AI service error: {error_msg}")
            
    except Exception as e:
        logger.error(f"Error sending message to AI: {e}")
        # If we're not in demo mode and encounter an error, fall back to demo mode
        if not hasattr(st.session_state, 'demo_mode') or not st.session_state.demo_mode:
            try:
                from demo_client import DemoAzureAIClient
                st.session_state.azure_client = DemoAzureAIClient()
                st.session_state.demo_mode = True
                # Retry with demo client
                response = st.session_state.azure_client.send_message(
                    message=user_message,
                    conversation_history=conversation_history
                )
                return response.get("content", "Demo mode activated!")
            except:
                pass
        
        return f"I apologize, but I encountered an error: {str(e)}"

def clear_conversation():
    """Clear the conversation history."""
    st.session_state.messages = []
    st.rerun()

def main():
    """Main application function."""
    # Apply custom styling
    apply_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # App header with demo mode indicator
    demo_indicator = ""
    if hasattr(st.session_state, 'demo_mode') and st.session_state.demo_mode:
        demo_indicator = "<div style='background: #ff9800; color: white; padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem;'>🎭 DEMO MODE - Deploy a model in Azure AI Foundry for real AI responses</div>"
    
    st.markdown(f"""
    <div class="chat-header">
        <h1>🤖 {Config.APP_TITLE}</h1>
        <p>Powered by Azure AI Foundry</p>
    </div>
    {demo_indicator}
    """, unsafe_allow_html=True)
    
    # Check for client initialization errors
    if hasattr(st.session_state, 'client_error'):
        display_error_message(f"Failed to initialize Azure AI client: {st.session_state.client_error}")
        st.markdown("### 🔧 Configuration Required")
        st.markdown("""
        Please ensure you have:
        1. Created a `.env` file with your Azure AI configuration
        2. Set the correct `AZURE_AI_ENDPOINT` and `AZURE_AI_API_KEY`
        3. Installed all required dependencies: `pip install -r requirements.txt`
        """)
        return
    
    # Sidebar with options
    with st.sidebar:
        st.markdown("### 🎛️ Chat Controls")
        
        if st.button("🗑️ Clear Conversation", type="secondary"):
            clear_conversation()
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        st.markdown(f"**Model Temperature:** {Config.TEMPERATURE}")
        st.markdown(f"**Max Tokens:** {Config.MAX_TOKENS}")
        st.markdown(f"**History Limit:** {Config.CONVERSATION_HISTORY_LIMIT}")
        
        # Show RAG status
        if Config.ENABLE_RAG and hasattr(st.session_state, 'azure_client') and hasattr(st.session_state.azure_client, 'rag_service'):
            if st.session_state.azure_client.rag_service.is_available():
                st.markdown("**RAG:** 🟢 Enabled")
                st.markdown(f"**Search Index:** {Config.AZURE_SEARCH_INDEX}")
            else:
                st.markdown("**RAG:** 🔴 Disabled")
        else:
            st.markdown("**RAG:** 🔴 Disabled")
        
        st.markdown("---")
        st.markdown("### 📊 Session Info")
        
        # Show current mode
        if hasattr(st.session_state, 'demo_mode') and st.session_state.demo_mode:
            st.markdown("**Mode:** 🎭 Demo")
            st.info("Deploy a model in Azure AI Foundry to enable real AI responses!")
        else:
            st.markdown("**Mode:** 🤖 Live AI")
        
        st.markdown(f"**Messages:** {len(st.session_state.messages)}")
        
        if st.session_state.messages:
            total_chars = sum(len(msg["content"]) for msg in st.session_state.messages)
            st.markdown(f"**Total Characters:** {total_chars:,}")
    
    # Chat interface
    st.markdown("### 💬 Conversation")
    
    # Display conversation history
    if st.session_state.messages:
        for message in st.session_state.messages:
            display_message(message["role"], message["content"])
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            👋 Welcome! Start a conversation by typing a message below.
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    # Use st.chat_input for better chat experience
    user_input = st.chat_input("Type your message here...")
    
    # Handle message sending
    if user_input:
        # Add user message to conversation
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.strip()
        })
        
        # Get AI response
        with st.spinner("Thinking..."):
            ai_response = send_message_to_ai(user_input.strip())
        
        # Add AI response to conversation
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Rerun to update the interface
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        Built with ❤️ using Streamlit and Azure AI Foundry
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()