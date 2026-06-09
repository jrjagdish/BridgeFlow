from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from debug import logger
from dotenv import load_dotenv
import os
import json
import threading
from contextlib import asynccontextmanager
from tortoise.contrib.fastapi import RegisterTortoise

# --- v1 imports (single-user, token.json based) ---
# from oauth import get_authorize, exchange_code_for_tokens, get_valid_access_token

# --- v2 imports (multi-user, DB + cookie based) ---
from v2.models import get_db_config
from v2.oauth import get_authorize_url, exchange_code_and_save_user
from v2.notion_oauth import get_notion_authorize_url, exchange_notion_code_and_save
from v2.auth import set_session_cookie, get_current_user_id

from scheduler import start_scheduler, stop_scheduler
from notion_client import verify_database_connection
from config import get_notion_database_id

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("----BridgeFlow Starting----")

    # v2: RegisterTortoise is a context manager that keeps the Tortoise connection
    # active across ALL request tasks for the app's lifetime.
    # v1 used init_db() (Tortoise.init()) which set global state — that broke in
    # Tortoise ORM 1.x because global state doesn't propagate to new request tasks.
    async with RegisterTortoise(app, config=get_db_config(), generate_schemas=True):

        # --- v1: init_db() without await (was a bug), and without context mgr ---
        # init_db()

        try:
            verify_database_connection(get_notion_database_id())
        except Exception as e:
            logger.error(f"Error : Coudn't access database ID: {e}")

        from sync import run_sync
        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()

        start_scheduler()
        yield
        stop_scheduler()

    logger.info("---BridgeFlow Stopped---")


app = FastAPI(title="BridgeFlow", lifespan=lifespan)


@app.get("/")
def health_check():
    logger.info("Health check endpoint called.")
    return {
        "status": "BridgeFlow is running",
        "docs": "/docs",
        "oauth": "/oauth/start",
        "trigger": "/sync/trigger",
        "status_check": "/status",
    }


# ---------------------------------------------------------------------------
# OAuth routes
# ---------------------------------------------------------------------------

# --- v1: POST, returned auth_url as JSON, no cookie, single user ---
# @app.post("/oauth/authorize")
# def authorize():
#     try:
#         auth_url = get_authorize()
#         return {"auth_url": auth_url}
#     except Exception as e:
#         logger.error(f"Error generating authorization URL: {e}")
#         raise HTTPException(status_code=500, detail="Error generating authorization URL")

@app.get("/oauth/start")
def oauth_start():
    """Return the Google consent URL. Open this in a browser to log in."""
    try:
        auth_url = get_authorize_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"[v2] Error generating auth URL: {e}")
        raise HTTPException(status_code=500, detail="Error generating authorization URL")


# --- v1: saved tokens to tokens.json, returned HTML, no cookie ---
# @app.get("/oauth/callback")
# def oauth_callback(code: str):
#     try:
#         tokens = exchange_code_for_tokens(code)
#         return HTMLResponse(
#             """ <h1> Connected to Google Sheets!</h1>
#             <p>BridgeFlow is now syncing your Sheet to Notion every 5 minutes.</p>
#             <p>Check the terminal for sync logs.</p>
#             <p><a href="/sync/trigger">Trigger a manual sync now</a></p>
#             <p><a href="/status">Check sync status</a></p> """
#         )
#     except Exception as e:
#         logger.error(f"Error exchanging code for tokens: {e}")
#         raise HTTPException(status_code=500, detail="Error exchanging code for tokens")

@app.get("/oauth/callback")
async def oauth_callback(code: str, response: Response):
    """
    Google redirects here after the user grants consent.
    Exchanges the code for tokens, saves them to DB, sets an HTTP-only session cookie.
    """
    try:
        user = await exchange_code_and_save_user(code)
        set_session_cookie(response, user.id)
        logger.info(f"[v2] OAuth complete for {user.email}")
        # Redirect to frontend — cookie travels with the redirect response
        redirect = RedirectResponse(url=FRONTEND_URL, status_code=302)
        set_session_cookie(redirect, user.id)
        logger.info(f"[v2] OAuth complete for {user.email}, redirecting to frontend")
        return redirect
    except Exception as e:
        logger.error(f"[v2] Error in OAuth callback: {e}")
        raise HTTPException(status_code=500, detail="Error exchanging code for tokens")


# ---------------------------------------------------------------------------
# Notion OAuth routes
# ---------------------------------------------------------------------------

@app.get("/oauth/notion/start")
def notion_oauth_start():
    """Return the Notion consent URL. Frontend redirects the browser here."""
    try:
        auth_url = get_notion_authorize_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"[notion] Error generating auth URL: {e}")
        raise HTTPException(status_code=500, detail="Error generating Notion auth URL")


@app.get("/oauth/notion/callback")
async def notion_oauth_callback(code: str, user_id: str = Depends(get_current_user_id)):
    """
    Notion redirects here after the user picks a workspace.
    Session cookie identifies which user is connecting — so Google OAuth
    must have been completed first to have a valid session.
    """
    try:
        await exchange_notion_code_and_save(code, user_id)
        return RedirectResponse(url=FRONTEND_URL, status_code=302)
    except Exception as e:
        logger.error(f"[notion] Error in OAuth callback: {e}")
        raise HTTPException(status_code=500, detail="Error connecting Notion account")


# ---------------------------------------------------------------------------
# User / session routes (consumed by the React frontend)
# ---------------------------------------------------------------------------

@app.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    """Return the current authenticated user's profile. 401 if not logged in."""
    from v2.models import User
    user = await User.get(id=user_id)
    return {
        "id": str(user.id),
        "email": user.email,
        "google_connected": bool(user.google_access_token),
        "notion_connected": bool(user.notion_token),
    }


@app.post("/logout")
def logout_user(response: Response):
    from v2.auth import clear_session_cookie
    clear_session_cookie(response)
    return {"status": "logged out"}


# ---------------------------------------------------------------------------
# Sync routes (v2 — reads user from session cookie)
# ---------------------------------------------------------------------------

# @app.get("/sync/trigger")
# async def trigger_sync(user_id: str = Depends(get_current_user_id)):
#     from sync import run_sync
#     thread = threading.Thread(target=run_sync, daemon=True)
#     thread.start()
#     return {"status": "Sync triggered", "user_id": user_id}

@app.get("/status")
def status(user_id: str = Depends(get_current_user_id)):
    from state_store import get_sync_logs
    raw = get_sync_logs(10)
    return {
        "logs": [
            {
                "sync_time":    row[0],
                "rows_fetched": row[1],
                "rows_created": row[2],
                "rows_updated": row[3],
                "errors":       json.loads(row[4]) if row[4] else [],
            }
            for row in raw
        ]
    }
