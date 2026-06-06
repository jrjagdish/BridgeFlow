# BridgeFlow – Google Sheets → Notion Sync

BridgeFlow is a lightweight background service that automatically syncs data from Google Sheets to Notion.

It monitors a Google Sheet at regular intervals, detects new or modified rows, and mirrors those changes into a Notion database.

No manual copy-pasting, no third-party automation tools, and no recurring subscription costs.

---

## Features

### One-Way Synchronization

Automatically reads rows from a Google Sheet and creates corresponding entries in a Notion database.

### Smart Change Detection

Uses a unique ID column to identify records.

* Creates a new Notion page when a new ID appears.
* Updates the existing Notion page when data for an existing ID changes.
* Prevents duplicate entries.

### Background Processing

Runs automatically on a configurable schedule and stores sync state in SQLite to track changes efficiently.

### Configurable Column Mapping

Map Google Sheet columns to any Notion database properties through a simple configuration file.

### Manual Sync Trigger

Trigger synchronization instantly through an API endpoint without waiting for the next scheduled run.

---

# Tech Stack

* FastAPI
* APScheduler
* SQLite
* Google Sheets API
* Notion API
* Python

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/bridgeflow.git
cd bridgeflow
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

## config.json

Create a `config.json` file in the project root.

```json
{
  "google": {
    "spreadsheet_id": "YOUR_GOOGLE_SHEET_ID",
    "sheet_name": "Tasks",
    "id_column": "ID"
  },
  "notion": {
    "database_id": "YOUR_NOTION_DATABASE_ID"
  },
  "column_mapping": {
    "ID": {
      "notion_property": "Task ID",
      "type": "rich_text"
    },
    "Task Name": {
      "notion_property": "Name",
      "type": "title"
    },
    "Status": {
      "notion_property": "Status",
      "type": "select"
    },
    "Due Date": {
      "notion_property": "Due Date",
      "type": "date"
    }
  },
  "sync_interval_minutes": 5
}
```

### Notes

* Google Sheet column names are case-sensitive.
* Notion property names must exactly match your database schema.
* The ID column should contain unique values.

---

# Environment Variables

Create a `.env` file in the root directory.

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/oauth/callback

NOTION_TOKEN=your_notion_internal_integration_token
```

---

# Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The application will be available at:

```text
http://localhost:8000
```

---

# API Endpoints

## Connect Google Account

### GET /oauth/start

```text
http://localhost:8000/oauth/start
```

Redirects the user to Google's authorization page.

After successful authentication, BridgeFlow stores OAuth tokens locally, allowing future sync operations without requiring repeated logins.

---

## Check Application Status

### GET /status

```text
http://localhost:8000/status
```

Returns:

* Application health status
* Recent sync activity
* Number of records processed
* Sync statistics

---

## Trigger Manual Synchronization

### GET /sync/trigger

```text
http://localhost:8000/sync/trigger
```

Forces an immediate synchronization between Google Sheets and Notion.

Useful for testing and verification.

---

# Synchronization Workflow

1. Read rows from Google Sheets.
2. Identify each row using the configured ID column.
3. Compare current data with previously synced data stored in SQLite.
4. Create a new Notion page if the ID does not exist.
5. Update the existing Notion page if changes are detected.
6. Save the latest sync state locally.

---

# Project Structure

```text
bridgeflow/
│
├── main.py
├── scheduler.py
├── notion_client.py
├── google_client.py
├── sync_service.py
├── database.db
├── config.json
├── .env
├── tokens.json
│
└── README.md
```

---

# Important Rules

## Unique IDs Required

Every row must contain a unique identifier.

Example:

```text
T001
T002
T003
```

Rows without an ID will be skipped during synchronization.

---

## Supported Date Format

Dates must use the ISO format:

```text
YYYY-MM-DD
```

Example:

```text
2026-06-06
```

---

## Notion Character Limit

Notion text properties have a maximum limit of 2,000 characters.

BridgeFlow automatically truncates values exceeding this limit to prevent synchronization failures.

---

# Future Improvements

* Two-way synchronization
* Real-time webhook support
* Multiple sheet support
* Conflict resolution system
* Docker deployment
* User dashboard
* Email notifications
* Sync history analytics

---

# License

MIT License

Feel free to use, modify, and distribute this project.
