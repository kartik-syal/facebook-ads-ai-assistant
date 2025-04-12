# fb_api.py

import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
import datetime

# ──────────────────────────────────────────────────────────────────────────────
# Load and validate IDs from secrets
# ──────────────────────────────────────────────────────────────────────────────

PAGE_ID        = st.secrets["FB_PAGE_ID"]
raw_ad_acc_id  = st.secrets["FB_AD_ACCOUNT_ID"]

# Ensure Ad Account ID has the "act_" prefix
if not raw_ad_acc_id.startswith("act_"):
    ad_account_id = "act_" + raw_ad_acc_id
else:
    ad_account_id = raw_ad_acc_id

# Prevent using the Page ID as the Ad Account ID
if ad_account_id.replace("act_", "") == PAGE_ID:
    raise RuntimeError(
        "It looks like FB_AD_ACCOUNT_ID is set to your Page ID. "
        "Please update `.streamlit/secrets.toml` so that FB_AD_ACCOUNT_ID "
        "is your Ad Account ID (prefixed with 'act_')."
    )

AD_ACCOUNT_ID = ad_account_id

# ──────────────────────────────────────────────────────────────────────────────
# Initialize the Facebook API using your unified token
# ──────────────────────────────────────────────────────────────────────────────

FacebookAdsApi.init(
    app_id=st.secrets["FB_APP_ID"],
    app_secret=st.secrets["FB_APP_SECRET"],
    access_token=st.secrets["FB_ACCESS_TOKEN"],
)

def get_posts_by_range(page_id: str, since: datetime.datetime, until: datetime.datetime) -> list[dict]:
    """
    Fetch all posts from the given Facebook Page between `since` and `until`.
    Returns a list of dicts with id, created_time, and an excerpt.
    """
    page = Page(page_id)
    posts = page.get_posts(
        fields=["id", "created_time", "message"],
        params={"since": since.isoformat(), "until": until.isoformat()}
    )
    results = []
    for p in posts:
        message = p.get("message", "")
        excerpt = message[:50] + ("..." if len(message) > 50 else "")
        results.append({
            "id": p["id"],
            "created_time": p.get("created_time", "N/A"),
            "excerpt": excerpt,
        })
    while posts:
        try:
            posts = posts.load_next_page()
            for p in posts:
                message = p.get("message", "")
                excerpt = message[:50] + ("..." if len(message) > 50 else "")
                results.append({
                    "id": p["id"],
                    "created_time": p.get("created_time", "N/A"),
                    "excerpt": excerpt,
                })
        except Exception:
            break
    return results

def create_campaign(name: str, objective: str, daily_budget: int, num_ads: int | None = None) -> dict:
    """
    Create a Facebook ad campaign under your (real) ad account.
    The campaign is created in PAUSED status to prevent delivery/spend.
    """
    objective_map = {
        "engagement":       "OUTCOME_ENGAGEMENT",
        "post_engagement":  "OUTCOME_ENGAGEMENT",
        "leads":            "OUTCOME_LEADS",
        "lead_generation":  "OUTCOME_LEADS",
        "conversions":      "OUTCOME_SALES",
        "sales":            "OUTCOME_SALES",
        "traffic":          "OUTCOME_TRAFFIC",
        "link_clicks":      "OUTCOME_TRAFFIC",
        "awareness":        "OUTCOME_AWARENESS",
        "brand_awareness":  "OUTCOME_AWARENESS",
        "app_promotion":    "OUTCOME_APP_PROMOTION",
        "app promotion":    "OUTCOME_APP_PROMOTION",
    }
    valid_objective = objective_map.get(objective.lower(), objective.upper())

    ad_account = AdAccount(AD_ACCOUNT_ID)
    campaign = ad_account.create_campaign(
        params={
            "name": name,
            "objective": valid_objective,
            "status": Campaign.Status.paused,
            "daily_budget": str(daily_budget),  # in cents
            "special_ad_categories": [],        # required even if empty
        }
    )
    result = {"campaign_id": campaign["id"]}
    if num_ads is not None:
        result["num_ads"] = num_ads
    return result
