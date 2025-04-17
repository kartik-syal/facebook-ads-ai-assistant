import streamlit as st
from assistant_client import create_thread, run_turn
from logger import info, error, debug, warning

debug("Starting Facebook Ads AI Assistant application")

st.set_page_config(page_title="Facebook Ads AI Assistant", layout="centered")
st.markdown("""
  <h1 style='text-align: center; color: #1877F2;'>🤖 Facebook Ads AI Assistant</h1>
  <p style='text-align: center; color: grey; font-size:16px;'>
    Interactively create and boost Facebook ad campaigns—just by chatting.
  </p>
""", unsafe_allow_html=True)

# ―― Initialize session state ――
if "thread_id" not in st.session_state:
    info("Initializing new session state with a new thread")
    try:
        thread_id = create_thread()
        st.session_state.thread_id = thread_id
        st.session_state.history = []
        debug(f"Session initialized with thread ID: {thread_id}")
    except Exception as e:
        error(f"Failed to initialize session: {e}")
        st.error(f"Failed to initialize: {e}")

# Reset button
if st.button("🔄 Start New Conversation"):
    info("User requested to start a new conversation")
    try:
        thread_id = create_thread()
        st.session_state.thread_id = thread_id
        st.session_state.history.clear()
        debug(f"Reset conversation with new thread ID: {thread_id}")
        st.rerun()
    except Exception as e:
        error(f"Failed to reset conversation: {e}")
        st.error(f"Failed to reset: {e}")

# Render chat history
for role, text in st.session_state.history:
    st.chat_message(role).write(text)

# User input
user_input = st.chat_input("What would you like to do with your Facebook ads?")

if user_input:
    info(f"Received user input: {user_input[:50]}..." if len(user_input) > 50 else user_input)
    
    # Show user
    st.session_state.history.append(("user", user_input))
    st.chat_message("user").write(user_input)

    # Stream assistant reply
    assistant_msg = ""
    placeholder = None
    debug(f"Starting assistant response stream for thread {st.session_state.thread_id}")
    
    try:
        for chunk in run_turn(st.session_state.thread_id, user_input):
            assistant_msg += chunk
            
            # Only create the placeholder once we have some content
            if placeholder is None and assistant_msg.strip():
                placeholder = st.chat_message("assistant")
            
            # Only write to placeholder if it exists
            if placeholder is not None:
                placeholder.write(assistant_msg)
    except Exception as e:
        error(f"Error during run_turn streaming: {e}")
        assistant_msg = f"I encountered an error: {str(e)}"
        if placeholder is None:
            placeholder = st.chat_message("assistant")
        placeholder.write(assistant_msg)

    # In case we received no content at all, create placeholder at the end
    if placeholder is None:
        warning("No assistant response received")
        placeholder = st.chat_message("assistant")
        placeholder.write("I couldn't generate a response. Please try again.")

    # Save it
    debug(f"Saving assistant response to history: {assistant_msg[:50]}..." if len(assistant_msg) > 50 else assistant_msg)
    st.session_state.history.append(("assistant", assistant_msg))
