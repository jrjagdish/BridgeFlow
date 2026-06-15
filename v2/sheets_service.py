"""
v2/sheets_service.py — per-user Google Sheets fetch using the DB-stored token.
"""

import requests
from v2.oauth import get_valid_access_token_for_user

SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"


async def fetch_sheet_preview(
    user_id: str,
    spreadsheet_id: str,
    sheet_name: str = "Sheet1",
    limit: int = 5,
):
    """
    Fetch the header row + first `limit` data rows from a Google Sheet.
    Uses the stored Google token for the given user (auto-refreshes if expired).

    Returns: (headers: list[str], preview_rows: list[dict])
    """
    token = await get_valid_access_token_for_user(user_id)
    url = f"{SHEETS_API}/{spreadsheet_id}/values/{sheet_name}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    resp.raise_for_status()

    values = resp.json().get("values", [])
    if not values:
        return [], []

    headers = values[0]
    preview = []
    for row in values[1: limit + 1]:
        padded = row + [""] * (len(headers) - len(row))
        preview.append(dict(zip(headers, padded)))

    return headers, preview
