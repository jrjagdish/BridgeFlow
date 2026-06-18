"""
Unit tests for all BridgeFlow routes.

All DB and external-service calls are mocked — no real PostgreSQL or Redis needed.
Run with:  pytest
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from v2.auth import COOKIE_NAME, get_current_user_id

USER_ID = "00000000-0000-0000-0000-000000000001"

# Override the session-cookie dependency globally for every test in this module
app.dependency_overrides[get_current_user_id] = lambda: USER_ID


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _qs(items=None):
    """Return a mock Tortoise queryset that supports chaining and awaiting."""
    items = items or []
    qs = AsyncMock(return_value=items)
    qs.order_by = MagicMock(return_value=qs)
    qs.limit = MagicMock(return_value=qs)
    qs.first = AsyncMock(return_value=items[0] if items else None)
    qs.count = AsyncMock(return_value=len(items))
    qs.exists = AsyncMock(return_value=bool(items))
    return qs


def _job(status="completed", triggered_by="manual"):
    j = MagicMock()
    j.id = uuid.uuid4()
    j.status = status
    j.triggered_by = triggered_by
    j.celery_task_id = "celery-abc-123"
    j.started_at = datetime(2026, 6, 18, 10, 0, tzinfo=timezone.utc)
    j.finished_at = datetime(2026, 6, 18, 10, 1, tzinfo=timezone.utc)
    j.created_at = datetime(2026, 6, 18, 10, 0, tzinfo=timezone.utc)
    j.rows_fetched = 10
    j.rows_created = 5
    j.rows_updated = 3
    j.rows_skipped = 2
    j.errors = []
    j.save = AsyncMock()
    return j


def _user():
    u = MagicMock()
    u.id = uuid.UUID(USER_ID)
    u.email = "test@example.com"
    u.google_access_token = "google-token"
    u.notion_token = "notion-token"
    u.save = AsyncMock()
    return u


def _config():
    c = MagicMock()
    c.spreadsheet_id = "sheet123"
    c.sheet_name = "Sheet1"
    c.notion_database_id = "notion_db123"
    c.column_mappings = [{"sheet_col": "Name", "notion_property": "Name", "type": "title"}]
    c.id_column = "ID"
    c.sync_interval_minutes = 5
    c.save = AsyncMock()
    return c


@pytest.fixture
async def client():
    """AsyncClient with DB lifespan fully mocked out."""
    class _NoOpCM:
        async def __aenter__(self): return None
        async def __aexit__(self, *a): return False

    with patch("main.RegisterTortoise", return_value=_NoOpCM()), \
         patch("main.run_migrations", new_callable=AsyncMock), \
         patch("main.get_db_config", return_value={}):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as c:
            yield c


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

async def test_health_check(client):
    r = await client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "BridgeFlow is running"
    assert "oauth" in data
    assert "trigger" in data
    assert "status_check" in data


# ---------------------------------------------------------------------------
# OAuth — Google
# ---------------------------------------------------------------------------

async def test_oauth_start_success(client):
    with patch("main.get_authorize_url", return_value="https://accounts.google.com/auth"):
        r = await client.get("/oauth/start")
    assert r.status_code == 200
    assert "auth_url" in r.json()


async def test_oauth_start_error(client):
    with patch("main.get_authorize_url", side_effect=Exception("missing config")):
        r = await client.get("/oauth/start")
    assert r.status_code == 500


async def test_oauth_callback_success(client):
    with patch("main.exchange_code_and_save_user", new_callable=AsyncMock, return_value=_user()):
        r = await client.get("/oauth/callback?code=test_code", follow_redirects=False)
    assert r.status_code == 302


async def test_oauth_callback_error(client):
    with patch("main.exchange_code_and_save_user", new_callable=AsyncMock,
               side_effect=Exception("bad token")):
        r = await client.get("/oauth/callback?code=bad")
    assert r.status_code == 500


# ---------------------------------------------------------------------------
# OAuth — Notion
# ---------------------------------------------------------------------------

async def test_notion_oauth_start_success(client):
    with patch("main.get_notion_authorize_url", return_value="https://api.notion.com/oauth"):
        r = await client.get("/oauth/notion/start")
    assert r.status_code == 200
    assert "auth_url" in r.json()


async def test_notion_oauth_start_error(client):
    with patch("main.get_notion_authorize_url", side_effect=RuntimeError("no client id")):
        r = await client.get("/oauth/notion/start")
    assert r.status_code == 500


async def test_notion_oauth_callback_success(client):
    with patch("main.exchange_notion_code_and_save", new_callable=AsyncMock):
        r = await client.get("/oauth/notion/callback?code=abc", follow_redirects=False)
    assert r.status_code == 302


async def test_notion_oauth_callback_error(client):
    with patch("main.exchange_notion_code_and_save", new_callable=AsyncMock,
               side_effect=Exception("bad code")):
        r = await client.get("/oauth/notion/callback?code=bad")
    assert r.status_code == 500


# ---------------------------------------------------------------------------
# /me, /logout, /oauth/notion/disconnect
# ---------------------------------------------------------------------------

async def test_get_me(client):
    with patch("v2.models.User.get", new_callable=AsyncMock, return_value=_user()):
        r = await client.get("/me")
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "test@example.com"
    assert data["google_connected"] is True
    assert data["notion_connected"] is True


async def test_get_me_db_error(client):
    with patch("v2.models.User.get", new_callable=AsyncMock, side_effect=Exception("db down")):
        r = await client.get("/me")
    assert r.status_code == 500


async def test_logout(client):
    r = await client.post("/logout")
    assert r.status_code == 200
    assert r.json()["status"] == "logged out"


async def test_notion_disconnect(client):
    mock_user = _user()
    with patch("v2.models.User.get", new_callable=AsyncMock, return_value=mock_user):
        r = await client.post("/oauth/notion/disconnect")
    assert r.status_code == 200
    assert r.json()["status"] == "disconnected"
    mock_user.save.assert_awaited_once()


async def test_notion_disconnect_error(client):
    with patch("v2.models.User.get", new_callable=AsyncMock, side_effect=Exception("db error")):
        r = await client.post("/oauth/notion/disconnect")
    assert r.status_code == 500


# ---------------------------------------------------------------------------
# /sync/trigger
# ---------------------------------------------------------------------------

async def test_trigger_sync_success(client):
    mock_job = _job(status="pending")
    mock_task = MagicMock()
    mock_task.id = "celery-task-123"

    with patch("v2.models.SyncJob.create", new_callable=AsyncMock, return_value=mock_job), \
         patch("v2.tasks.sync_user") as mock_celery:
        mock_celery.apply_async.return_value = mock_task
        r = await client.post("/sync/trigger")

    assert r.status_code == 200
    data = r.json()
    assert "job_id" in data
    assert data["status"] == "pending"


async def test_trigger_sync_error(client):
    with patch("v2.models.SyncJob.create", new_callable=AsyncMock,
               side_effect=Exception("db error")):
        r = await client.post("/sync/trigger")
    assert r.status_code == 500


# ---------------------------------------------------------------------------
# /sync/jobs
# ---------------------------------------------------------------------------

async def test_list_sync_jobs(client):
    mock_job = _job()
    with patch("v2.models.SyncJob.filter", return_value=_qs([mock_job])):
        r = await client.get("/sync/jobs")
    assert r.status_code == 200
    jobs = r.json()
    assert len(jobs) == 1
    assert jobs[0]["status"] == "completed"


async def test_list_sync_jobs_empty(client):
    with patch("v2.models.SyncJob.filter", return_value=_qs([])):
        r = await client.get("/sync/jobs")
    assert r.status_code == 200
    assert r.json() == []


async def test_list_sync_jobs_custom_limit(client):
    jobs = [_job() for _ in range(3)]
    with patch("v2.models.SyncJob.filter", return_value=_qs(jobs)):
        r = await client.get("/sync/jobs?limit=3")
    assert r.status_code == 200
    assert len(r.json()) == 3


async def test_list_sync_jobs_error(client):
    with patch("v2.models.SyncJob.filter", side_effect=Exception("db error")):
        r = await client.get("/sync/jobs")
    assert r.status_code == 500


# ---------------------------------------------------------------------------
# /sync/jobs/{job_id}
# ---------------------------------------------------------------------------

async def test_get_sync_job_found(client):
    mock_job = _job()
    with patch("v2.models.SyncJob.get_or_none", new_callable=AsyncMock, return_value=mock_job):
        r = await client.get(f"/sync/jobs/{mock_job.id}")
    assert r.status_code == 200
    assert r.json()["status"] == "completed"


async def test_get_sync_job_not_found(client):
    with patch("v2.models.SyncJob.get_or_none", new_callable=AsyncMock, return_value=None):
        r = await client.get(f"/sync/jobs/{uuid.uuid4()}")
    assert r.status_code == 404


async def test_get_sync_job_error(client):
    with patch("v2.models.SyncJob.get_or_none", new_callable=AsyncMock,
               side_effect=Exception("db error")):
        r = await client.get(f"/sync/jobs/{uuid.uuid4()}")
    assert r.status_code == 500


# ---------------------------------------------------------------------------
# /sync/rows
# ---------------------------------------------------------------------------

async def test_list_synced_rows(client):
    row = MagicMock()
    row.row_id = "row1"
    row.notion_page_id = "page1"
    row.status = "synced"
    row.error_message = None
    row.last_synced_at = datetime(2026, 6, 18, 10, 0, tzinfo=timezone.utc)

    with patch("v2.models.SyncedRow.filter", return_value=_qs([row])):
        r = await client.get("/sync/rows")

    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["row_id"] == "row1"
    assert data[0]["status"] == "synced"


async def test_list_synced_rows_empty(client):
    with patch("v2.models.SyncedRow.filter", return_value=_qs([])):
        r = await client.get("/sync/rows")
    assert r.status_code == 200
    assert r.json() == []


async def test_list_synced_rows_error(client):
    with patch("v2.models.SyncedRow.filter", side_effect=Exception("db error")):
        r = await client.get("/sync/rows")
    assert r.status_code == 500


# ---------------------------------------------------------------------------
# /status
# ---------------------------------------------------------------------------

async def test_get_status_with_last_job(client):
    last = _job(triggered_by="manual")
    first_qs = _qs([last])
    count_qs = _qs([])

    with patch("v2.models.SyncJob.filter") as mock_filter:
        mock_filter.side_effect = [first_qs, count_qs]
        r = await client.get("/status")

    assert r.status_code == 200
    data = r.json()
    assert "server_time" in data
    assert data["last_triggered_by"] == "manual"
    assert data["last_sync_status"] == "completed"
    assert data["active_jobs"] == 0


async def test_get_status_no_jobs(client):
    first_qs = _qs([])
    count_qs = _qs([])

    with patch("v2.models.SyncJob.filter") as mock_filter:
        mock_filter.side_effect = [first_qs, count_qs]
        r = await client.get("/status")

    assert r.status_code == 200
    data = r.json()
    assert data["last_triggered_at"] is None
    assert data["active_jobs"] == 0


async def test_get_status_with_active_jobs(client):
    last = _job(status="running", triggered_by="scheduler")
    first_qs = _qs([last])
    count_qs = _qs([last])  # 1 active job

    with patch("v2.models.SyncJob.filter") as mock_filter:
        mock_filter.side_effect = [first_qs, count_qs]
        r = await client.get("/status")

    assert r.status_code == 200
    assert r.json()["active_jobs"] == 1


async def test_get_status_error(client):
    with patch("v2.models.SyncJob.filter", side_effect=Exception("db error")):
        r = await client.get("/status")
    assert r.status_code == 500


# ---------------------------------------------------------------------------
# /sheets/preview
# ---------------------------------------------------------------------------

async def test_sheets_preview_success(client):
    with patch("main.fetch_sheet_preview", new_callable=AsyncMock,
               return_value=(["Name", "Email"], [{"Name": "Alice", "Email": "alice@test.com"}])):
        r = await client.post("/sheets/preview",
                              json={"spreadsheet_id": "abc123", "sheet_name": "Sheet1"})
    assert r.status_code == 200
    data = r.json()
    assert data["headers"] == ["Name", "Email"]
    assert len(data["preview"]) == 1


async def test_sheets_preview_error(client):
    with patch("main.fetch_sheet_preview", new_callable=AsyncMock,
               side_effect=Exception("no access")):
        r = await client.post("/sheets/preview",
                              json={"spreadsheet_id": "bad", "sheet_name": "Sheet1"})
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# /notion/page
# ---------------------------------------------------------------------------

async def test_notion_create_page_success(client):
    with patch("main.create_notion_page", new_callable=AsyncMock,
               return_value={"page_id": "page123"}):
        r = await client.post("/notion/page")
    assert r.status_code == 200
    assert r.json()["page_id"] == "page123"


async def test_notion_create_page_error(client):
    with patch("main.create_notion_page", new_callable=AsyncMock,
               side_effect=Exception("notion error")):
        r = await client.post("/notion/page")
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# /notion/database
# ---------------------------------------------------------------------------

_DB_BODY = {
    "title": "Test DB",
    "properties": [{"sheet_col": "Name", "notion_property": "Name", "type": "title"}],
}


async def test_notion_create_database_auto_page(client):
    with patch("main.create_notion_page", new_callable=AsyncMock,
               return_value={"page_id": "page123"}), \
         patch("main.create_notion_database", new_callable=AsyncMock,
               return_value={"database_id": "db456"}):
        r = await client.post("/notion/database", json=_DB_BODY)
    assert r.status_code == 200
    data = r.json()
    assert data["database_id"] == "db456"
    assert data["page_id"] == "page123"


async def test_notion_create_database_with_parent(client):
    with patch("main.create_notion_database", new_callable=AsyncMock,
               return_value={"database_id": "db456"}):
        r = await client.post("/notion/database",
                              json={**_DB_BODY, "parent_page_id": "existing-page"})
    assert r.status_code == 200


async def test_notion_create_database_error(client):
    with patch("main.create_notion_page", new_callable=AsyncMock,
               side_effect=Exception("page create failed")):
        r = await client.post("/notion/database", json=_DB_BODY)
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# /config
# ---------------------------------------------------------------------------

async def test_get_config(client):
    with patch("v2.models.UserConfig.get_or_create", new_callable=AsyncMock,
               return_value=(_config(), False)):
        r = await client.get("/config")
    assert r.status_code == 200
    data = r.json()
    assert data["spreadsheet_id"] == "sheet123"
    assert data["sheet_name"] == "Sheet1"
    assert data["id_column"] == "ID"


async def test_get_config_error(client):
    with patch("v2.models.UserConfig.get_or_create", new_callable=AsyncMock,
               side_effect=Exception("db error")):
        r = await client.get("/config")
    assert r.status_code == 500


async def test_save_config_full(client):
    mock_cfg = _config()
    with patch("v2.models.UserConfig.get_or_create", new_callable=AsyncMock,
               return_value=(mock_cfg, False)):
        r = await client.post("/config", json={
            "spreadsheet_id": "new_sheet",
            "sheet_name": "NewSheet",
            "notion_database_id": "new_db",
            "id_column": "ID",
            "sync_interval_minutes": 10,
        })
    assert r.status_code == 200
    assert r.json()["status"] == "saved"
    mock_cfg.save.assert_awaited_once()


async def test_save_config_partial(client):
    mock_cfg = _config()
    with patch("v2.models.UserConfig.get_or_create", new_callable=AsyncMock,
               return_value=(mock_cfg, False)):
        r = await client.post("/config", json={"sync_interval_minutes": 15})
    assert r.status_code == 200
    assert mock_cfg.sync_interval_minutes == 15


async def test_save_config_error(client):
    with patch("v2.models.UserConfig.get_or_create", new_callable=AsyncMock,
               side_effect=Exception("db error")):
        r = await client.post("/config", json={"spreadsheet_id": "x"})
    assert r.status_code == 500


# ---------------------------------------------------------------------------
# Unauthenticated access
# ---------------------------------------------------------------------------

async def test_unauthenticated_protected_routes():
    """Protected routes must return 401 when no session cookie is present."""
    # Temporarily remove the auth override
    app.dependency_overrides.pop(get_current_user_id, None)

    class _NoOpCM:
        async def __aenter__(self): return None
        async def __aexit__(self, *a): return False

    try:
        with patch("main.RegisterTortoise", return_value=_NoOpCM()), \
             patch("main.run_migrations", new_callable=AsyncMock), \
             patch("main.get_db_config", return_value={}):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                for path, method in [
                    ("/me", "GET"),
                    ("/sync/trigger", "POST"),
                    ("/sync/jobs", "GET"),
                    ("/sync/rows", "GET"),
                    ("/config", "GET"),
                    ("/status", "GET"),
                ]:
                    r = await getattr(c, method.lower())(path)
                    assert r.status_code == 401, f"{method} {path} should be 401"
    finally:
        app.dependency_overrides[get_current_user_id] = lambda: USER_ID
