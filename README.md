# Facebook Ads AI Assistant

This repository implements a multi-agent AI assistant that dynamically sets up Facebook ad campaigns. Using a conversational interface (built with Streamlit) and powered by GPT-4o via LangChain, the assistant is able to:

- Understand natural language queries (e.g., "boost posts from yesterday", "all posts", or specific ranges like "2023-01-01 to 2023-02-01").
- Retrieve posts from a Facebook Page by parsing natural-language date ranges.
- Create Facebook ad campaigns using the Facebook Marketing API.
- Maintain conversation context using LangChain’s message history.

## Project Structure

```
facebook-ads-ai-assistant/
├── .streamlit/
│   └── secrets.toml         # Contains sensitive keys and tokens (do not commit)
├── agent.py                 # Initializes and configures the LangChain agent
├── app.py                   # Main Streamlit application integrating the multi-agent system
├── fb_api.py                # Functions for interacting with the Facebook Marketing API
├── tools.py                 # Tool wrappers for retrieving posts and creating campaigns
├── requirements.txt         # List of project dependencies
└── README.md                # This file
```

## Prerequisites

- **Python 3.8+** is recommended.
- A Facebook Developer account with an app enabled for the Marketing API.
- A valid **Page access token** and **Page ID** for the Facebook Page you want to manage.
- An OpenAI API key with access to GPT-4o (or similar model available via LangChain).

## Setup

1. **Clone the repository:**

   ```
   git clone https://github.com/yourusername/facebook-ads-ai-assistant.git
   cd facebook-ads-ai-assistant
   ```

2. **Create and activate a virtual environment:**

   ```
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install the dependencies:**

   ```
   pip install -r requirements.txt
   ```

4. **Configure secrets:**

   Create (or update) the file `.streamlit/secrets.toml` with your credentials:

   ```toml
   OPENAI_API_KEY = "your-openai-key"
   FB_APP_ID = "your-facebook-app-id"
   FB_APP_SECRET = "your-facebook-app-secret"
   FB_ACCESS_TOKEN = "your-new-page-access-token"  # Must be a Page access token!
   FB_AD_ACCOUNT_ID = "act_your_ad_account_id"
   FB_PAGE_ID = "your_facebook_page_numeric_id"
   ```

5. **Run the application:**

   ```
   streamlit run app.py
   ```

   Then open the provided URL (e.g., [http://localhost:8501](http://localhost:8501)) in your browser.

## Usage

- **Conversational Interface:**  
  Type queries into the chat input. For example:
  - "Boost all posts from last week"
  - "Promote posts from 2023-01-01 to 2023-01-31"
  - "All posts for all time"

- **Dynamic Campaign Creation:**  
  The system will interpret your natural language instructions, fetch the relevant posts using the Facebook Graph API, ask for any missing details (like campaign objective or budget), and then create a campaign accordingly.

## Notes

- The agent’s system prompt includes the current date/time to provide context.
- The project uses [dateparser](https://pypi.org/project/dateparser/) to convert natural language date phrases into datetime objects.
- Ensure your Facebook App and tokens have the proper permissions (e.g., `pages_read_engagement`, `pages_manage_posts`).