"""
v2/oauth.py — per-user token management stored in DB.

v1 equivalent: oauth.py (stores tokens in tokens.json for a single global user)
Key difference: every function takes a user_id or User object so tokens
are isolated per user. The HTTP-only session cookie tells us which user
is making the request; we never put the actual token in the cookie.
"""

import os
import base64
import json
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from debug import logger

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
# GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"  # not used — see _parse_id_token below

# openid + email added so Google includes an id_token in the token exchange response.
# That lets us extract google_id + email without a second HTTP call to userinfo.
# v1 only had spreadsheets.readonly (no user identity needed for single-user).
SCOPES = "openid email https://www.googleapis.com/auth/spreadsheets.readonly"


# ---------------------------------------------------------------------------
# Step 1 — build the Google consent URL (same as v1 get_authorize)
# ---------------------------------------------------------------------------

def get_authorize_url() -> str:
    """Return the Google OAuth consent URL to redirect the user to."""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",   # needed to get a refresh_token
        "prompt": "consent",        # force consent so refresh_token is always returned
    }
    url = requests.Request("GET", GOOGLE_AUTH_URL, params=params).prepare().url
    logger.info(f"[v2] Generated Google auth URL")
    return url


# ---------------------------------------------------------------------------
# Step 2 — exchange auth code for tokens + fetch Google profile
#           then create/update the User row in DB
# ---------------------------------------------------------------------------

async def exchange_code_and_save_user(code: str):
    """
    Exchange the OAuth code for tokens, fetch the user's Google profile,
    then create or update the User row in DB.

    Returns the User ORM object so the caller can set the session cookie.

    v1 equivalent: exchange_code_for_tokens() — but that saved to tokens.json
    and had no concept of which user.
    """
    from v2.models import User  # local import to avoid circular at module load

    # --- exchange code for tokens ---
    response = requests.post(GOOGLE_TOKEN_URL, data={
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    response.raise_for_status()
    token_data = response.json()

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data["expires_in"])

    # --- extract google_id + email from the id_token Google returned ---
    # No extra HTTP call needed. The id_token is a JWT; we only need the payload
    # (middle segment). We received it directly from Google over HTTPS so we
    # trust it without signature verification here.
    # v1 had no equivalent — it never needed to know who the user was.
    profile = _parse_id_token(token_data["id_token"])
    google_id = profile["sub"]   # stable unique ID from Google
    email = profile["email"]

    # --- create or update User in DB ---
    user, created = await User.get_or_create(
        google_id=google_id,
        defaults={"email": email},
    )

    user.email = email
    user.google_access_token = access_token
    user.google_token_expires_at = expires_at

    # Google only returns refresh_token on first consent; keep old one if absent
    if refresh_token:
        user.google_refresh_token = refresh_token

    await user.save()

    action = "Created" if created else "Updated"
    logger.info(f"[v2] {action} user {email} in DB (google_id={google_id})")
    return user


# ---------------------------------------------------------------------------
# Step 3 — get a valid access token for a user (refresh if expired)
#           call this before every Google Sheets API request
# ---------------------------------------------------------------------------

async def get_valid_access_token_for_user(user_id: str) -> str:
    """
    Load the user's tokens from DB and return a valid access token.
    Automatically refreshes if expired or about to expire (within 5 min).

    v1 equivalent: get_valid_access_token() — but that read from tokens.json
    """
    from v2.models import User

    user = await User.get(id=user_id)

    now = datetime.now(timezone.utc)
    expires_at = user.google_token_expires_at

    if expires_at is None or now >= expires_at - timedelta(minutes=5):
        logger.info(f"[v2] Token expired/expiring for {user.email}. Refreshing.")
        user = await _refresh_and_save(user)

    return user.google_access_token


# ---------------------------------------------------------------------------
# Internal — refresh token and persist to DB
# ---------------------------------------------------------------------------

async def _refresh_and_save(user):
    """
    Refresh the Google access token for this user and update DB.

    v1 equivalent: refresh_access_token() — but that saved to tokens.json
    """
    response = requests.post(GOOGLE_TOKEN_URL, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": user.google_refresh_token,
        "grant_type": "refresh_token",
    })
    response.raise_for_status()
    token_data = response.json()

    user.google_access_token = token_data["access_token"]
    user.google_token_expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=token_data["expires_in"])
    )
    # refresh_token is not returned on a refresh call — keep the existing one
    await user.save()

    logger.info(f"[v2] Refreshed access token for {user.email}")
    return user


# ---------------------------------------------------------------------------
# Internal — decode the JWT id_token without a network call
# ---------------------------------------------------------------------------

def _parse_id_token(id_token: str) -> dict:
    """
    Decode the payload segment of a Google id_token (JWT).
    JWTs are: base64(header).base64(payload).signature
    We only need the payload which contains 'sub' (google_id) and 'email'.
    """
    payload_segment = id_token.split(".")[1]
    # base64url may be missing padding — pad to a multiple of 4
    padding = 4 - len(payload_segment) % 4
    payload_segment += "=" * (padding % 4)
    return json.loads(base64.urlsafe_b64decode(payload_segment))
