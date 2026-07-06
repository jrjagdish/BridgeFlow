"""
v2/auth.py — HTTP-only session cookie helpers + API key auth.

In v1 there was no concept of sessions — one global tokens.json, one user.
In v2 we need to know WHICH user is making each request. We do this by:
  - setting an HTTP-only cookie containing the user's UUID after login
  - reading that cookie on every protected request to identify the user

The cookie holds only the user's UUID, never the actual Google token.

API keys (for the CLI/SDK, which can't hold a browser cookie) are issued
via POST /auth/api-key while the caller is cookie-authenticated. Only the
SHA-256 hash of the key is stored — the raw key is shown once, at creation.
"""

import hashlib
import secrets

from fastapi import Request, HTTPException
from fastapi.responses import Response

COOKIE_NAME = "bf_session"   # bf = BridgeFlow
COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days in seconds

API_KEY_PREFIX = "bf_"


def generate_api_key() -> str:
    """Return a new random API key (shown to the user once, never stored raw)."""
    return API_KEY_PREFIX + secrets.token_urlsafe(32)


def hash_api_key(raw_key: str) -> str:
    """SHA-256 hex digest of a raw API key, for storage/lookup."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def set_session_cookie(response: Response, user_id: str) -> None:
    """
    Attach an HTTP-only session cookie to the outgoing response.
    Call this right after creating/finding the user in the OAuth callback.

    httponly=True  → JS cannot read the cookie (XSS protection)
    samesite="lax" → sent on same-site navigations + top-level cross-site GETs
                     (covers the OAuth redirect back from Google)
    secure=False   → set to True in production when running over HTTPS
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=str(user_id),
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=True,   # TODO: set True in production (HTTPS only)
    )


async def get_current_user_id(request: Request) -> str:
    """
    Identify the current user from either an API key or the session cookie.
    Raises HTTP 401 if neither is present/valid.

    Checks, in order:
      1. `Authorization: Bearer <api_key>` header — used by the CLI/SDK.
      2. The bf_session cookie — used by the browser frontend.

    Use this as a dependency in any route that needs to know the current user:

        @app.get("/sync/trigger")
        async def trigger(user_id: str = Depends(get_current_user_id)):
            token = await get_valid_access_token_for_user(user_id)
            ...
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        raw_key = auth_header[len("Bearer "):].strip()
        from v2.models import User
        user = await User.get_or_none(api_key_hash=hash_api_key(raw_key))
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return str(user.id)

    user_id = request.cookies.get(COOKIE_NAME)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated. Visit /oauth/start first.")
    return user_id


def clear_session_cookie(response: Response) -> None:
    """Remove the session cookie (logout)."""
    response.delete_cookie(key=COOKIE_NAME)
