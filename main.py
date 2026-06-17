from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import Response, RedirectResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from debug import logger
from dotenv import load_dotenv
import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from tortoise.contrib.fastapi import RegisterTortoise

from v2.models import get_db_config
from v2.oauth import get_authorize_url, exchange_code_and_save_user
from v2.notion_oauth import get_notion_authorize_url, exchange_notion_code_and_save
from v2.auth import set_session_cookie, get_current_user_id
from v2.sheets_service import fetch_sheet_preview
from v2.notion_service import create_notion_page, create_notion_database


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class SheetPreviewRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: str = "Sheet1"


class PropertyMapping(BaseModel):
    sheet_col: str
    notion_property: str
    type: str = "rich_text"


class CreateDatabaseRequest(BaseModel):
    parent_page_id: Optional[str] = None  # if omitted, a new Notion page is created automatically
    title: str = "BridgeFlow Sync"
    properties: List[PropertyMapping]


class SaveConfigRequest(BaseModel):
    spreadsheet_id: Optional[str] = None
    sheet_name: Optional[str] = None
    notion_database_id: Optional[str] = None
    column_mappings: Optional[List[dict]] = None
    id_column: Optional[str] = None          # Sheet column used as unique row identifier
    sync_interval_minutes: Optional[int] = None

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


async def run_migrations():
    """Apply additive schema changes that generate_schemas won't handle."""
    from tortoise import connections
    conn = connections.get("default")
    await conn.execute_script(
        "ALTER TABLE user_configs ADD COLUMN IF NOT EXISTS id_column VARCHAR(255);"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("----BridgeFlow Starting----")
    async with RegisterTortoise(app, config=get_db_config(), generate_schemas=True):
        await run_migrations()
        yield
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


@app.post("/oauth/notion/disconnect")
async def notion_disconnect(user_id: str = Depends(get_current_user_id)):
    """Clear the user's Notion token so they can reconnect to a different workspace/page."""
    from v2.models import User
    user = await User.get(id=user_id)
    user.notion_token = None
    await user.save()
    logger.info(f"[notion] Disconnected for {user.email}")
    return {"status": "disconnected"}


# ---------------------------------------------------------------------------
# Sync routes (v2 — reads user from session cookie)
# ---------------------------------------------------------------------------

# @app.get("/sync/trigger")
# async def trigger_sync(user_id: str = Depends(get_current_user_id)):
#     from sync import run_sync
#     thread = threading.Thread(target=run_sync, daemon=True)
#     thread.start()
#     return {"status": "Sync triggered", "user_id": user_id}

@app.post("/sync/trigger")
async def trigger_sync(user_id: str = Depends(get_current_user_id)):
    """
    Manually trigger a sync for the current user.
    Returns job_id — poll GET /sync/jobs/{job_id} to track progress.
    The Celery worker must be running separately for the job to execute.
    """
    from v2.models import SyncJob
    from v2.tasks import sync_user

    job = await SyncJob.create(
        id=uuid.uuid4(),
        user_id=user_id,
        status="pending",
        triggered_by="manual",
    )
    task = sync_user.apply_async(args=[str(user_id), str(job.id)])
    job.celery_task_id = task.id
    await job.save()

    logger.info(f"[sync] Manual trigger user={user_id} job={job.id} celery={task.id}")
    return {"job_id": str(job.id), "celery_task_id": task.id, "status": "pending"}


@app.get("/sync/jobs")
async def list_sync_jobs(user_id: str = Depends(get_current_user_id), limit: int = 20):
    """Return the most recent sync jobs for the current user, newest first."""
    from v2.models import SyncJob

    jobs = await SyncJob.filter(user_id=user_id).order_by("-created_at").limit(limit)
    return [_job_to_dict(j) for j in jobs]


@app.get("/sync/jobs/{job_id}")
async def get_sync_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    """Return full details of a single sync job."""
    from v2.models import SyncJob

    job = await SyncJob.get_or_none(id=job_id, user_id=user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_dict(job)


@app.get("/sync/jobs/{job_id}/stream")
async def stream_job_status(job_id: str, user_id: str = Depends(get_current_user_id)):
    """
    SSE stream that emits the job's current state every second until it finishes.
    Frontend: const es = new EventSource('/sync/jobs/<id>/stream')
    """
    from v2.models import SyncJob

    async def _events():
        terminal = {"completed", "completed_with_errors", "failed"}
        last_payload = None
        while True:
            job = await SyncJob.get_or_none(id=job_id, user_id=user_id)
            if job is None:
                yield f"data: {json.dumps({'error': 'job not found'})}\n\n"
                return
            payload = json.dumps(_job_to_dict(job))
            if payload != last_payload:
                yield f"data: {payload}\n\n"
                last_payload = payload
            if job.status in terminal:
                return
            await asyncio.sleep(1)

    return StreamingResponse(
        _events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/sync/rows")
async def list_synced_rows(user_id: str = Depends(get_current_user_id), limit: int = 100):
    """Return all rows tracked in Notion for the current user (audit trail)."""
    from v2.models import SyncedRow

    rows = await SyncedRow.filter(user_id=user_id).order_by("-last_synced_at").limit(limit)
    return [
        {
            "row_id": r.row_id,
            "notion_page_id": r.notion_page_id,
            "status": r.status,
            "error_message": r.error_message,
            "last_synced_at": r.last_synced_at.isoformat() if r.last_synced_at else None,
        }
        for r in rows
    ]


def _job_to_dict(j) -> dict:
    return {
        "id": str(j.id),
        "status": j.status,
        "triggered_by": j.triggered_by,
        "celery_task_id": j.celery_task_id,
        "started_at": j.started_at.isoformat() if j.started_at else None,
        "finished_at": j.finished_at.isoformat() if j.finished_at else None,
        "rows_fetched": j.rows_fetched,
        "rows_created": j.rows_created,
        "rows_updated": j.rows_updated,
        "rows_skipped": j.rows_skipped,
        "errors": j.errors,
        "created_at": j.created_at.isoformat() if j.created_at else None,
    }


# ---------------------------------------------------------------------------
# Google Sheets — preview endpoint (uses the user's stored Google token)
# ---------------------------------------------------------------------------

@app.post("/sheets/preview")
async def sheets_preview(body: SheetPreviewRequest, user_id: str = Depends(get_current_user_id)):
    """
    Fetch the header row + first 5 data rows from the given spreadsheet.
    The user must have completed Google OAuth first (so their token is in DB).
    """
    try:
        headers, preview = await fetch_sheet_preview(
            user_id, body.spreadsheet_id.strip(), body.sheet_name.strip() or "Sheet1"
        )
        return {"headers": headers, "preview": preview}
    except Exception as e:
        logger.error(f"[sheets] preview failed: {e}")
        raise HTTPException(status_code=400, detail=f"Could not read spreadsheet: {e}")


# ---------------------------------------------------------------------------
# Notion — create a page, then a database inside it
# ---------------------------------------------------------------------------

@app.post("/notion/page")
async def notion_create_page(user_id: str = Depends(get_current_user_id)):
    """
    Create a new BridgeFlow page at the root of the user's Notion workspace.
    Returns the page_id to use as parent when creating a database.
    Requires the Notion integration to have workspace-level access.
    """
    try:
        result = await create_notion_page(user_id, title="BridgeFlow")
        return result
    except Exception as e:
        logger.error(f"[notion] create_page failed: {e}")
        raise HTTPException(status_code=400, detail=f"Could not create Notion page: {e}")


@app.post("/notion/database")
async def notion_create_database(body: CreateDatabaseRequest, user_id: str = Depends(get_current_user_id)):
    """
    Create a new Notion database with the given property schema.
    If parent_page_id is omitted, a 'BridgeFlow' page is created automatically
    in the user's Notion workspace and used as the parent.
    """
    try:
        parent_id = body.parent_page_id.strip() if body.parent_page_id else None

        if not parent_id:
            page = await create_notion_page(user_id, title=body.title.strip() or "BridgeFlow")
            parent_id = page["page_id"]
            logger.info(f"[notion] Auto-created parent page id={parent_id}")

        result = await create_notion_database(
            user_id,
            parent_id,
            body.title.strip() or "BridgeFlow Sync",
            [p.model_dump() for p in body.properties],
        )
        result["page_id"] = parent_id
        return result
    except Exception as e:
        logger.error(f"[notion] create_database failed: {e}")
        raise HTTPException(status_code=400, detail=f"Could not create Notion database: {e}")


# ---------------------------------------------------------------------------
# Config — persist per-user settings in the DB (replaces localStorage)
# ---------------------------------------------------------------------------

@app.get("/config")
async def get_config_route(user_id: str = Depends(get_current_user_id)):
    """Return this user's saved sync configuration."""
    from v2.models import UserConfig
    config, _ = await UserConfig.get_or_create(user_id=user_id)
    return {
        "spreadsheet_id":        config.spreadsheet_id or "",
        "sheet_name":            config.sheet_name or "Sheet1",
        "notion_database_id":    config.notion_database_id or "",
        "column_mappings":       config.column_mappings or [],
        "id_column":             config.id_column or "",
        "sync_interval_minutes": config.sync_interval_minutes,
    }


@app.post("/config")
async def save_config_route(body: SaveConfigRequest, user_id: str = Depends(get_current_user_id)):
    """Persist the user's sync configuration to the DB."""
    from v2.models import UserConfig
    config, _ = await UserConfig.get_or_create(user_id=user_id)
    if body.spreadsheet_id is not None:
        config.spreadsheet_id = body.spreadsheet_id
    if body.sheet_name is not None:
        config.sheet_name = body.sheet_name
    if body.notion_database_id is not None:
        config.notion_database_id = body.notion_database_id
    if body.column_mappings is not None:
        config.column_mappings = body.column_mappings
    if body.id_column is not None:
        config.id_column = body.id_column
    if body.sync_interval_minutes is not None:
        config.sync_interval_minutes = body.sync_interval_minutes
    await config.save()
    return {"status": "saved"}
