"""
bridgeflow.cli — command-line interface for the BridgeFlow API, built on the SDK client.

Install: pip install bridgeflow-cli
Usage:   bridgeflow login --api-key bf_... --base-url https://your-app.vercel.app
"""

from __future__ import annotations

import json
import sys
import time

import click

from . import config as cfgstore
from .client import BridgeFlowClient
from .exceptions import BridgeFlowError


def _client() -> BridgeFlowClient:
    api_key, base_url = cfgstore.resolve_credentials()
    if not api_key:
        click.echo("Not logged in. Run `bridgeflow login --api-key <key>` first.", err=True)
        sys.exit(1)
    return BridgeFlowClient(api_key=api_key, base_url=base_url)


def _print(data) -> None:
    click.echo(json.dumps(data, indent=2, default=str))


def _parse_mapping(raw: str) -> dict:
    """Parse 'sheet_col:notion_property:type' into a column-mapping dict."""
    parts = raw.split(":")
    if len(parts) not in (2, 3):
        raise click.BadParameter(
            f"'{raw}' — expected format sheet_col:notion_property[:type]"
        )
    sheet_col, notion_property = parts[0], parts[1]
    prop_type = parts[2] if len(parts) == 3 else "rich_text"
    return {"sheet_col": sheet_col, "notion_property": notion_property, "type": prop_type}


@click.group()
@click.version_option(package_name="bridgeflow-cli")
def main():
    """BridgeFlow CLI — sync Google Sheets to Notion from your terminal."""


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@main.command()
@click.option("--api-key", required=True, help="API key from BridgeFlow Settings -> API Access.")
@click.option("--base-url", default=cfgstore.DEFAULT_BASE_URL, show_default=True,
              help="URL of your BridgeFlow deployment.")
def login(api_key: str, base_url: str):
    """Save an API key and base URL locally for future commands."""
    try:
        BridgeFlowClient(api_key=api_key, base_url=base_url).whoami()
    except BridgeFlowError as e:
        click.echo(f"Login failed: {e}", err=True)
        sys.exit(1)
    cfgstore.save_config(api_key, base_url)
    click.echo(f"Logged in. Credentials saved to {cfgstore.CONFIG_FILE}")


@main.command()
def logout():
    """Remove the locally saved API key."""
    cfgstore.clear_config()
    click.echo("Logged out.")


@main.command()
def whoami():
    """Show the currently authenticated user."""
    _print(_client().whoami())


@main.command()
def status():
    """Show last sync trigger time and active job count."""
    _print(_client().get_status())


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@main.group()
def config():
    """View or update your sync configuration."""


@config.command("get")
def config_get():
    """Print the saved sync configuration."""
    _print(_client().get_config())


@config.command("set")
@click.option("--spreadsheet-id", default=None)
@click.option("--sheet-name", default=None)
@click.option("--notion-database-id", default=None)
@click.option("--id-column", default=None, help="Sheet column used as the unique row ID.")
@click.option("--sync-interval-minutes", default=None, type=int)
@click.option("--column-mapping", "column_mappings", multiple=True,
              help="sheet_col:notion_property[:type], repeatable. Replaces all existing mappings.")
def config_set(spreadsheet_id, sheet_name, notion_database_id, id_column,
               sync_interval_minutes, column_mappings):
    """Update one or more sync configuration fields."""
    mappings = [_parse_mapping(m) for m in column_mappings] if column_mappings else None
    result = _client().save_config(
        spreadsheet_id=spreadsheet_id,
        sheet_name=sheet_name,
        notion_database_id=notion_database_id,
        id_column=id_column,
        sync_interval_minutes=sync_interval_minutes,
        column_mappings=mappings,
    )
    _print(result)


# ---------------------------------------------------------------------------
# Google Sheets
# ---------------------------------------------------------------------------

@main.group()
def sheets():
    """Inspect a Google Sheet."""


@sheets.command("preview")
@click.option("--spreadsheet-id", required=True)
@click.option("--sheet-name", default="Sheet1", show_default=True)
def sheets_preview(spreadsheet_id, sheet_name):
    """Preview a sheet's header row and first few rows."""
    _print(_client().preview_sheet(spreadsheet_id, sheet_name))


# ---------------------------------------------------------------------------
# Notion
# ---------------------------------------------------------------------------

@main.group()
def notion():
    """Create Notion pages and databases."""


@notion.command("create-page")
@click.option("--title", default="BridgeFlow", show_default=True)
def notion_create_page(title):
    """Create a page at the root of your Notion workspace."""
    _print(_client().create_notion_page(title))


@notion.command("create-database")
@click.option("--title", default="BridgeFlow Sync", show_default=True)
@click.option("--parent-page-id", default=None, help="Existing page ID; auto-created if omitted.")
@click.option("--property", "properties", multiple=True, required=True,
              help="sheet_col:notion_property[:type], repeatable. Types: "
                   "title, rich_text, number, select, multi_select, status, date, checkbox, url, email, phone_number.")
def notion_create_database(title, parent_page_id, properties):
    """Create a Notion database with the given property schema."""
    props = [_parse_mapping(p) for p in properties]
    _print(_client().create_notion_database(title, props, parent_page_id))


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

@main.group()
def sync():
    """Trigger and inspect sync jobs."""


@sync.command("trigger")
@click.option("--wait/--no-wait", default=False, help="Poll until the job reaches a terminal state.")
def sync_trigger(wait):
    """Trigger a manual sync."""
    client = _client()
    job = client.trigger_sync()
    if not wait:
        _print(job)
        return

    terminal = {"completed", "completed_with_errors", "failed"}
    job_id = job["job_id"]
    while job.get("status") not in terminal:
        time.sleep(1)
        job = client.get_job(job_id)
    _print(job)


@sync.command("jobs")
@click.option("--limit", default=20, show_default=True)
def sync_jobs(limit):
    """List recent sync jobs."""
    _print(_client().list_jobs(limit))


@sync.command("job")
@click.argument("job_id")
def sync_job(job_id):
    """Show a single sync job by ID."""
    _print(_client().get_job(job_id))


@sync.command("rows")
@click.option("--limit", default=100, show_default=True)
def sync_rows(limit):
    """List synced rows (audit trail)."""
    _print(_client().list_rows(limit))


def run():
    try:
        main()
    except BridgeFlowError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    run()
