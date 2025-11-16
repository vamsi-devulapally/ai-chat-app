# 🤖 AI Chat Assistant

A modern, responsive chat interface built with Streamlit that integrates with Azure AI Foundry for intelligent conversations.

## ✨ Features

- 💬 **Interactive Chat Interface**: Modern chat bubbles with user and AI messages
- 🎨 **Beautiful UI**: Custom CSS styling with gradients and animations
- 🔄 **Real-time Responses**: Instant AI responses with typing indicators
- 📝 **Conversation History**: Maintains context throughout the conversation
- ⚙️ **Configurable Settings**: Easily adjustable AI parameters
- 🛡️ **Secure**: Environment-based configuration for API keys
- 🎯 **Error Handling**: Robust error handling with retry mechanisms
- 📱 **Responsive Design**: Works great on desktop and mobile

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Azure AI Foundry project with API access

### Installation

1. **Clone or download this repository**
   ```powershell
   # If you haven't already, navigate to the project directory
   cd c:\chatbot
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file with your Azure AI Foundry credentials:
   
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_DEPLOYMENT=your_deployment_name
   MODEL_NAME=gpt-4o-mini
   
   # Optional: RAG Configuration
   ENABLE_RAG=true
   AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
   AZURE_SEARCH_KEY=your_search_admin_key
   AZURE_SEARCH_INDEX=your_index_name
   ```

4. **Run the application**
   ```powershell
   streamlit run app.py
   ```

5. **Open your browser**
   
   The application will automatically open in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
c:\chatbot\
├── app.py                 # Main Streamlit application
├── azure_ai_client.py     # Azure AI Foundry client wrapper
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (your credentials)
├── .env.example          # Environment template
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint | Required |
| `AZURE_OPENAI_API_KEY` | API key for authentication | Required |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI deployment name | Required |
| `MODEL_NAME` | OpenAI model name | gpt-4o-mini |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint (for RAG) | Optional |
| `AZURE_SEARCH_KEY` | Azure AI Search admin key (for RAG) | Optional |
| `AZURE_SEARCH_INDEX` | Azure AI Search index name (for RAG) | Optional |
| `ENABLE_RAG` | Enable RAG functionality | true |
| `APP_TITLE` | Application title displayed in UI | "AI Chat Assistant" |
| `MAX_TOKENS` | Maximum tokens for AI responses | 1000 |
| `TEMPERATURE` | AI creativity level (0.0-1.0) | 0.7 |
| `CONVERSATION_HISTORY_LIMIT` | Max messages to keep in context | 50 |
| `REQUEST_TIMEOUT` | API request timeout in seconds | 30 |
| `MAX_RETRIES` | Number of retry attempts for failed requests | 3 |

### Customization

You can customize the AI behavior by modifying the values in your `.env` file:

- **Temperature**: Lower values (0.1-0.3) for more focused responses, higher values (0.7-0.9) for more creative responses
- **Max Tokens**: Increase for longer responses, decrease for shorter ones
- **History Limit**: Adjust based on your needs for conversation context

## 🛡️ Security Features

- **Environment Variables**: Sensitive credentials are stored in `.env` file
- **Input Validation**: All user inputs are validated and sanitized
- **Error Handling**: Comprehensive error handling prevents crashes
- **Retry Logic**: Automatic retry with exponential backoff for API failures
- **Connection Pooling**: Efficient HTTP connection management
- **Timeout Protection**: Prevents hanging requests

## 🎯 Usage Tips

1. **Starting Conversations**: Simply type your message and press Enter or click Send
2. **Clearing History**: Use the "Clear Conversation" button in the sidebar
3. **Monitoring**: Check the sidebar for session statistics
4. **Error Recovery**: The app automatically retries failed requests

## 🔧 Troubleshooting

### Common Issues

1. **"Failed to initialize Azure AI client"**
   - Check your `.env` file exists and has the correct credentials
   - Verify your Azure AI Foundry endpoint is accessible
   - Ensure your API key is valid and has the necessary permissions

2. **"Request timed out"**
   - Check your internet connection
   - The Azure AI service might be experiencing high load
   - Try again in a few moments

3. **"Authentication failed"**
   - Verify your API key is correct and hasn't expired
   - Check that your Azure AI Foundry project is active

4. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're using Python 3.8 or higher

### Getting Help

If you encounter issues:

1. Check the Streamlit logs in your terminal
2. Verify your Azure OpenAI service configuration
3. Test your API key with a simple curl request:
   ```powershell
   curl -X POST "https://your-resource-name.openai.azure.com/openai/deployments/your-deployment-name/chat/completions?api-version=2024-02-01" -H "api-key: YOUR_API_KEY" -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"Hello"}]}'
   ```

## 📊 Performance

The application includes several performance optimizations:

- **Connection Pooling**: Reuses HTTP connections for better performance
- **Retry Logic**: Handles transient failures gracefully
- **Conversation Limiting**: Prevents token overflow by limiting history
- **Async Operations**: Non-blocking UI during API calls

## 🔄 Updates

To update the application:

1. Pull the latest changes
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Restart the Streamlit application

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Feel free to customize and extend this application for your specific needs!

---

**Built with ❤️ using Streamlit and Azure AI Foundry**