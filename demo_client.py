"""
Demo Azure AI Client - Simulates responses when no model is deployed
"""
import time
import random
from typing import Dict, List, Optional
from config import Config

class DemoAzureAIClient:
    """Demo client that simulates Azure AI responses for testing purposes."""
    
    def __init__(self):
        """Initialize demo client."""
        self.config = Config()
        print("🎭 Demo mode activated - Simulating Azure AI responses")
    
    def send_message(self, message: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Simulate AI response for demo purposes.
        
        Args:
            message: User input message
            conversation_history: Previous conversation context
            
        Returns:
            Dict containing simulated AI response
        """
        # Simulate processing time
        time.sleep(random.uniform(1, 2))
        
        # Demo responses based on message content
        demo_responses = [
            "Hello! I'm a demo AI assistant. Your Azure AI Foundry project needs a model deployment to work with real AI responses.",
            "This is a simulated response! Once you deploy a model in Azure AI Foundry, I'll provide real AI-powered answers.",
            "Great question! I'm currently in demo mode. Deploy a model like GPT-4 in your Azure AI Foundry project to unlock my full capabilities.",
            "I understand you're testing the chat interface. Everything looks good! Just deploy a model in Azure AI Foundry to get started.",
            "This chat interface is working perfectly! The only missing piece is deploying a model in your Azure AI Foundry project.",
        ]
        
        # Choose response based on message content or randomly
        if "hello" in message.lower() or "hi" in message.lower():
            response = "Hello! I'm your demo AI assistant. Deploy a model in Azure AI Foundry to unlock real AI conversations!"
        elif "deploy" in message.lower() or "model" in message.lower():
            response = "To deploy a model: Go to ai.azure.com → Your Project → Deployments → Create New Deployment → Choose a model like GPT-4"
        elif "test" in message.lower():
            response = "Test successful! ✅ Your Streamlit chat interface is working perfectly. Just need that model deployment!"
        elif len(message) > 50:
            response = "I can see you're writing detailed messages! Once you deploy a model, I'll be able to provide thoughtful, detailed responses to match."
        else:
            response = random.choice(demo_responses)
        
        return {
            "content": f"🎭 **DEMO MODE**: {response}\n\n💡 **Next Step**: Deploy a model in Azure AI Foundry to enable real AI responses!",
            "model": "demo-model",
            "usage": {"total_tokens": len(message) + len(response)},
            "success": True
        }