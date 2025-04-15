import datetime
import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad

PAGE_ID = st.secrets["FB_PAGE_ID"]
raw_ad_acc_id = st.secrets["FB_AD_ACCOUNT_ID"]

if not raw_ad_acc_id.startswith("act_"):
    ad_account_id = "act_" + raw_ad_acc_id
else:
    ad_account_id = raw_ad_acc_id

AD_ACCOUNT_ID = ad_account_id

FacebookAdsApi.init(
    app_id=st.secrets["FB_APP_ID"],
    app_secret=st.secrets["FB_APP_SECRET"],
    access_token=st.secrets["FB_ACCESS_TOKEN"],
)

def get_posts_by_range(page_id: str, since: datetime.datetime, until: datetime.datetime) -> list[dict]:
    """
    Fetch posts including media URLs and permalink for richer previews.
    """
    page = Page(page_id)
    posts = page.get_posts(
        fields=[
            "id",
            "created_time",
            "message",
            "full_picture",
            "permalink_url",
        ],
        params={"since": since.isoformat(), "until": until.isoformat()}
    )
    results = []
    for p in posts:
        msg = p.get("message", "")
        excerpt = (msg[:100] + ("…" if len(msg) > 100 else "")) or "<No text>"
        results.append({
            "id": p["id"],
            "created_time": p.get("created_time", ""),
            "excerpt": excerpt,
            "full_picture": p.get("full_picture"),       # may be None
            "permalink_url": p.get("permalink_url"),     # always present
        })
    # paginate
    while posts:
        try:
            posts = posts.load_next_page()
            for p in posts:
                msg = p.get("message", "")
                excerpt = (msg[:100] + ("…" if len(msg) > 100 else "")) or "<No text>"
                results.append({
                    "id": p["id"],
                    "created_time": p.get("created_time", ""),
                    "excerpt": excerpt,
                    "full_picture": p.get("full_picture"),
                    "permalink_url": p.get("permalink_url"),
                })
        except Exception:
            break
    return results

def create_campaign(name: str, objective: str, daily_budget: int, num_ads: int | None = None) -> dict:
    """
    Create a Facebook ad campaign under your ad account.
    The campaign is created in PAUSED status (no delivery/spend).
    """
    ad_account = AdAccount(AD_ACCOUNT_ID)
    camp = ad_account.create_campaign(params={
        "name": name,
        "objective": objective,
        "status": Campaign.Status.paused,
        "daily_budget": str(daily_budget),
        "special_ad_categories": [],
    })
    res = {"campaign_id": camp["id"]}
    if num_ads is not None:
        res["num_ads"] = num_ads
    return res

def create_ad_set(campaign_id: str, optimization_goal: str, bid_amount: int, geo_locations: list[str]) -> str:
    """
    Create one paused Ad Set under the given campaign.
    Note: No daily budget here (campaign-level budget is used).
    """
    targeting = {"geo_locations": {"countries": geo_locations}}
    ad_account = AdAccount(AD_ACCOUNT_ID)
    adset = ad_account.create_ad_set(params={
        "name": f"AdSet for campaign {campaign_id}",
        "campaign_id": campaign_id,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": optimization_goal,
        "bid_amount": str(bid_amount),
        "targeting": targeting,
        "status": AdSet.Status.paused,
    })
    return adset["id"]

def boost_posts(campaign_id: str, post_ids: list[str], optimization_goal: str, bid_amount: int, geo_locations: list[str]) -> dict:
    """
    For each post ID, create an AdCreative and an Ad under one Ad Set.
    """
    ad_set_id = create_ad_set(campaign_id, optimization_goal, bid_amount, geo_locations)
    ad_account = AdAccount(AD_ACCOUNT_ID)
    ad_ids = []
    for pid in post_ids:
        creative = ad_account.create_ad_creative(params={
            "name": f"Creative for post {pid}",
            "object_story_id": pid,
        })
        creative_id = creative["id"]
        ad = ad_account.create_ad(params={
            "name": f"Ad for post {pid}",
            "adset_id": ad_set_id,
            "creative": {"creative_id": creative_id},
            "status": Ad.Status.paused,
        })
        ad_ids.append(ad["id"])
    return {"ad_set_id": ad_set_id, "ad_ids": ad_ids}
