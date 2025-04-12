# tools.py

import streamlit as st
from langchain.agents import Tool
from fb_api import get_posts_by_range, create_campaign
import dateparser
from datetime import datetime

def parse_date_range(natural_str: str) -> tuple[datetime, datetime]:
    """
    Convert natural language phrases like "yesterday", "last week",
    "2023-01-01 to 2023-02-01", or "all posts" into since/until datetime objects.
    """
    now = datetime.now()
    txt = natural_str.strip().lower()
    if txt in ("all posts", "all time", "all"):
        since = datetime(2000, 1, 1)
        until = now
    elif " to " in txt:
        start_txt, end_txt = txt.split(" to ", 1)
        since = dateparser.parse(start_txt, settings={"PREFER_DATES_FROM": "past"})
        until = dateparser.parse(end_txt, settings={"PREFER_DATES_FROM": "future"})
    else:
        since = dateparser.parse(txt, settings={"PREFER_DATES_FROM": "past"})
        until = now
    if not since:
        since = datetime(2000, 1, 1)
    if not until:
        until = now
    return since, until

def tool_get_posts(input_str: str) -> str:
    """
    GetPosts Tool:
    Retrieves posts from your Facebook Page for a given natural language time range.
    Returns a friendly summary with each post's ID, created time, and a short excerpt.
    Example inputs: "yesterday", "last week", "2023-01-01 to 2023-02-01", "all posts".
    """
    try:
        since, until = parse_date_range(input_str)
        page_id = st.secrets["FB_PAGE_ID"]
        posts = get_posts_by_range(page_id, since, until)
        if posts:
            lines = []
            for post in posts:
                line = f"ID: {post['id']}, Created: {post['created_time']}, Excerpt: \"{post['excerpt']}\""
                lines.append(line)
            summary = "\n".join(lines)
            return f"Found {len(posts)} posts from {since.date()} to {until.date()}:\n{summary}"
        else:
            return f"No posts found from {since.date()} to {until.date()}."
    except Exception as e:
        return f"Error in GetPosts: {e}"

def tool_create_campaign(input_str: str) -> str:
    """
    CreateCampaign Tool:
    Creates a Facebook ad campaign using provided details.
    Input format: 'CampaignName;Objective;Budget'
    For example: 'Boost Posts;ENGAGEMENT;$10'
    The budget must be provided as a number (with or without a $ symbol).
    """
    try:
        name, objective, budget_str = [p.strip() for p in input_str.split(";")]
        budget = float(budget_str.replace("$", "").strip())
        daily_budget = int(budget * 100)
        num_ads = None  # Optionally, this could be determined from the posts if needed
        result = create_campaign(name, objective, daily_budget, num_ads)
        ads_info = f" and {result.get('num_ads')} ads" if result.get("num_ads") else ""
        return f"Campaign '{name}' created with ID: {result['campaign_id']}{ads_info}."
    except Exception as e:
        return f"Error in CreateCampaign: {e}"

get_posts_tool = Tool(
    name="GetPosts",
    func=tool_get_posts,
    description=(
        "Retrieves posts from your Facebook Page over a specified natural language time range. "
        "For example, input 'last week' or '2023-01-01 to 2023-02-01'. "
        "The output includes post IDs, creation times, and short message excerpts."
    ),
)

create_campaign_tool = Tool(
    name="CreateCampaign",
    func=tool_create_campaign,
    description=(
        "Creates a Facebook ad campaign. Input must be in the format 'CampaignName;Objective;Budget'. "
        "For example, 'Boost Posts;ENGAGEMENT;$10'. Ensure no extra characters or newlines are included."
    ),
)
