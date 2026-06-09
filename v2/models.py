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

    # --- v1 (single token string — too small, no expiry tracking) ---
    # google_tk = fields.CharField(max_length=255)
    # notion_tk = fields.CharField(max_length=255, null=True)

    # --- v2: split into proper fields so we can refresh per-user ---
    google_access_token = fields.TextField(null=True)
    google_refresh_token = fields.TextField(null=True)
    google_token_expires_at = fields.DatetimeField(null=True)

    # Notion token: user pastes this manually, not OAuth
    notion_token = fields.CharField(max_length=512, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"
