# tools.py

import streamlit as st
from langchain.agents import Tool
from fb_api import get_posts_by_range, create_campaign, boost_posts
import dateparser
from datetime import datetime

def parse_date_range(natural_str: str) -> tuple[datetime, datetime]:
    now = datetime.now()
    txt = natural_str.strip().lower()
    if txt in ("all posts", "all time", "all"):
        return datetime(2000,1,1), now
    if " to " in txt:
        start_txt, end_txt = txt.split(" to ",1)
        return dateparser.parse(start_txt, settings={"PREFER_DATES_FROM": "past"}), dateparser.parse(end_txt, settings={"PREFER_DATES_FROM": "future"})
    else:
        return dateparser.parse(txt, settings={"PREFER_DATES_FROM": "past"}) or datetime(2000,1,1), now

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
        if not posts:
            return f"No posts found from {since.date()} to {until.date()}."

        # Store for UI rendering
        st.session_state.latest_posts = posts

        # Numbered summary
        lines = []
        for i, p in enumerate(posts, start=1):
            lines.append(
                f"{i}. ID: {p['id']}\n   • Created: {p['created_time']}\n   • Excerpt: \"{p['excerpt']}\""
            )
        return (
            f"Found {len(posts)} posts from {since.date()} to {until.date()}:\n\n"
             "\n\n".join(lines)
        )
    except Exception as e:
        return f"Error in GetPosts: {e}"

def tool_create_campaign(input_str: str) -> str:
    try:
        name, objective, budget_str = [p.strip() for p in input_str.split(";")]
        budget = float(budget_str.replace("$", "").strip())
        daily_budget = int(budget * 100)
    except Exception:
        return ("Error: please provide campaign details in the format 'Name;Objective;Budget', e.g. 'Boost Posts;ENGAGEMENT;$10'.")
    try:
        result = create_campaign(name, objective, daily_budget, None)
        return f"✅ Campaign '{name}' created with ID: {result['campaign_id']}."
    except Exception as e:
        return f"Error in CreateCampaign: {e}"

def tool_boost_posts(input_str: str) -> str:
    """
    BoostPosts Tool:
    Boost specific posts under an existing campaign.
    Input format: 
      'campaign_id;post_id1,post_id2,...;optimization_goal;bid_amount;geolocations'
    Example: 
      '1234567890;121745232751965_122200870082052318,121745232751965_121745459418609;POST_ENGAGEMENT;0.50;US,CA'
    
    Note: bid_amount is provided in dollars and converted to cents.
    """
    try:
        parts = [p.strip() for p in input_str.split(";")]
        if len(parts) != 5:
            return ("Error: please provide details as 'campaign_id;post_id1,post_id2;optimization_goal;bid_amount;geolocations'. "
                    "E.g. '1234567890;121_1,121_2;POST_ENGAGEMENT;0.50;US,CA'.")
        campaign_id = parts[0]
        post_ids = [pid.strip() for pid in parts[1].split(",") if pid.strip()]
        optimization_goal = parts[2]
        bid_amount = int(float(parts[3]) * 100)  # Convert dollars to cents
        geo_locations = [g.strip().upper() for g in parts[4].split(",") if g.strip()]
    except Exception as e:
        return f"Error parsing input: {e}"
    try:
        res = boost_posts(campaign_id, post_ids, optimization_goal, bid_amount, geo_locations)
        return (f"✅ Boosted {len(post_ids)} posts under ad set {res['ad_set_id']}. "
                f"Ad IDs: {res['ad_ids']}")
    except Exception as e:
        return f"Error boosting posts: {e}"

get_posts_tool = Tool(
    name="GetPosts",
    func=tool_get_posts,
    description=(
        "Retrieves posts from your Facebook Page over a specified natural language time range. "
        "For example: 'last week' or '2023-01-01 to 2023-02-01'. "
        "Returns friendly details (post IDs, creation times, excerpts)."
    ),
)

create_campaign_tool = Tool(
    name="CreateCampaign",
    func=tool_create_campaign,
    description=(
        "Creates a paused Facebook ad campaign. Input must be in the format 'CampaignName;Objective;Budget'. "
        "For example: 'Boost Posts;ENGAGEMENT;$10'."
    ),
)

boost_posts_tool = Tool(
    name="BoostPosts",
    func=tool_boost_posts,
    description=(
        "Boost specific posts under an existing campaign. Input format: "
        "'campaign_id;post_id1,post_id2;optimization_goal;bid_amount;geolocations'. "
        "For example: '1234567890;121745232751965_122200870082052318,121745232751965_121745459418609;POST_ENGAGEMENT;0.50;US,CA'."
    ),
)
