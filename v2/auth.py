"""
v2/auth.py — HTTP-only session cookie helpers.

In v1 there was no concept of sessions — one global tokens.json, one user.
In v2 we need to know WHICH user is making each request. We do this by:
  - setting an HTTP-only cookie containing the user's UUID after login
  - reading that cookie on every protected request to identify the user

The cookie holds only the user's UUID, never the actual Google token.
"""

from fastapi import Request, HTTPException
from fastapi.responses import Response

COOKIE_NAME = "bf_session"   # bf = BridgeFlow
COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days in seconds


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


def get_current_user_id(request: Request) -> str:
    """
    Read the session cookie and return the user UUID string.
    Raises HTTP 401 if the cookie is missing (user not logged in).

    Use this as a dependency in any route that needs to know the current user:

        @app.get("/sync/trigger")
        async def trigger(user_id: str = Depends(get_current_user_id)):
            token = await get_valid_access_token_for_user(user_id)
            ...
    """
    user_id = request.cookies.get(COOKIE_NAME)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated. Visit /oauth/start first.")
    return user_id


def clear_session_cookie(response: Response) -> None:
    """Remove the session cookie (logout)."""
    response.delete_cookie(key=COOKIE_NAME)
