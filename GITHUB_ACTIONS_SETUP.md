# GitHub Actions Deployment Setup

## 📋 Prerequisites for GitHub Actions

To enable automated deployments with the updated parameterized workflow, you'll need to set up the following:

### 1. Azure Service Principal

Create a service principal for GitHub Actions authentication:

#### **Step 1.1: Get your subscription ID**
```bash
az account show --query 'id' --output tsv
```

#### **Step 1.2: Create the service principal**
```bash
# Replace {subscription-id} with your actual subscription ID from Step 1.1
az ad sp create-for-rbac --name "ai-chat-app-github" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/rg-chat-app \
  --sdk-auth
```

#### **Step 1.3: Save the output**
This will output JSON credentials that look like:
```json
{
  "clientId": "xxxxxxxxx",
  "clientSecret": "xxxxxxxxx",
  "subscriptionId": "xxxxxxxxx",
  "tenantId": "xxxxxxxxx"
}
```

**⚠️ Important**: Copy this entire JSON output - you'll need it for the GitHub secret in the next step.

### 2. GitHub Repository Secrets

Add the following **SECRETS** to your GitHub repository:
Go to: **Settings** → **Secrets and variables** → **Actions** → **Secrets**

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AZURE_CREDENTIALS` | JSON output from service principal creation | Azure authentication credentials |
| `AZURE_OPENAI_ENDPOINT` | `https://your-endpoint.cognitiveservices.azure.com/` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | `your-api-key-here` | Azure OpenAI API key |
| `AZURE_SEARCH_ENDPOINT` | `https://your-search.search.windows.net` | Azure AI Search endpoint |
| `AZURE_SEARCH_KEY` | `your-search-admin-key` | Azure AI Search admin key |

### 3. GitHub Repository Variables

Add the following **VARIABLES** to your GitHub repository:
Go to: **Settings** → **Secrets and variables** → **Actions** → **Variables**

#### Infrastructure Variables
| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `AZURE_WEBAPP_NAME` | `ai-chat-app` | Azure Web App name |
| `AZURE_RESOURCE_GROUP` | `rg-chat-app` | Azure Resource Group name |
| `AZURE_CONTAINER_REGISTRY` | `aichatapp` | Azure Container Registry name |
| `CONTAINER_IMAGE_NAME` | `ai-chat-app` | Docker container image name |

#### Application Configuration Variables
| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o-mini` | Azure OpenAI deployment name |
| `MODEL_NAME` | `gpt-4o-mini` | OpenAI model name |
| `AZURE_SEARCH_INDEX` | `your-index-name` | Azure AI Search index name |
| `ENABLE_RAG` | `true` | Enable RAG functionality |
| `RAG_TOP_K` | `5` | Number of search results to retrieve |
| `RAG_SEARCH_TYPE` | `hybrid` | Search type (hybrid, vector, text) |
| `APP_TITLE` | `AI Chat Assistant` | Application title |
| `MAX_TOKENS` | `1000` | Maximum tokens for AI responses |
| `TEMPERATURE` | `0.7` | AI model temperature |
| `CONVERSATION_HISTORY_LIMIT` | `50` | Max conversation history |
| `REQUEST_TIMEOUT` | `30` | Request timeout in seconds |
| `MAX_RETRIES` | `3` | Maximum retry attempts |

### 4. Setting Up Secrets and Variables

#### Using GitHub Web Interface:

1. **Go to your repository**: `https://github.com/vamsi-devulapally/ai-chat-app`
2. **Navigate to Settings** → **Secrets and variables** → **Actions**
3. **Add Secrets**: Click "New repository secret" for each secret above
4. **Add Variables**: Click "Variables" tab, then "New repository variable" for each variable above

#### Using GitHub CLI (Alternative):

```bash
# Set secrets
gh secret set AZURE_CREDENTIALS --body "$(cat azure-credentials.json)"
gh secret set AZURE_OPENAI_ENDPOINT --body "your-endpoint-here"
gh secret set AZURE_OPENAI_API_KEY --body "your-api-key-here"
gh secret set AZURE_SEARCH_ENDPOINT --body "your-search-endpoint"
gh secret set AZURE_SEARCH_KEY --body "your-search-key"

# Set variables
gh variable set AZURE_WEBAPP_NAME --body "ai-chat-app"
gh variable set AZURE_RESOURCE_GROUP --body "rg-chat-app"
gh variable set AZURE_CONTAINER_REGISTRY --body "aichatapp"
gh variable set CONTAINER_IMAGE_NAME --body "ai-chat-app"
gh variable set AZURE_OPENAI_DEPLOYMENT --body "gpt-4o-mini"
gh variable set MODEL_NAME --body "gpt-4o-mini"
gh variable set AZURE_SEARCH_INDEX --body "your-index-name"
gh variable set ENABLE_RAG --body "true"
gh variable set APP_TITLE --body "AI Chat Assistant"
```

### 5. Updated Workflow Features

The updated parameterized workflow now includes:

- ✅ **Fully parameterized configuration** - All settings from GitHub secrets/variables
- ✅ **Environment-specific deployments** - Manual environment selection
- ✅ **Secure secret management** - Sensitive data in GitHub secrets
- ✅ **Configurable variables** - Non-sensitive settings as variables
- ✅ **Default fallbacks** - Sensible defaults if variables not set
- ✅ **Application settings deployment** - Updates Azure App Service settings
- ✅ **Deployment verification** - Confirms settings are applied

### 6. Environment Variables Security

**Store as Secrets (Sensitive Data):**
- API Keys (`AZURE_OPENAI_API_KEY`, `AZURE_SEARCH_KEY`)
- Endpoints with tokens (`AZURE_OPENAI_ENDPOINT`, `AZURE_SEARCH_ENDPOINT`)
- Azure credentials (`AZURE_CREDENTIALS`)

**Store as Variables (Configuration Data):**
- Resource names, model settings, application configuration
- Non-sensitive settings like timeouts, limits, feature flags

### 7. Workflow Triggers

The workflow will run on:
- **Push to main branch**: Automatic deployment to production
- **Manual trigger**: Use "Run workflow" button with environment selection
  - Options: production, staging, development

### 8. Multi-Environment Support

The workflow now supports different environments:
```yaml
workflow_dispatch:
  inputs:
    environment:
      description: 'Environment to deploy to'
      required: true
      default: 'production'
      type: choice
      options:
      - production
      - staging  
      - development
```

### 9. Deployment Process

When triggered, the workflow will:

1. **Checkout code** from the repository
2. **Login to Azure** using the service principal
3. **Build Docker image** directly in Azure Container Registry
4. **Set application settings** from GitHub secrets/variables
5. **Update Web App** with the new container image (tagged with commit SHA)
6. **Restart Web App** to apply changes
7. **Verify deployment** status and app settings

### 10. Deployment URL

Your deployed application: **https://ai-chat-app-dgfyguhvc6bfgzar.southindia-01.azurewebsites.net**

## 🔧 Manual Deployment Commands

If you prefer manual deployment, use these commands:

```bash
# Build and push to ACR
az acr build --registry aichatapp --image ai-chat-app:latest .

# Set application settings manually
az webapp config appsettings set --name ai-chat-app --resource-group rg-chat-app \
  --settings AZURE_OPENAI_ENDPOINT="your-endpoint" \
             AZURE_OPENAI_API_KEY="your-key" \
             AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"

# Update Web App with new image
az webapp config container set \
  --name ai-chat-app \
  --resource-group rg-chat-app \
  --docker-custom-image-name aichatapp.azurecr.io/ai-chat-app:latest \
  --docker-registry-server-url https://aichatapp.azurecr.io

# Restart Web App
az webapp restart --name ai-chat-app --resource-group rg-chat-app
```
