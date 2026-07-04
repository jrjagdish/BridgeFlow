import uuid
from tortoise.models import Model
from tortoise import fields
import os
import ssl
import urllib.parse
from dotenv import load_dotenv
load_dotenv()


def get_db_config() -> dict:
    """
    Build the Tortoise config dict from DATABASE_URL.

    Neon (and similar cloud Postgres providers) include ?ssl=require&channel_binding=require
    in their URLs. asyncpg rejects those as URL params — it needs ssl as an SSLContext object.
    We parse the URL, strip those params, and pass ssl directly in the credentials dict.
    """
    db_url = os.getenv("DATABASE_URL")
    parsed = urllib.parse.urlparse(db_url)
    ssl_ctx = ssl.create_default_context()

    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": parsed.hostname,
                    "port": parsed.port or 5432,
                    "user": parsed.username,
                    "password": parsed.password,
                    "database": parsed.path.lstrip("/"),
                    "ssl": ssl_ctx,
                },
            }
        },
        "apps": {
            "models": {
                "models": ["v2.models"],
                "default_connection": "default",
            }
        },
        "use_tz": True,
        "timezone": "UTC",
    }


# --- v1: init_db used Tortoise.init() which set global state.
#         In Tortoise ORM 1.x that global state doesn't propagate to new
#         request tasks — use RegisterTortoise in main.py lifespan instead. ---
# async def init_db():
#     from tortoise import Tortoise
#     await Tortoise.init(config=get_db_config())
#     await Tortoise.generate_schemas()


class User(Model):
    id = fields.UUIDField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    google_id = fields.CharField(max_length=255, unique=True)

    google_access_token = fields.TextField(null=True)
    google_refresh_token = fields.TextField(null=True)
    google_token_expires_at = fields.DatetimeField(null=True)

    notion_token = fields.CharField(max_length=512, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"


class UserConfig(Model):
    """Per-user sync configuration stored in the DB (replaces localStorage / config.json)."""
    user = fields.OneToOneField("models.User", related_name="config", on_delete=fields.CASCADE)
    spreadsheet_id = fields.CharField(max_length=255, null=True)
    sheet_name = fields.CharField(max_length=255, default="Sheet1")
    notion_database_id = fields.CharField(max_length=255, null=True)
    column_mappings = fields.JSONField(null=True)   # [{sheet_col, notion_property, type}]
    id_column = fields.CharField(max_length=255, null=True)  # Sheet column used as unique row ID
    sync_interval_minutes = fields.IntField(default=5)

    class Meta:
        table = "user_configs"


class SyncJob(Model):
    """Tracks every sync run (manual or scheduled). Never deleted — full audit trail."""
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="sync_jobs")
    status = fields.CharField(max_length=32, default="pending")
    # pending | running | completed | completed_with_errors | failed
    triggered_by = fields.CharField(max_length=32, default="manual")  # manual | scheduler
    celery_task_id = fields.CharField(max_length=255, null=True)
    started_at = fields.DatetimeField(null=True)
    finished_at = fields.DatetimeField(null=True)
    rows_fetched = fields.IntField(default=0)
    rows_created = fields.IntField(default=0)
    rows_updated = fields.IntField(default=0)
    rows_skipped = fields.IntField(default=0)
    errors = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "sync_jobs"


class Feedback(Model):
    """Freeform feedback submitted by a user via the in-app feedback widget."""
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="feedback")
    message = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "feedback"


class SyncedRow(Model):
    """
    Tracks every row that has been pushed to Notion.
    row_hash detects changes so unchanged rows are never re-pushed.
    Previous data is preserved even when errors occur — only error_message changes.
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="synced_rows")
    row_id = fields.CharField(max_length=512)         # Value of id_column from Google Sheets
    row_hash = fields.CharField(max_length=64)         # SHA-256 of row dict — detects changes
    notion_page_id = fields.CharField(max_length=255)  # Notion page to update on next sync
    last_synced_at = fields.DatetimeField(auto_now=True)
    last_sync_job = fields.ForeignKeyField("models.SyncJob", related_name="synced_rows", null=True)
    status = fields.CharField(max_length=32, default="synced")  # synced | error
    error_message = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "synced_rows"
        unique_together = [("user", "row_id")]
