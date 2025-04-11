import streamlit as st
from datetime import datetime
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from tools import get_posts_tool, create_campaign_tool

# Inject current datetime into the system prompt
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
system_message = f"""
[As of {now}] You are a Facebook Ads Assistant. You have two tools:

1) GetPosts – retrieves post IDs for a user‐specified time range.
   • Accepts natural language: 'yesterday', 'last week', '2023-01-01 to 2023-02-01', 'all posts', etc.
2) CreateCampaign – creates an ad campaign.
   • Input: 'CampaignName;Objective;Budget' (e.g., 'Boost Posts;ENGAGEMENT;$5').

Workflow:
- When asked to promote posts in a given range, first call GetPosts.
- Then ask follow‑up questions for KPI/objective and budget if missing.
- Finally call CreateCampaign.
- Always summarize what you did at the end.
"""

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    api_key=st.secrets["OPENAI_API_KEY"],
)

agent = initialize_agent(
    tools=[get_posts_tool, create_campaign_tool],
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"system_message": system_message},
)

def run_agent(user_input: str, chat_history) -> str:
    # Pass both input and history so the agent can maintain context
    result = agent({"input": user_input, "chat_history": chat_history})
    return result["output"]
