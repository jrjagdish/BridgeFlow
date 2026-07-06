# bridgeflow-cli

Python SDK and command-line client for [BridgeFlow](https://github.com/jrjagdish/BridgeFlow) — the Google Sheets → Notion sync app.

## Install

```bash
pip install bridgeflow-cli
```

## Get an API key

1. Log in to your BridgeFlow web app.
2. Go to **Settings → API Access** and click **Generate API Key**.
3. Copy the key — it's shown only once.

## CLI usage

```bash
# One-time setup
bridgeflow login --api-key bf_xxxxxxxx --base-url https://your-app.vercel.app

bridgeflow whoami
bridgeflow status

# Configure the sync
bridgeflow config set \
  --spreadsheet-id 1tXdvBTf9LExJNci... \
  --sheet-name Sheet1 \
  --notion-database-id 375abee6b0e380... \
  --id-column ID \
  --column-mapping "ID:Task ID:rich_text" \
  --column-mapping "Task Name:Name:title" \
  --column-mapping "Status:Status:select"

bridgeflow config get

# Set up Notion from scratch
bridgeflow notion create-database --title "Tasks" \
  --property "Task Name:Name:title" \
  --property "Status:Status:select"

# Preview a sheet before configuring it
bridgeflow sheets preview --spreadsheet-id 1tXdvBTf9LExJNci...

# Run and inspect syncs
bridgeflow sync trigger --wait
bridgeflow sync jobs --limit 10
bridgeflow sync job <job_id>
bridgeflow sync rows

bridgeflow logout
```

Credentials are stored in `~/.bridgeflow/config.json`. Set `BRIDGEFLOW_API_KEY` / `BRIDGEFLOW_BASE_URL` env vars to override them (useful in CI).

## SDK usage

```python
from bridgeflow import BridgeFlowClient

client = BridgeFlowClient(api_key="bf_xxxxxxxx", base_url="https://your-app.vercel.app")

client.save_config(spreadsheet_id="...", notion_database_id="...", id_column="ID")
job = client.trigger_sync()
print(client.get_job(job["job_id"]))

for row in client.list_rows():
    print(row["row_id"], row["status"])
```

### Errors

All SDK calls raise a subclass of `bridgeflow.BridgeFlowError`:

* `AuthenticationError` — missing or invalid API key.
* `APIError` — the API returned a non-2xx response (`.status_code`, `.detail`).
* `ConnectionError` — the BridgeFlow server couldn't be reached.

## License

MIT
