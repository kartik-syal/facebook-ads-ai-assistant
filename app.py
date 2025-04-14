# app.py
from dateutil.parser import parse
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

# In app.py
if user_input:
    # Add user's message to history
    history.add_user_message(user_input)
    st.chat_message("user").write(user_input)

    # Run your agent
    response = run_agent(user_input, history.messages)
    
    # Build a complete response that includes both the AI text and formatted posts
    complete_response = response
    
    # If we have posts to display
    if "latest_posts" in st.session_state:
        posts = st.session_state.latest_posts
        
        # Create a single assistant message block
        with st.chat_message("assistant"):
            # Display the AI text response
            st.markdown(response)
            
            # Add a header for the posts section
            st.markdown("### Here are the posts I found:")
            
            # Use columns for horizontal layout
            cols = st.columns(min(len(posts), 3))  # Up to 3 columns
            
            for i, (col, post) in enumerate(zip(cols, posts)):
                with col:
                    st.markdown(f"**Post {i+1}**")
                    
                    try:
                        dt = parse(post["created_time"])
                        friendly_time = dt.strftime("%b %d, %Y %I:%M %p")
                    except Exception:
                        friendly_time = post["created_time"]
                    
                    st.markdown(f"**Created:** {friendly_time}")
                    
                    if post.get("excerpt") and post["excerpt"].strip().lower() != "<no text>":
                        st.markdown(f"**Preview:** {post['excerpt']}")
                    
                    if post.get("full_picture"):
                        st.image(post["full_picture"], use_container_width=True)
                    
                    if post.get("permalink_url"):
                        st.markdown(f"[View on Facebook]({post['permalink_url']})")
                    
                    st.markdown(f"<small style='color:gray;'>ID: {post['id']}</small>", unsafe_allow_html=True)
            
            # Also store a markdown version of the posts for history
            posts_markdown = "\n\n### Here are the posts I found:\n\n"
            for i, post in enumerate(posts):
                try:
                    dt = parse(post["created_time"])
                    friendly_time = dt.strftime("%b %d, %Y %I:%M %p")
                except Exception:
                    friendly_time = post["created_time"]
                
                posts_markdown += f"**Post {i+1}**  \n"
                posts_markdown += f"**Created:** {friendly_time}  \n"
                
                if post.get("excerpt") and post["excerpt"].strip().lower() != "<no text>":
                    posts_markdown += f"**Preview:** {post['excerpt']}  \n"
                
                # Image links don't render in message history, so we note there was an image
                if post.get("full_picture"):
                    posts_markdown += f"*[Post contains an image]*  \n"
                
                if post.get("permalink_url"):
                    posts_markdown += f"[View on Facebook]({post['permalink_url']})  \n"
                
                posts_markdown += f"ID: {post['id']}  \n\n"
                
                # Add separator between posts
                if i < len(posts) - 1:
                    posts_markdown += "---\n\n"
        
        # Add the combined response with markdown to message history
        history.add_ai_message(complete_response + posts_markdown)
        
        # Clear out the stored posts so they don't reappear on refresh
        del st.session_state.latest_posts
    else:
        # If no posts, just display the normal response
        with st.chat_message("assistant"):
            st.markdown(response)
        history.add_ai_message(response)