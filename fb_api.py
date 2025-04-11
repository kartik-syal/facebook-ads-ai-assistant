import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
import datetime

# Initialize Facebook API using Streamlit secrets
FacebookAdsApi.init(
    app_id=st.secrets["FB_APP_ID"],
    app_secret=st.secrets["FB_APP_SECRET"],
    access_token=st.secrets["FB_ACCESS_TOKEN"],
)

AD_ACCOUNT_ID = st.secrets["FB_AD_ACCOUNT_ID"]
PAGE_ID      = st.secrets["FB_PAGE_ID"]  # numeric page ID

def get_posts_by_range(page_id: str, since: datetime.datetime, until: datetime.datetime) -> list[str]:
    """
    Fetch all post IDs from the given Facebook Page between since/until.
    """
    page = Page(page_id)
    posts = page.get_posts(
        fields=["id", "created_time", "message"],
        params={"since": since.isoformat(), "until": until.isoformat()}
    )
    post_ids = [p["id"] for p in posts]
    # paginate
    while posts:
        try:
            posts = posts.load_next_page()
            post_ids.extend(p["id"] for p in posts)
        except Exception:
            break
    return post_ids

def create_campaign(name: str, objective: str, daily_budget: int, num_ads: int | None = None) -> dict:
    """
    Create a Facebook ad campaign. Returns campaign ID (and num_ads if provided).
    """
    ad_account = AdAccount(AD_ACCOUNT_ID)
    campaign = ad_account.create_campaign(
        params={
            "name": name,
            "objective": objective,
            "status": Campaign.Status.paused,
            "daily_budget": str(daily_budget),
        }
    )
    result = {"campaign_id": campaign["id"]}
    if num_ads is not None:
        result["num_ads"] = num_ads
    return result
