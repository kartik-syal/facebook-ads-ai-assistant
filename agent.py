# agent.py

import streamlit as st
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from tools import get_posts_tool, create_campaign_tool

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

system_message = f"""
[As of {now}] You are a Facebook Ads Assistant. Your role is to interactively help the user set up a Facebook ad campaign by asking clarifying questions rather than immediately calling tools.
When a user provides an initial request, follow these steps:
1. Use the GetPosts tool to retrieve posts for the specified time range and present a friendly summary (including post IDs, creation dates, and short excerpts).
2. Ask the user: "Do you want to use all these posts or only specific ones? Please list the post IDs you'd like to include, or type 'all' if you want to use all posts."
3. Ask: "What is your desired campaign objective or KPI?" (Do not assume any default; let the user provide the value.)
4. Ask: "What is your daily budget?" (Request a numerical value; do not add currency symbols.)
5. Once you have all the details, present a summary of the proposed campaign configuration including:
   - The posts to be used (list the post IDs or state 'all')
   - The campaign objective
   - The daily budget
6. Finally, ask: "Do you confirm creating this campaign? If yes, please type 'confirm'." 
7. Only when the user explicitly types "confirm" should you call the CreateCampaign tool.
If any detail is missing, ask the appropriate clarifying question.
Always be conversational and ask one question at a time.
"""

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    openai_api_key=st.secrets["OPENAI_API_KEY"],
)

agent = initialize_agent(
    tools=[get_posts_tool, create_campaign_tool],
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"system_message": system_message},
)

def run_agent(user_input: str, chat_history) -> str:
    outputs = agent.invoke({"input": user_input, "chat_history": chat_history})
    return outputs["output"]
