import streamlit as st
from agent import run_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

st.set_page_config(page_title="Facebook Ads AI Assistant", layout="centered")
st.markdown("""
  <h1 style='text-align: center; color: #1877F2;'>
    🤖 Facebook Ads AI Assistant
  </h1>
  <p style='text-align: center; color: grey; font-size:16px;'>
    Interactively create and boost Facebook ad campaigns—just by chatting.
  </p>
""", unsafe_allow_html=True)

history = StreamlitChatMessageHistory()

# Render existing conversation
for msg in history.messages:
    st.chat_message(msg.type).write(msg.content)

# Collect new user input
user_input = st.chat_input("What would you like to do with your Facebook ads?")

if user_input:
    history.add_user_message(user_input)
    st.chat_message("user").write(user_input)
    response = run_agent(user_input, history.messages)
    history.add_ai_message(response)
    st.chat_message("assistant").write(response)