import streamlit as st
from agent import run_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# Page setup
st.set_page_config(page_title="Facebook Ads AI Assistant", layout="centered")
st.markdown("""
  <h1 style='text-align: center; color: #1877F2;'>
    🤖 Facebook Ads AI Assistant
  </h1>
  <p style='text-align: center; color: grey; font-size:16px;'>
    Automate Facebook campaigns for any time range—just by chatting.
  </p>
""", unsafe_allow_html=True)

# Persistent history
history = StreamlitChatMessageHistory()
for msg in history.messages:
    st.chat_message(msg.type).write(msg.content)

# User input
user_input = st.chat_input("What posts should we promote, and how?")

if user_input:
    history.add_user_message(user_input)
    st.chat_message("user").write(user_input)

    # Run the multi‐agent assistant
    response = run_agent(user_input, history.messages)
    history.add_ai_message(response)
    st.chat_message("assistant").write(response)
