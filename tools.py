import streamlit as st
from langchain.agents import Tool
from fb_api import get_posts_by_range, create_campaign
import dateparser  # natural‐language date parsing :contentReference[oaicite:0]{index=0}
from datetime import datetime

def parse_date_range(natural_str: str) -> tuple[datetime, datetime]:
    """
    Convert phrases like "yesterday", "last week", 
    "2023-01-01 to 2023-02-01", or "all posts" into since/until datetimes.
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
        # relative expression (e.g., "yesterday", "2 weeks ago")
        since = dateparser.parse(txt, settings={"PREFER_DATES_FROM": "past"})
        until = now

    # Fallback if parsing failed
    if not since:
        since = datetime(2000, 1, 1)
    if not until:
        until = now

    return since, until

def tool_get_posts(input_str: str) -> str:
    """
    Tool: Retrieve posts in any time range.
    Input examples:
      - "yesterday"
      - "last week"
      - "2023-01-01 to 2023-02-01"
      - "all posts"
    """
    try:
        since, until = parse_date_range(input_str)
        page_id = st.secrets["FB_PAGE_ID"]
        posts = get_posts_by_range(page_id, since, until)
        return (
            f"Found {len(posts)} posts from {since.date()} to {until.date()}: {posts}"
        )
    except Exception as e:
        return f"Error in GetPosts: {e}"

def tool_create_campaign(input_str: str) -> str:
    """
    Tool: Create a Facebook ad campaign.
    Input format: 'CampaignName;Objective;Budget'
    e.g. 'Boost Posts;ENGAGEMENT;$5'
    """
    try:
        name, objective, budget_str = [p.strip() for p in input_str.split(";")]
        budget = float(budget_str.replace("$", ""))
        daily_budget = int(budget * 100)
        # Number of ads = number of posts if name contains a range indicator
        num_ads = None
        if "all posts" in name.lower() or ";" in name:
            # assume the agent will supply exact number if needed
            num_ads = None
        result = create_campaign(name, objective, daily_budget, num_ads)
        ads_info = f" and {result.get('num_ads')} ads" if result.get("num_ads") else ""
        return f"Campaign '{name}' created with ID: {result['campaign_id']}{ads_info}."
    except Exception as e:
        return f"Error in CreateCampaign: {e}"

get_posts_tool = Tool(
    name="GetPosts",
    func=tool_get_posts,
    description=(
        "Retrieve posts in any natural‐language time range. "
        "E.g., 'yesterday', 'last week', '2023-01-01 to 2023-02-01', or 'all posts'."
    ),
)

create_campaign_tool = Tool(
    name="CreateCampaign",
    func=tool_create_campaign,
    description=(
        "Create a Facebook ad campaign. "
        "Input: 'CampaignName;Objective;Budget' (e.g., 'Boost Posts;ENGAGEMENT;$5')."
    ),
)
