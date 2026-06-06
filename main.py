from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from debug import logger
from oauth import get_authorize, exchange_code_for_tokens, get_valid_access_token
import threading
from dotenv import load_dotenv
from state_store import init_db
from scheduler import start_scheduler, stop_scheduler
from notion_client import verify_database_connection
from config import get_notion_database_id
from contextlib import asynccontextmanager

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("----BridgeFlow Starting----")
    init_db()
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


@app.post("/oauth/authorize")
def authorize():
    try:
        auth_url = get_authorize()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise HTTPException(
            status_code=500, detail="Error generating authorization URL"
        )


@app.get("/oauth/callback")
def oauth_callback(code: str):
    try:
        tokens = exchange_code_for_tokens(code)
        return HTMLResponse(
            """ <h1> Connected to Google Sheets!</h1> 
            <p>BridgeFlow is now syncing your Sheet to Notion every 5 minutes.</p> 
            <p>Check the terminal for sync logs.</p> 
            <p><a href="/sync/trigger">Trigger a manual sync now</a></p> 
            <p><a href="/status">Check sync status</a></p> """
        )
    except Exception as e:
        logger.error(f"Error exchanging code for tokens: {e}")
        raise HTTPException(status_code=500, detail="Error exchanging code for tokens")


@app.get("/sync/trigger")
def trigger_sync():
    from sync import run_sync
    thread = threading.Thread(target=run_sync,daemon=True)
    thread.start()
    return {"status":"Sync triggered. See terminal for logs"}

@app.get("/status")
def status():
    from state_store import get_sync_logs
    return {"status":get_sync_logs(5)}