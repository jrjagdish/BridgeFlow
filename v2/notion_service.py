"""
v2/notion_service.py — Notion page and database creation using the user's stored Notion token.
"""

import requests
from debug import logger

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _notion_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

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


async def create_notion_page(user_id: str, title: str = "BridgeFlow") -> dict:
    """
    Create a new page at the Notion workspace root.

    Requires the user's Notion token to have workspace-level access (granted
    during the Notion OAuth consent screen when the user selects 'All pages').

    Returns: {page_id: str, url: str}
    """
    from v2.models import User
    user = await User.get(id=user_id)

    body = {
        "parent": {"type": "workspace", "workspace": True},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
    }

    resp = requests.post(
        f"{NOTION_API}/pages",
        headers={
            "Authorization": f"Bearer {user.notion_token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        json=body,
        timeout=15,
    )

    if not resp.ok:
        logger.error(f"[notion] create_page failed {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    page_id = data["id"].replace("-", "")
    logger.info(f"[notion] Created page '{title}' id={page_id}")
    return {"page_id": page_id, "url": data.get("url", "")}


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


# ---------------------------------------------------------------------------
# Row sync helpers
# ---------------------------------------------------------------------------

def _build_notion_properties(row: dict, mappings: list) -> dict:
    """
    Convert a flat row dict to Notion property format using column mappings.

    mappings: [{sheet_col: str, notion_property: str, type: str}]
    Supported types: title, rich_text, number, select, multi_select,
                     checkbox, date, url, email, phone_number
    """
    props: dict = {}
    for m in mappings:
        sheet_col = m.get("sheet_col", "")
        notion_prop = m.get("notion_property", "")
        prop_type = m.get("type", "rich_text")
        value = row.get(sheet_col, "")

        if prop_type == "title":
            props[notion_prop] = {"title": [{"text": {"content": str(value)}}]}

        elif prop_type == "number":
            try:
                props[notion_prop] = {"number": float(value) if value != "" else None}
            except (ValueError, TypeError):
                props[notion_prop] = {"number": None}

        elif prop_type == "select":
            props[notion_prop] = {"select": {"name": str(value)} if value else None}

        elif prop_type == "multi_select":
            items = [v.strip() for v in str(value).split(",") if v.strip()]
            props[notion_prop] = {"multi_select": [{"name": i} for i in items]}

        elif prop_type == "checkbox":
            props[notion_prop] = {"checkbox": str(value).lower() in ("true", "yes", "1", "checked")}

        elif prop_type == "date":
            props[notion_prop] = {"date": {"start": str(value)} if value else None}

        elif prop_type == "url":
            props[notion_prop] = {"url": str(value) if value else None}

        elif prop_type == "email":
            props[notion_prop] = {"email": str(value) if value else None}

        elif prop_type == "phone_number":
            props[notion_prop] = {"phone_number": str(value) if value else None}

        else:  # rich_text (default)
            props[notion_prop] = {"rich_text": [{"text": {"content": str(value)}}]}

    return props


async def upsert_notion_row(
    user_id: str,
    database_id: str,
    notion_page_id: str | None,
    row: dict,
    mappings: list,
) -> str:
    """
    Create (notion_page_id=None) or update an existing Notion page with row data.
    Returns the Notion page ID (no dashes).
    """
    from v2.models import User
    user = await User.get(id=user_id)

    properties = _build_notion_properties(row, mappings)

    if notion_page_id is None:
        body = {
            "parent": {"type": "database_id", "database_id": _format_uuid(database_id)},
            "properties": properties,
        }
        resp = requests.post(
            f"{NOTION_API}/pages",
            headers=_notion_headers(user.notion_token),
            json=body,
            timeout=15,
        )
    else:
        resp = requests.patch(
            f"{NOTION_API}/pages/{_format_uuid(notion_page_id)}",
            headers=_notion_headers(user.notion_token),
            json={"properties": properties},
            timeout=15,
        )

    if not resp.ok:
        logger.error(f"[notion] upsert_row failed {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    return resp.json()["id"].replace("-", "")
