# Facebook Ads AI Assistant - Comprehensive Guide

## Project Overview

The Facebook Ads AI Assistant is a conversational AI tool that helps users create and manage Facebook ad campaigns through natural language interactions. The assistant is built using OpenAI's GPT-4o model via the Assistants API, Streamlit for the user interface, and the Facebook Marketing API for ad campaign operations.

## Features

1. **Natural Language Understanding**: Users interact with the assistant in conversational language
2. **Post Retrieval**: Fetches and displays Facebook Page posts from specified time periods
3. **Campaign Creation**: Creates ad campaigns with user-specified objectives and budgets
4. **Post Boosting**: Boosts selected posts with targeting and bidding options
5. **Conversational Flow**: Guides users through the ad creation process in a friendly, step-by-step manner

## Architecture and Information Flow

```
┌─────────────────────┐      ┌──────────────────────┐      ┌────────────────────────┐
│                     │      │                      │      │                        │
│    Streamlit UI     │─────►│   OpenAI Assistant   │─────►│   Facebook Graph API   │
│      (app.py)       │◄─────│      (GPT-4o)        │◄─────│                        │
│                     │      │                      │      │                        │
└─────────────────────┘      └──────────────────────┘      └────────────────────────┘
          │                             │                             │
          │                             │                             │
          ▼                             ▼                             ▼
┌─────────────────────┐      ┌──────────────────────┐      ┌────────────────────────┐
│                     │      │                      │      │                        │
│   User Messages     │─────►│    Tool Functions    │─────►│    Facebook Ad         │
│  (Thread History)   │◄─────│    (API Calls)       │◄─────│    Campaign Creation   │
│                     │      │                      │      │                        │
└─────────────────────┘      └──────────────────────┘      └────────────────────────┘
```

### Information Flow

1. The user enters a message in the Streamlit UI (app.py)
2. The message is sent to the OpenAI Assistant API (assistant_client.py)
3. The Assistant processes the message and may call tools:
   - GetPosts: Retrieves posts from Facebook Page (fb_api.py)
   - CreateCampaign: Creates a new ad campaign (fb_api.py)
   - BoostPosts: Boosts selected posts (fb_api.py)
4. The results are returned to the Assistant which formulates a response
5. The response is streamed back to the Streamlit UI
6. The conversation continues with the context maintained in the OpenAI thread

## Technology Stack

1. **Frontend**:
   - Streamlit: Web interface for the conversation
   - Markdown formatting for responses

2. **Backend**:
   - Python 3.8+
   - OpenAI Assistants API: Handles conversation and tool routing
   - Facebook Marketing API: Manages ad campaigns and posts

3. **APIs and SDKs**:
   - OpenAI Python SDK
   - Facebook Business SDK (facebook-business)

4. **Logging and Monitoring**: 
   - Custom logger.py module for structured logging

## Setup Guide

### Prerequisites

1. **Meta/Facebook Requirements**:
   - A Facebook Developer Account
   - A Facebook App with Marketing API enabled
   - A Facebook Page you manage
   - An Ad Account with permissions to create ads
   - Proper Facebook permissions and tokens

2. **OpenAI Requirements**:
   - An OpenAI API key with access to GPT-4o or similar

3. **System Requirements**:
   - Python 3.8+
   - Virtual environment (recommended)

### Facebook/Meta Setup Process

1. **Create a Facebook Developer Account**:
   - Go to [Facebook for Developers](https://developers.facebook.com/)
   - Sign up using your Facebook account
   - Complete the developer account verification if prompted

2. **Create a Facebook App**:
   - From the Developer Dashboard, click "Create App"
   - Choose "Business" as the app type
   - Enter app details (name, contact email)
   - Select "Marketing API" as the product to add to your app

3. **Configure App Settings**:
   - Go to App Settings > Basic
   - Note your App ID and App Secret (you'll need these for configuration)

4. **Set up App Permissions**:
   - Navigate to App Review > Permissions and Features
   - Request the following permissions:
     - `pages_read_engagement` (to fetch posts)
     - `pages_manage_posts` (to manage posts)
     - `ads_management` (to create and manage ads)
     - `ads_read` (to read ad account data)
     - `pages_show_list` (to access list of pages)
     - `business_management` (to manage business assets)
     - `pages_read_user_content` (to read user content on pages)
   - Complete the verification process for these permissions

5. **Generate Access Tokens**:
   - First, generate a short-lived user token:
     - Go to Graph API Explorer tool: https://developers.facebook.com/tools/explorer/
     - Select your app from the dropdown
     - Add the required permissions
     - Click "Generate Access Token"
     - Copy the token (this is your short-lived token)

   - Then, use the provided script to convert to a long-lived page token:
     - Update `.streamlit/secrets.toml` with your short-lived token
     - Run: `python get_long_lived_page_token.py`
     - Copy the output token into your secrets file as FB_ACCESS_TOKEN

6. **Get Your Page ID and Ad Account ID**:
   - Page ID: Go to your Facebook Page > About > Page transparency > Page ID
   - Ad Account ID: Go to Facebook Ads Manager > Account Settings > Account ID (add "act_" prefix if not present)

### Project Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/kartik-syal/facebook-ads-ai-assistant.git
   cd facebook-ads-ai-assistant
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Secrets**:
   Create a `.streamlit/secrets.toml` file with the following:
   ```toml
   OPENAI_API_KEY = "your-openai-key"
   OPENAI_ASSISTANT_ID = "your-assistant-id"  # Will be created in the next step
   FB_APP_ID = "your-facebook-app-id"
   FB_APP_SECRET = "your-facebook-app-secret"
   FB_SHORT_LIVED_USER_TOKEN = "your-short-lived-token"  # For token generation only
   FB_ACCESS_TOKEN = "your-long-lived-page-access-token"
   FB_AD_ACCOUNT_ID = "act_your_ad_account_id"
   FB_PAGE_ID = "your_facebook_page_numeric_id"
   ```

5. **Set up the OpenAI Assistant**:
   ```bash
   python setup_assistant.py
   ```
   This script creates the OpenAI Assistant with the proper tools and instructions.
   Note the Assistant ID and add it to your `.streamlit/secrets.toml` file.

6. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

7. **Access the Application**:
   Open your browser to the provided URL (usually http://localhost:8501)

## Usage Guide

1. **Starting a Conversation**:
   - Enter a natural language query like "Show me posts from last week" or "I want to create a campaign"
   - The assistant will guide you through the process step by step

2. **Post Retrieval**:
   - Request posts using natural language time references
   - View post details including preview text, images, and links
   - Select posts for boosting

3. **Campaign Creation**:
   - Specify campaign name, objective, and budget
   - The assistant will map your goals to Facebook's campaign objectives
   - Review and confirm campaign details

4. **Post Boosting**:
   - Select optimization goals (engagement, reach, traffic, etc.)
   - Set bid amounts and targeting options
   - Confirm boost setup before execution

5. **Starting Over**:
   - Click "Start New Conversation" to reset the conversation thread

## Development Guide

### Key Files and Their Functions

- **app.py**: Main Streamlit application and UI
- **assistant_client.py**: Handles communication with OpenAI Assistant API
- **fb_api.py**: Interface with Facebook Marketing API
- **setup_assistant.py**: Creates/configures the OpenAI Assistant
- **get_long_lived_page_token.py**: Utility to generate long-lived tokens
- **logger.py**: Logging utilities
- **.streamlit/secrets.toml**: Configuration and sensitive credentials

### Adding New Features

1. **Adding New Tools**:
   - Update `setup_assistant.py` with new tool definitions
   - Add corresponding functions in `assistant_client.py` and implement in `fb_api.py`

2. **Enhancing the UI**:
   - Modify `app.py` to add new UI elements or improve user experience

3. **Extending API Capabilities**:
   - Add new functions to `fb_api.py` to interface with additional Facebook Marketing API features

## Troubleshooting

1. **API Authentication Issues**:
   - Check that your tokens are valid and have the correct permissions
   - Ensure your Facebook App is properly configured
   - Verify your token hasn't expired (use get_long_lived_page_token.py to refresh)

2. **Assistant Not Responding**:
   - Check your OpenAI API key and quota
   - Verify that the Assistant ID in your secrets file is correct
   - Check the logs for detailed error messages

3. **Facebook API Errors**:
   - Ensure your Ad Account has proper access and permissions
   - Verify budget values meet Facebook's minimum requirements
   - Check that your Page access token has the required permissions

## Best Practices

1. **Security**:
   - Never commit your `.streamlit/secrets.toml` file to version control
   - Regularly rotate your API keys and tokens
   - Use environment variables for sensitive information in production

2. **Cost Management**:
   - Monitor your OpenAI API usage
   - Set budgets and caps for your Facebook ad campaigns
   - Start with paused campaigns and review before activating

3. **Performance**:
   - Use streaming responses for better user experience
   - Implement proper error handling and logging
   - Cache results where appropriate to minimize API calls

## Additional Resources

1. **API Documentation**:
   - [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview)
   - [Facebook Marketing API](https://developers.facebook.com/docs/marketing-apis/)
   - [Streamlit Documentation](https://docs.streamlit.io/)

2. **SDK References**:
   - [Facebook Business SDK for Python](https://github.com/facebook/facebook-python-business-sdk)
   - [OpenAI Python SDK](https://github.com/openai/openai-python)

## Repository

The official repository for this project is available at: [https://github.com/kartik-syal/facebook-ads-ai-assistant.git](https://github.com/kartik-syal/facebook-ads-ai-assistant.git)