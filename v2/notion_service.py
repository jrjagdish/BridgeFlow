"""
v2/notion_service.py — Notion database creation using the user's stored Notion token.
"""

import requests
from debug import logger

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

_TYPE_SCHEMA = {
    "title":        {"title": {}},
    "rich_text":    {"rich_text": {}},
    "number":       {"number": {"format": "number"}},
    "select":       {"select": {}},
    "multi_select": {"multi_select": {}},
    "status":       {"status": {}},
    "date":         {"date": {}},
    "checkbox":     {"checkbox": {}},
    "url":          {"url": {}},
    "email":        {"email": {}},
    "phone_number": {"phone_number": {}},
}


def _format_uuid(raw: str) -> str:
    """Ensure a Notion ID is in xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx form."""
    s = raw.replace("-", "")
    if len(s) != 32:
        return raw
    return f"{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:]}"


async def create_notion_database(
    user_id: str,
    parent_page_id: str,
    title: str,
    properties: list,
) -> dict:
    """
    Create a new Notion database under parent_page_id.

    properties: list of {notion_property: str, type: str}
      - Exactly one entry must have type=="title"; it becomes Notion's title column.
      - If none has type=="title", a "Name" title column is prepended automatically.

    Returns: {database_id: str, url: str}
    """
    from v2.models import User
    user = await User.get(id=user_id)

    notion_props: dict = {}
    title_added = False

    for prop in properties:
        name = prop["notion_property"]
        ptype = prop.get("type", "rich_text")

        if ptype == "title" and not title_added:
            notion_props[name] = {"title": {}}
            title_added = True
        else:
            t = "rich_text" if ptype == "title" else ptype
            notion_props[name] = _TYPE_SCHEMA.get(t, {"rich_text": {}})

    if not title_added:
        notion_props = {"Name": {"title": {}}, **notion_props}

    body = {
        "parent": {"type": "page_id", "page_id": _format_uuid(parent_page_id)},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": notion_props,
    }

    resp = requests.post(
        f"{NOTION_API}/databases",
        headers={
            "Authorization": f"Bearer {user.notion_token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        json=body,
        timeout=15,
    )

    if not resp.ok:
        logger.error(f"[notion] create_database failed {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    db_id = data["id"].replace("-", "")
    logger.info(f"[notion] Created database '{title}' id={db_id}")
    return {"database_id": db_id, "url": data.get("url", "")}
