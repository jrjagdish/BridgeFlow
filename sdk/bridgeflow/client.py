"""
bridgeflow.client — thin wrapper around the BridgeFlow REST API.

Authenticates every request with an API key (Authorization: Bearer <key>),
generated from the BridgeFlow web app under Settings -> API Access.
"""

from __future__ import annotations

from typing import Any

import requests

from .exceptions import APIError, AuthenticationError, ConnectionError as BridgeFlowConnectionError

DEFAULT_TIMEOUT = 30


class BridgeFlowClient:
    """
    A client for the BridgeFlow API.

        from bridgeflow import BridgeFlowClient

        client = BridgeFlowClient(api_key="bf_...", base_url="https://your-app.vercel.app")
        client.trigger_sync()
        for job in client.list_jobs():
            print(job["status"])
    """

    def __init__(self, api_key: str, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        if not api_key:
            raise AuthenticationError("No API key provided.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers["Authorization"] = f"Bearer {api_key}"

    # -- internal -----------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        try:
            resp = self._session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as e:
            raise BridgeFlowConnectionError(str(e)) from e

        if resp.status_code == 401:
            raise AuthenticationError("Invalid or expired API key. Run `bridgeflow login` again.")

        if not resp.ok:
            detail = resp.text
            try:
                detail = resp.json().get("detail", detail)
            except ValueError:
                pass
            raise APIError(resp.status_code, detail)

        if resp.status_code == 204 or not resp.content:
            return None
        return resp.json()

    # -- account / status -----------------------------------------------------

    def whoami(self) -> dict:
        """Return the authenticated user's profile."""
        return self._request("GET", "/me")

    def get_status(self) -> dict:
        """Last trigger time, last sync status, and active job count."""
        return self._request("GET", "/status")

    # -- config -----------------------------------------------------------

    def get_config(self) -> dict:
        return self._request("GET", "/config")

    def save_config(
        self,
        *,
        spreadsheet_id: str | None = None,
        sheet_name: str | None = None,
        notion_database_id: str | None = None,
        column_mappings: list[dict] | None = None,
        id_column: str | None = None,
        sync_interval_minutes: int | None = None,
    ) -> dict:
        body = {
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": sheet_name,
            "notion_database_id": notion_database_id,
            "column_mappings": column_mappings,
            "id_column": id_column,
            "sync_interval_minutes": sync_interval_minutes,
        }
        body = {k: v for k, v in body.items() if v is not None}
        return self._request("POST", "/config", json=body)

    # -- Google Sheets -----------------------------------------------------

    def preview_sheet(self, spreadsheet_id: str, sheet_name: str = "Sheet1") -> dict:
        """Returns {"headers": [...], "preview": [...]}."""
        return self._request(
            "POST",
            "/sheets/preview",
            json={"spreadsheet_id": spreadsheet_id, "sheet_name": sheet_name},
        )

    # -- Notion -----------------------------------------------------

    def create_notion_page(self, title: str = "BridgeFlow") -> dict:
        return self._request("POST", "/notion/page")

    def create_notion_database(
        self,
        title: str,
        properties: list[dict],
        parent_page_id: str | None = None,
    ) -> dict:
        """
        properties: [{"sheet_col": str, "notion_property": str, "type": str}, ...]
        """
        body = {"title": title, "properties": properties, "parent_page_id": parent_page_id}
        return self._request("POST", "/notion/database", json=body)

    # -- Sync -----------------------------------------------------

    def trigger_sync(self) -> dict:
        return self._request("POST", "/sync/trigger")

    def list_jobs(self, limit: int = 20) -> list[dict]:
        return self._request("GET", "/sync/jobs", params={"limit": limit})

    def get_job(self, job_id: str) -> dict:
        return self._request("GET", f"/sync/jobs/{job_id}")

    def list_rows(self, limit: int = 100) -> list[dict]:
        return self._request("GET", "/sync/rows", params={"limit": limit})
