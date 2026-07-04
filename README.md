# BridgeFlow – Google Sheets → Notion Sync

BridgeFlow is a multi-user web application that automatically syncs data from Google Sheets to Notion.

Connect your Google account, connect your Notion workspace, configure your column mapping once, and BridgeFlow handles the rest — detecting new rows, detecting changes, and keeping your Notion database up to date on a configurable schedule.

No manual copy-pasting. No third-party automation subscriptions. Self-hostable.

---

## What's New in V2

| Feature | V1 | V2 |
|---|---|---|
| Users | Single user, tokens.json | Multi-user, PostgreSQL |
| Auth | Manual token copy | Google OAuth + Notion OAuth |
| Database | SQLite | Neon PostgreSQL (cloud) |
| Scheduler | APScheduler (in-process) | Inngest (cron trigger, serverless-friendly) |
| Job queue | None | Inngest events |
| Job tracking | None | SyncJob audit trail |
| Frontend | None | React + Vite |
| Deployment | Local only | Docker + Vercel |

---

## Features

### Multi-User OAuth

Each user connects their own Google account and Notion workspace through a standard OAuth flow. Tokens are stored securely in PostgreSQL — never in files or browser storage.

### Smart Change Detection

Uses a configurable ID column to identify rows.

* Creates a new Notion page when a new row ID appears.
* Updates the existing Notion page when row data changes (hash-based comparison — unchanged rows are skipped entirely).
* Preserves previously synced data on error — only the error message is updated.
* Prevents duplicate entries.

### Background Processing with Inngest

Auto-syncs are dispatched on a schedule (default every 5 minutes) by an Inngest cron function. Inngest calls back into the API over HTTP (`POST /api/inngest`), so there's no separate worker/beat process to run — it works on Vercel's serverless functions for free, unlike Celery.

### Full Job Audit Trail

Every sync run — manual or scheduled — is recorded as a `SyncJob` with:

* Status (`pending`, `running`, `completed`, `completed_with_errors`, `failed`)
* Row counts (fetched, created, updated, skipped)
* Error list per failed row
* Timestamps (started, finished)

### Live Job Streaming

Poll or stream the status of a running sync job via Server-Sent Events.

### Configurable Column Mapping

Map any Google Sheet column to any Notion property with type support for `title`, `rich_text`, `number`, `select`, `date`, `checkbox`, and `url`.

### React Frontend

A web UI for connecting accounts, configuring the sync, previewing sheet data, creating Notion databases, and triggering syncs.

---

## Tech Stack

* **FastAPI** — API server
* **Tortoise ORM + asyncpg** — async database layer
* **Neon PostgreSQL** — cloud Postgres (or any Postgres)
* **Inngest** — scheduled/background job runs (serverless-friendly, no worker process)
* **React + Vite** — frontend
* **Docker + Docker Compose** — containerised deployment
* **Vercel** — serverless deployment for API + frontend

---

## Project Structure

```text
bridgeflow/
│
├── main.py                  # FastAPI app, all routes
├── debug.py                 # Shared logger
├── requirements.txt
├── requirements-dev.txt     # pytest, pytest-asyncio, httpx
├── pytest.ini
├── Dockerfile               # Python API image
├── docker-compose.yml       # API + frontend
├── vercel.json              # Vercel routing config
├── .env                     # Local environment variables
│
├── v2/
│   ├── auth.py              # HTTP-only session cookie helpers
│   ├── oauth.py             # Google OAuth — token exchange + refresh
│   ├── notion_oauth.py      # Notion OAuth — token exchange
│   ├── models.py            # Tortoise ORM models + DB config
│   ├── sheets_service.py    # Google Sheets API calls
│   ├── notion_service.py    # Notion API calls
│   ├── inngest_client.py    # Inngest client instance
│   ├── inngest_functions.py # Cron function — dispatches auto-syncs every 5 min
│   └── tasks.py             # _do_sync + dispatch_all_syncs_async (sync logic)
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── components/
│       └── hooks/
│
└── tests/
    └── test_routes.py       # Unit tests for all routes (mocked DB)
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/bridgeflow.git
cd bridgeflow
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend && npm install && cd ..
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Google OAuth
CLIENT_ID=your_google_client_id
CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5173/oauth/callback

# Notion OAuth
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret
NOTION_REDIRECT_URI=http://localhost:5173/oauth/notion/callback

# Database (Neon PostgreSQL or any Postgres)
DATABASE_URL=postgresql://user:password@host/dbname?ssl=require

# Inngest — local dev talks to the Inngest Dev Server; leave INNGEST_DEV unset in prod
INNGEST_DEV=1
# INNGEST_EVENT_KEY=       # prod only, from the Inngest dashboard
# INNGEST_SIGNING_KEY=     # prod only, from the Inngest dashboard

# Frontend URL (used for OAuth redirects)
FRONTEND_URL=http://localhost:5173
```

---

## Running Locally

BridgeFlow requires two processes running simultaneously, plus the Inngest Dev Server if you want to exercise the scheduled sync locally.

### Terminal 1 — API Server

```bash
uvicorn main:app --reload
```

### Terminal 2 — Frontend

```bash
cd frontend && npm run dev
```

Open `http://localhost:5173` in your browser.

### Terminal 3 (optional) — Inngest Dev Server

```bash
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```

This gives you a local dashboard (`http://localhost:8222`) to trigger and inspect the scheduled sync function without waiting for the real cron.

---

## Running with Docker

Start the API and frontend with a single command:

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend (Vite dev) | http://localhost:5173 |
| API (FastAPI) | http://localhost:8000 |

---

## Deploying to Vercel

### 1. Push to GitHub

### 2. Import into Vercel

Connect your GitHub repository. Vercel uses `vercel.json` — no additional configuration needed in the Vercel dashboard.

### 3. Set Environment Variables in Vercel

| Variable | Production value |
|---|---|
| `CLIENT_ID` | Google OAuth client ID |
| `CLIENT_SECRET` | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | `https://your-app.vercel.app/oauth/callback` |
| `NOTION_CLIENT_ID` | Notion OAuth client ID |
| `NOTION_CLIENT_SECRET` | Notion OAuth client secret |
| `NOTION_REDIRECT_URI` | `https://your-app.vercel.app/oauth/notion/callback` |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `INNGEST_EVENT_KEY` | From the Inngest dashboard (production app) |
| `INNGEST_SIGNING_KEY` | From the Inngest dashboard (production app) |
| `FRONTEND_URL` | `https://your-app.vercel.app` |

### 4. Register Redirect URIs

**Google Cloud Console** → APIs & Services → Credentials → your OAuth Client:
```
https://your-app.vercel.app/oauth/callback
```

**Notion integration settings**:
```
https://your-app.vercel.app/oauth/notion/callback
```

### 5. Connect the app to Inngest

In the [Inngest dashboard](https://app.inngest.com), create an app pointing at `https://your-app.vercel.app/api/inngest` and copy the Event Key + Signing Key into the Vercel env vars above. Inngest will call that endpoint on its own schedule (every 5 minutes, per the cron trigger in `v2/inngest_functions.py`) — no separate worker process needed, which is what makes this work on Vercel's free tier.

---

## API Reference

### Auth

| Method | Path | Description |
|---|---|---|
| `GET` | `/oauth/start` | Returns Google consent URL |
| `GET` | `/oauth/callback` | Google OAuth callback — sets session cookie |
| `GET` | `/oauth/notion/start` | Returns Notion consent URL |
| `GET` | `/oauth/notion/callback` | Notion OAuth callback |
| `GET` | `/me` | Current user profile |
| `POST` | `/logout` | Clear session cookie |
| `POST` | `/oauth/notion/disconnect` | Remove Notion token |

### Sync

| Method | Path | Description |
|---|---|---|
| `POST` | `/sync/trigger` | Manually trigger a sync |
| `GET` | `/sync/jobs` | List recent sync jobs |
| `GET` | `/sync/jobs/{job_id}` | Get a single sync job |
| `GET` | `/sync/jobs/{job_id}/stream` | SSE stream — live job status |
| `GET` | `/sync/rows` | Audit trail of all synced rows |
| `GET` | `/status` | Last trigger time + active job count |

### Configuration

| Method | Path | Description |
|---|---|---|
| `GET` | `/config` | Load saved sync configuration |
| `POST` | `/config` | Save sync configuration |
| `POST` | `/sheets/preview` | Preview sheet headers and first rows |
| `POST` | `/notion/page` | Create a Notion page |
| `POST` | `/notion/database` | Create a Notion database with a property schema |

---

## Configuration Reference

`POST /config` accepts:

```json
{
  "spreadsheet_id": "your_google_sheet_id",
  "sheet_name": "Sheet1",
  "notion_database_id": "your_notion_database_id",
  "id_column": "ID",
  "column_mappings": [
    { "sheet_col": "ID",        "notion_property": "Task ID",  "type": "rich_text" },
    { "sheet_col": "Task Name", "notion_property": "Name",     "type": "title"     },
    { "sheet_col": "Status",    "notion_property": "Status",   "type": "select"    },
    { "sheet_col": "Due Date",  "notion_property": "Due Date", "type": "date"      }
  ],
  "sync_interval_minutes": 5
}
```

### Supported Notion Property Types

| Type | Notion property |
|---|---|
| `title` | Title (required — one per database) |
| `rich_text` | Text |
| `number` | Number |
| `select` | Select |
| `date` | Date |
| `checkbox` | Checkbox |
| `url` | URL |

---

## Sync Rules

### Unique ID Required

Every row must have a non-empty value in the configured `id_column`. Rows without an ID are skipped and logged as errors.

### Date Format

Dates must be in ISO format:

```text
YYYY-MM-DD
```

### Notion Character Limit

Notion text properties have a 2,000-character limit. Values exceeding this are automatically truncated.

### First Sync Must Be Manual

Auto-sync via the scheduler only starts after the user has completed at least one successful manual sync. This prevents unintended background activity on misconfigured accounts.

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests cover all routes with a fully mocked database — no real PostgreSQL required.

---

## Logs

| File | Contains |
|---|---|
| `logs/bridgeflow.log` | All log messages (DEBUG and above) |
| `logs/bridgeflow_errors.log` | Errors only |

Console output shows INFO and above. Set `LOG_DIR` environment variable to change the log directory.

---

## License

MIT License. Free to use, modify, and distribute.  
