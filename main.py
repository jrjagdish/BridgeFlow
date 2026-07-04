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

import inngest.fast_api

from v2.models import get_db_config
from v2.oauth import get_authorize_url, exchange_code_and_save_user
from v2.notion_oauth import get_notion_authorize_url, exchange_notion_code_and_save
from v2.auth import set_session_cookie, get_current_user_id
from v2.sheets_service import fetch_sheet_preview
from v2.notion_service import create_notion_page, create_notion_database
from v2.inngest_client import inngest_client
from v2.inngest_functions import functions as inngest_functions


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
    parent_page_id: Optional[str] = None
    title: str = "BridgeFlow Sync"
    properties: List[PropertyMapping]


class SaveConfigRequest(BaseModel):
    spreadsheet_id: Optional[str] = None
    sheet_name: Optional[str] = None
    notion_database_id: Optional[str] = None
    column_mappings: Optional[List[dict]] = None
    id_column: Optional[str] = None
    sync_interval_minutes: Optional[int] = None


class FeedbackRequest(BaseModel):
    message: str

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


async def run_migrations():
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

# Inngest handles time-based (scheduled) runs — replaces Celery Beat, which
# can't run as a long-lived process on Vercel's serverless functions.
inngest.fast_api.serve(app, inngest_client, inngest_functions)


@app.get("/")
def health_check():
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

@app.get("/oauth/start")
def oauth_start():
    try:
        auth_url = get_authorize_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"[v2] Error generating auth URL: {e}")
        raise HTTPException(status_code=500, detail="Error generating authorization URL")


@app.get("/oauth/callback")
async def oauth_callback(code: str, response: Response):
    try:
        user = await exchange_code_and_save_user(code)
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
    try:
        auth_url = get_notion_authorize_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"[notion] Error generating auth URL: {e}")
        raise HTTPException(status_code=500, detail="Error generating Notion auth URL")


@app.get("/oauth/notion/callback")
async def notion_oauth_callback(code: str, user_id: str = Depends(get_current_user_id)):
    try:
        await exchange_notion_code_and_save(code, user_id)
        return RedirectResponse(url=FRONTEND_URL, status_code=302)
    except Exception as e:
        logger.error(f"[notion] Error in OAuth callback: {e}")
        raise HTTPException(status_code=500, detail="Error connecting Notion account")


# ---------------------------------------------------------------------------
# User / session routes
# ---------------------------------------------------------------------------

@app.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    from v2.models import User
    try:
        user = await User.get(id=user_id)
        return {
            "id": str(user.id),
            "email": user.email,
            "google_connected": bool(user.google_access_token),
            "notion_connected": bool(user.notion_token),
        }
    except Exception as e:
        logger.error(f"[me] Failed to fetch user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")


@app.post("/logout")
def logout_user(response: Response):
    from v2.auth import clear_session_cookie
    clear_session_cookie(response)
    return {"status": "logged out"}


@app.post("/oauth/notion/disconnect")
async def notion_disconnect(user_id: str = Depends(get_current_user_id)):
    from v2.models import User
    try:
        user = await User.get(id=user_id)
        user.notion_token = None
        await user.save()
        logger.info(f"[notion] Disconnected for {user.email}")
        return {"status": "disconnected"}
    except Exception as e:
        logger.error(f"[notion] Disconnect failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to disconnect Notion account")


# ---------------------------------------------------------------------------
# Sync routes
# ---------------------------------------------------------------------------

@app.post("/sync/trigger")
async def trigger_sync(user_id: str = Depends(get_current_user_id)):
    from v2.models import SyncJob
    from v2.tasks import _do_sync
    try:
        job = await SyncJob.create(
            id=uuid.uuid4(),
            user_id=user_id,
            status="pending",
            triggered_by="manual",
        )
        logger.info(f"[sync] Manual trigger user={user_id} job={job.id}")
        await _do_sync(str(user_id), str(job.id), manage_db=False)
        await job.refresh_from_db()
        return {"job_id": str(job.id), "status": job.status}
    except Exception as e:
        logger.error(f"[sync] Trigger failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger sync")


# ---------------------------------------------------------------------------
# Feedback route
# ---------------------------------------------------------------------------

@app.post("/feedback")
async def submit_feedback(body: FeedbackRequest, user_id: str = Depends(get_current_user_id)):
    from v2.models import Feedback
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Feedback message cannot be empty")
    if len(message) > 2000:
        raise HTTPException(status_code=400, detail="Feedback message is too long (max 2000 characters)")
    try:
        await Feedback.create(id=uuid.uuid4(), user_id=user_id, message=message)
        logger.info(f"[feedback] Received feedback from user {user_id}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"[feedback] Failed to save feedback for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@app.get("/sync/jobs")
async def list_sync_jobs(user_id: str = Depends(get_current_user_id), limit: int = 20):
    from v2.models import SyncJob
    try:
        jobs = await SyncJob.filter(user_id=user_id).order_by("-created_at").limit(limit)
        return [_job_to_dict(j) for j in jobs]
    except Exception as e:
        logger.error(f"[sync] list_jobs failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to list sync jobs")


@app.get("/sync/jobs/{job_id}")
async def get_sync_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    from v2.models import SyncJob
    try:
        job = await SyncJob.get_or_none(id=job_id, user_id=user_id)
        if not job:
            logger.debug(f"[sync] Job {job_id} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Job not found")
        return _job_to_dict(job)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[sync] get_job failed job={job_id} user={user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sync job")


@app.get("/sync/jobs/{job_id}/stream")
async def stream_job_status(job_id: str, user_id: str = Depends(get_current_user_id)):
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
    from v2.models import SyncedRow
    try:
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
    except Exception as e:
        logger.error(f"[sync] list_rows failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to list synced rows")


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
# Status route — last trigger time + active job count for current user
# ---------------------------------------------------------------------------

@app.get("/status")
async def get_status(user_id: str = Depends(get_current_user_id)):
    """Show when sync was last triggered and current active-job count for the user."""
    from v2.models import SyncJob
    from datetime import datetime, timezone
    try:
        last_job = await SyncJob.filter(user_id=user_id).order_by("-created_at").first()
        active_count = await SyncJob.filter(
            user_id=user_id, status__in=["pending", "running"]
        ).count()
        return {
            "server_time": datetime.now(timezone.utc).isoformat(),
            "last_triggered_at": last_job.created_at.isoformat() if last_job else None,
            "last_triggered_by": last_job.triggered_by if last_job else None,
            "last_sync_status": last_job.status if last_job else None,
            "active_jobs": active_count,
        }
    except Exception as e:
        logger.error(f"[status] Failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve status")


# ---------------------------------------------------------------------------
# Google Sheets — preview endpoint
# ---------------------------------------------------------------------------

@app.post("/sheets/preview")
async def sheets_preview(body: SheetPreviewRequest, user_id: str = Depends(get_current_user_id)):
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
    try:
        result = await create_notion_page(user_id, title="BridgeFlow")
        return result
    except Exception as e:
        logger.error(f"[notion] create_page failed: {e}")
        raise HTTPException(status_code=400, detail=f"Could not create Notion page: {e}")


@app.post("/notion/database")
async def notion_create_database(body: CreateDatabaseRequest, user_id: str = Depends(get_current_user_id)):
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
# Config — persist per-user settings
# ---------------------------------------------------------------------------

@app.get("/config")
async def get_config_route(user_id: str = Depends(get_current_user_id)):
    from v2.models import UserConfig
    try:
        config, _ = await UserConfig.get_or_create(user_id=user_id)
        return {
            "spreadsheet_id":        config.spreadsheet_id or "",
            "sheet_name":            config.sheet_name or "Sheet1",
            "notion_database_id":    config.notion_database_id or "",
            "column_mappings":       config.column_mappings or [],
            "id_column":             config.id_column or "",
            "sync_interval_minutes": config.sync_interval_minutes,
        }
    except Exception as e:
        logger.error(f"[config] get failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load config")


@app.post("/config")
async def save_config_route(body: SaveConfigRequest, user_id: str = Depends(get_current_user_id)):
    from v2.models import UserConfig
    try:
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
    except Exception as e:
        logger.error(f"[config] save failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save config")
