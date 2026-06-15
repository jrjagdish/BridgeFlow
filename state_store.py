import json
from datetime import datetime, timedelta
import sqlite3
from debug import logger

DB_FILE = "BridgeFlow.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS row_state (
                   task_id TEXT PRIMARY KEY,
                   row_data TEXT,
                   notion_page_id TEXT,
                   last_synced TIMESTAMP
                   )""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS sync_log (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   sync_time TIMESTAMP,
                   row_fetched INTEGER DEFAULT 0,
                   row_created INTEGER DEFAULT 0,
                   row_updated INTEGER DEFAULT 0,
                   error_message TEXT
                   )""")
    conn.commit()
    logger.info("Database initialized with tables: row_state, sync_log")
    conn.close()


def get_row_state(task_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT row_data,notion_page_id FROM row_state WHERE task_id = ?""",
        (task_id,),
    )
    result = cursor.fetchone()
    conn.close()
    return result


def save_row_state(task_id: str, row_data: dict, notion_page_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO row_state (task_id, row_data, notion_page_id, last_synced) 
                      VALUES (?, ?, ?, ?)""",
        (task_id, json.dumps(row_data), notion_page_id, datetime.now().isoformat()),
    )
    conn.commit()
    logger.info(
        f"Saved state for task_id: {task_id} with notion_page_id: {notion_page_id}"
    )
    conn.close()


def log_sync(
    row_fetched: int, row_created: int, row_updated: int, error_message: list = None
):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO sync_log (sync_time, row_fetched, row_created, row_updated, error_message) 
                      VALUES (?, ?, ?, ?, ?)""",
        (
            datetime.now().isoformat(),
            row_fetched,
            row_created,
            row_updated,
            json.dumps(error_message) if error_message else None,
        ),
    )
    conn.commit()
    logger.info(
        f"Logged sync: fetched={row_fetched}, created={row_created}, updated={row_updated}, error={error_message}"
    )
    conn.close()


def get_sync_logs(limit=5):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT sync_time, row_fetched, row_created, row_updated, error_message 
                      FROM sync_log ORDER BY sync_time DESC LIMIT ?""",
        (limit,),
    )
    logs = cursor.fetchall()
    conn.close()
    return logs
