import streamlit as st
from fb_api import get_posts_by_range, create_campaign, boost_posts
from datetime import datetime
import json
from langchain.tools import Tool

def tool_get_posts(input_str: str) -> str:
    """
    Retrieves posts from your Facebook Page for a given ISO date range.
    Input should be a JSON string with 'since' and 'until' dates in ISO format (YYYY-MM-DD).
    Example: {"since": "2023-01-01", "until": "2023-01-31"}
    """
    try:
        input_data = json.loads(input_str)
        since = input_data.get("since")
        until = input_data.get("until")
        
        if not since or not until:
            return "Error: Both 'since' and 'until' dates are required."
        
        since_dt = datetime.fromisoformat(since)
        until_dt = datetime.fromisoformat(until)
        page_id = st.secrets["FB_PAGE_ID"]
        posts = get_posts_by_range(page_id, since_dt, until_dt)
        if not posts:
            return f"No posts found from {since_dt.date()} to {until_dt.date()}."

        return posts
    except json.JSONDecodeError:
        return "Error: Input must be a valid JSON string with 'since' and 'until' fields."
    except Exception as e:
        return f"Error in GetPosts: {e}"

def tool_create_campaign(input_str: str) -> str:
    """
    Creates a paused Facebook ad campaign with the specified parameters.
    Input should be a JSON string with 'name', 'objective', and 'budget' fields.
    Example: {"name": "Summer Sale", "objective": "OUTCOME_TRAFFIC", "budget": 10.0}
    """
    try:
        input_data = json.loads(input_str)
        name = input_data.get("name")
        objective = input_data.get("objective")
        budget = input_data.get("budget")
        
        if not all([name, objective, budget]):
            return "Error: 'name', 'objective', and 'budget' are all required."
        
        daily_budget = int(float(budget) * 100)  # Convert dollars to cents
        result = create_campaign(name, objective, daily_budget, None)
        return f"Campaign '{name}' created with ID: {result['campaign_id']}."
    except json.JSONDecodeError:
        return "Error: Input must be a valid JSON string with 'name', 'objective', and 'budget' fields."
    except Exception as e:
        return f"Error in CreateCampaign: {e}"

def tool_boost_posts(input_str: str) -> str:
    """
    Boost specific posts under an existing campaign.
    Input should be a JSON string with 'campaign_id', 'post_ids', 'optimization_goal', 'bid_amount', and 'geo_locations' fields.
    Example: {"campaign_id": "123456", "post_ids": ["post1", "post2"], "optimization_goal": "POST_ENGAGEMENT", "bid_amount": 5.0, "geo_locations": ["US", "CA"]}
    """
    try:
        input_data = json.loads(input_str)
        campaign_id = input_data.get("campaign_id")
        post_ids = input_data.get("post_ids")
        optimization_goal = input_data.get("optimization_goal")
        bid_amount = input_data.get("bid_amount")
        geo_locations = input_data.get("geo_locations")
        
        if not all([campaign_id, post_ids, optimization_goal, bid_amount, geo_locations]):
            return "Error: All fields (campaign_id, post_ids, optimization_goal, bid_amount, geo_locations) are required."
        
        bid_cents = int(float(bid_amount) * 100)  # Convert dollars to cents
        geo_locations = [g.strip().upper() for g in geo_locations]
        
        res = boost_posts(campaign_id, post_ids, optimization_goal, bid_cents, geo_locations)
        return (f"Boosted {len(post_ids)} posts under ad set {res['ad_set_id']}. "
                f"Ad IDs: {res['ad_ids']}")
    except json.JSONDecodeError:
        return "Error: Input must be a valid JSON string with 'campaign_id', 'post_ids', 'optimization_goal', 'bid_amount', and 'geo_locations' fields."
    except Exception as e:
        return f"Error boosting posts: {e}"

get_posts_tool = Tool(
    name="GetPosts",
    description=(
        "Retrieves posts from your Facebook Page over a specified date range. "
        "Input must be a JSON string with 'since' and 'until' in ISO format (YYYY-MM-DD). "
    ),
    func=tool_get_posts,
)

create_campaign_tool = Tool(
    name="CreateCampaign",
    description=(
        "Creates a paused Facebook ad campaign. "
        "Input must be a JSON string with 'name', 'objective', and 'budget' fields. "
    ),
    func=tool_create_campaign,
)

boost_posts_tool = Tool(
    name="BoostPosts",
    description=(
        "Boost specific posts under an existing campaign. "
        "Input must be a JSON string with 'campaign_id', 'post_ids', 'optimization_goal', 'bid_amount', and 'geo_locations' fields. "
    ),
    func=tool_boost_posts,
)
