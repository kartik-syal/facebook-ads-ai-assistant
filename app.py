import streamlit as st
from assistant_client import create_thread, run_turn

st.set_page_config(page_title="Facebook Ads AI Assistant", layout="centered")
st.markdown("""
  <h1 style='text-align: center; color: #1877F2;'>🤖 Facebook Ads AI Assistant</h1>
  <p style='text-align: center; color: grey; font-size:16px;'>
    Interactively create and boost Facebook ad campaigns—just by chatting.
  </p>
""", unsafe_allow_html=True)

# ―― Initialize session state ――
if "thread_id" not in st.session_state:
    st.session_state.thread_id = create_thread()
    st.session_state.history = []

# Reset button
if st.button("🔄 Start New Conversation"):
    st.session_state.thread_id = create_thread()
    st.session_state.history.clear()
    st.rerun()

# Render chat history
for role, text in st.session_state.history:
    st.chat_message(role).write(text)

# User input
user_input = st.chat_input("What would you like to do with your Facebook ads?")

if user_input:
    # Show user
    st.session_state.history.append(("user", user_input))
    st.chat_message("user").write(user_input)

    # Stream assistant reply
    assistant_msg = ""
    placeholder = None
    for chunk in run_turn(st.session_state.thread_id, user_input):
        assistant_msg += chunk
        
        # Only create the placeholder once we have some content
        if placeholder is None and assistant_msg.strip():
            placeholder = st.chat_message("assistant")
        
        # Only write to placeholder if it exists
        if placeholder is not None:
            placeholder.write(assistant_msg)

    # In case we received no content at all, create placeholder at the end
    if placeholder is None:
        placeholder = st.chat_message("assistant")
        placeholder.write("I couldn't generate a response. Please try again.")

    # Save it
    st.session_state.history.append(("assistant", assistant_msg))
