import toml
import requests
import sys

secrets = toml.load(".streamlit/secrets.toml")
APP_ID = secrets["FB_APP_ID"]
APP_SECRET = secrets["FB_APP_SECRET"]
SHORT_TOKEN = secrets["FB_SHORT_LIVED_USER_TOKEN"]
PAGE_ID = secrets["FB_PAGE_ID"]

resp = requests.get(
    "https://graph.facebook.com/v22.0/oauth/access_token",
    params={
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": SHORT_TOKEN,
    },
)
resp.raise_for_status()
long_user_token = resp.json()["access_token"]

resp = requests.get(
    "https://graph.facebook.com/v22.0/me/accounts",
    params={"access_token": long_user_token},
)
resp.raise_for_status()
for page in resp.json().get("data", []):
    if page.get("id") == PAGE_ID:
        print(page["access_token"])
        sys.exit(0)

sys.exit("Error: FB_PAGE_ID not found in your pages list.")