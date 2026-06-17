"""
v2/notion_oauth.py — Notion OAuth, same structure as v2/oauth.py for Google.

Flow:
  1. /oauth/notion/start  → redirect user to Notion consent screen
  2. Notion redirects to  → /oauth/notion/callback?code=...
  3. Backend exchanges code for access_token, saves to User.notion_token
  4. Redirects back to frontend (user is now fully connected)
"""

import os
import base64
import requests
from dotenv import load_dotenv
from debug import logger

load_dotenv()

NOTION_CLIENT_ID     = os.getenv("NOTION_CLIENT_ID")
NOTION_CLIENT_SECRET = os.getenv("NOTION_CLIENT_SECRET")
NOTION_REDIRECT_URI  = os.getenv("NOTION_REDIRECT_URI")

NOTION_AUTH_URL  = "https://api.notion.com/v1/oauth/authorize"
NOTION_TOKEN_URL = "https://api.notion.com/v1/oauth/token"


# ---------------------------------------------------------------------------
# Step 1 — build the Notion consent URL
# ---------------------------------------------------------------------------

def get_notion_authorize_url() -> str:
    if not NOTION_CLIENT_ID:
        raise RuntimeError("NOTION_CLIENT_ID is not set in .env")
    params = {
        "client_id":     NOTION_CLIENT_ID,
        "response_type": "code",
        "owner":         "user",
        "redirect_uri":  NOTION_REDIRECT_URI,
    }
    url = requests.Request("GET", NOTION_AUTH_URL, params=params).prepare().url
    logger.info(f"[notion] Auth URL generated (redirect_uri={NOTION_REDIRECT_URI})")
    return url


# ---------------------------------------------------------------------------
# Step 2 — exchange code for token, save to the current user's DB row
# ---------------------------------------------------------------------------

async def exchange_notion_code_and_save(code: str, user_id: str):
    """
    Exchange the Notion OAuth code for an access token and save to DB.
    Notion uses HTTP Basic Auth (client_id:client_secret) for the token exchange.
    Must be called with user_id from session cookie — Google OAuth must come first.
    """
    from v2.models import User

    if not NOTION_CLIENT_ID or not NOTION_CLIENT_SECRET:
        raise RuntimeError("NOTION_CLIENT_ID or NOTION_CLIENT_SECRET is not set in .env")

    # Log what we're sending so mismatches are easy to spot
    logger.info(f"[notion] Exchanging code, redirect_uri={NOTION_REDIRECT_URI}")

    credentials = base64.b64encode(
        f"{NOTION_CLIENT_ID}:{NOTION_CLIENT_SECRET}".encode()
    ).decode()

    response = requests.post(
        NOTION_TOKEN_URL,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type":  "application/json",
        },
        json={
            "grant_type":   "authorization_code",
            "code":         code,
            "redirect_uri": NOTION_REDIRECT_URI,
        },
    )

    # Log the actual Notion error body before raising — makes 401/400 easy to debug
    if not response.ok:
        logger.error(f"[notion] Token exchange failed {response.status_code}: {response.text}")
        response.raise_for_status()

    data = response.json()

    user = await User.get(id=user_id)
    user.notion_token = data["access_token"]
    await user.save()

    workspace = data.get("workspace_name", "unknown")
    logger.info(f"[notion] Connected workspace '{workspace}' for {user.email}")
    return user
