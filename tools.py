import streamlit as st
from fb_api import get_posts_by_range, create_campaign, boost_posts
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from typing import List, Literal


class PostDateInput(BaseModel):
    since: str = Field(..., description="Start date in ISO format (YYYY-MM-DD)")
    until: str = Field(..., description="End date in ISO format (YYYY-MM-DD)")

class CampaignInput(BaseModel):
    name: str = Field(..., description="Name of the campaign")
    objective: Literal[
        "OUTCOME_ENGAGEMENT", "OUTCOME_LEADS", "OUTCOME_SALES", 
        "OUTCOME_TRAFFIC", "OUTCOME_AWARENESS", "OUTCOME_APP_PROMOTION"
    ] = Field(..., description="Campaign objective")
    budget: float = Field(..., description="Daily budget in dollars (e.g., 10.0)")

class BoostPostsInput(BaseModel):
    campaign_id: str = Field(..., description="ID of the campaign to use")
    post_ids: List[str] = Field(..., description="List of post IDs to boost")
    optimization_goal: Literal[
        "POST_ENGAGEMENT", "LINK_CLICKS", "IMPRESSIONS", "REACH", 
        "PAGE_LIKES", "OFFSITE_CONVERSIONS", "VIDEO_VIEWS"
    ] = Field(..., description="Optimization goal")
    bid_amount: float = Field(..., description="Bid amount in dollars")
    geo_locations: List[str] = Field(..., description="List of country codes (e.g., ['US', 'CA'])")

def tool_get_posts(since: str, until: str) -> str:
    """
    Retrieves posts from your Facebook Page for a given ISO date range.
    """
    try:
        since_dt = datetime.fromisoformat(since)
        until_dt = datetime.fromisoformat(until)
        page_id = st.secrets["FB_PAGE_ID"]
        posts = get_posts_by_range(page_id, since_dt, until_dt)
        if not posts:
            return f"No posts found from {since_dt.date()} to {until_dt.date()}."

        return posts
    except Exception as e:
        return f"Error in GetPosts: {e}"

def tool_create_campaign(name: str, objective: str, budget: float) -> str:
    """
    Creates a paused Facebook ad campaign with the specified parameters.
    """
    try:
        daily_budget = int(budget * 100)  # Convert dollars to cents
        result = create_campaign(name, objective, daily_budget, None)
        return f"Campaign '{name}' created with ID: {result['campaign_id']}."
    except Exception as e:
        return f"Error in CreateCampaign: {e}"

def tool_boost_posts(campaign_id: str, post_ids: List[str], optimization_goal: str, bid_amount: float, geo_locations: List[str]) -> str:
    """
    Boost specific posts under an existing campaign.
    """
    try:
        bid_cents = int(bid_amount * 100)  # Convert dollars to cents
        geo_locations = [g.strip().upper() for g in geo_locations]
        
        res = boost_posts(campaign_id, post_ids, optimization_goal, bid_cents, geo_locations)
        return (f"Boosted {len(post_ids)} posts under ad set {res['ad_set_id']}. "
                f"Ad IDs: {res['ad_ids']}")
    except Exception as e:
        return f"Error boosting posts: {e}"

get_posts_tool = StructuredTool.from_function(
    name="GetPosts",
    description=(
        "Retrieves posts from your Facebook Page over a specified date range. "
        "Input must include 'since' and 'until' in ISO format (YYYY-MM-DD)."
    ),
    func=tool_get_posts,
    args_schema=PostDateInput,
)

create_campaign_tool = StructuredTool.from_function(
    name="CreateCampaign",
    description=(
        "Creates a paused Facebook ad campaign with a name, objective, and daily budget."
    ),
    func=tool_create_campaign,
    args_schema=CampaignInput,
)

boost_posts_tool = StructuredTool.from_function(
    name="BoostPosts",
    description=(
        "Boost specific posts under an existing campaign with targeting parameters."
    ),
    func=tool_boost_posts,
    args_schema=BoostPostsInput,
)
