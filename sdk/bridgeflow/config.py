"""
bridgeflow.config — local credential storage for the CLI, at ~/.bridgeflow/config.json.

BRIDGEFLOW_API_KEY / BRIDGEFLOW_BASE_URL env vars take precedence over the file,
so the CLI works unmodified in CI.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

DEFAULT_BASE_URL = "http://localhost:8000"

CONFIG_DIR = Path(os.environ.get("BRIDGEFLOW_CONFIG_DIR", Path.home() / ".bridgeflow"))
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(api_key: str, base_url: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"api_key": api_key, "base_url": base_url}, indent=2))
    try:
        os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 0600 — best effort on Windows
    except OSError:
        pass


def clear_config() -> None:
    try:
        CONFIG_FILE.unlink()
    except FileNotFoundError:
        pass


def resolve_credentials() -> tuple[str | None, str]:
    """Return (api_key, base_url), preferring env vars over the config file."""
    cfg = load_config()
    api_key = os.environ.get("BRIDGEFLOW_API_KEY") or cfg.get("api_key")
    base_url = os.environ.get("BRIDGEFLOW_BASE_URL") or cfg.get("base_url") or DEFAULT_BASE_URL
    return api_key, base_url
