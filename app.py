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

if user_input:
    # Add user's message to history
    history.add_user_message(user_input)
    st.chat_message("user").write(user_input)

    # Run your agent
    response = run_agent(user_input, history.messages)

    # Now create a single assistant message block
    with st.chat_message("assistant"):
        # 1) Write the AI text first
        st.write(response)

        # 2) Immediately follow up with the posts (if any) inside the same block
        if "latest_posts" in st.session_state:
            posts = st.session_state.latest_posts
            posts_per_row = 3
            for i in range(0, len(posts), posts_per_row):
                cols = st.columns(posts_per_row)
                for j, post in enumerate(posts[i : i + posts_per_row]):
                    with cols[j]:
                        st.markdown(f"**Post {i+j+1}**")
                        try:
                            dt = parse(post["created_time"])
                            friendly_time = dt.strftime("%b %d, %Y %I:%M %p")
                        except Exception:
                            friendly_time = post["created_time"]
                        st.markdown(f"**Created:** {friendly_time}")

                        if post.get("excerpt") and post["excerpt"].strip().lower() != "<no text>":
                            st.markdown(f"**Preview:** {post['excerpt']}")

                        if post.get("full_picture"):
                            st.markdown(
                                f"""
                                <div style="height: 200px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
                                    <img src="{post['full_picture']}" style="max-height: 100%; max-width: 100%; object-fit: contain;" />
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        if post.get("permalink_url"):
                            st.markdown(f"[View on Facebook]({post['permalink_url']})")

                        st.markdown(
                            f"<small style='color:gray;'>ID: {post['id']}</small>", 
                            unsafe_allow_html=True
                        )

            # Clear out the stored posts so they don't reappear on refresh
            del st.session_state.latest_posts

    # Finally add the AI response text to message history
    history.add_ai_message(response)
