// All API calls go through the Vite proxy → localhost:8000

export async function getMe() {
  const res = await fetch('/me', { credentials: 'include' })
  if (!res.ok) throw new Error('Not authenticated')
  return res.json()
}

export async function getOAuthStartUrl() {
  const res = await fetch('/oauth/start')
  if (!res.ok) throw new Error('Failed to get auth URL')
  const data = await res.json()
  return data.auth_url
}

export async function getSyncStatus() {
  const res = await fetch('/status', { credentials: 'include' })
  if (!res.ok) throw new Error('Failed to fetch sync status')
  return res.json()
}

export async function triggerSync() {
  const res = await fetch('/sync/trigger', { method: 'GET', credentials: 'include' })
  if (!res.ok) throw new Error('Failed to trigger sync')
  return res.json()
}

export async function logout() {
  await fetch('/logout', { method: 'POST', credentials: 'include' })
}

// ---------------------------------------------------------------------------
// Notion OAuth — same pattern as Google. Backend endpoint: GET /notion/oauth/start
// ---------------------------------------------------------------------------

export async function getNotionOAuthUrl() {
  const res = await fetch('/oauth/notion/start')
  if (!res.ok) throw new Error('Failed to get Notion auth URL')
  const data = await res.json()
  return data.auth_url
}

// ---------------------------------------------------------------------------
// Config — mirrors config.json fields, stored in localStorage for now.
// Replace with GET /config and POST /config when backend endpoint is ready.
// ---------------------------------------------------------------------------

const DEFAULT_CONFIG = {
  google: {
    spreadsheet_id: '',
    sheet_name: 'Sheet1',
    id_column: 'ID',
  },
  notion: {
    database_id: '',
  },
  column_mapping: [
    { sheet_col: 'ID',        notion_property: 'Task ID', type: 'number' },
    { sheet_col: 'Task Name', notion_property: 'Tasks',   type: 'title' },
    { sheet_col: 'Status',    notion_property: 'Status',  type: 'status' },
  ],
  sync_interval_minutes: 5,
}

export function loadConfig() {
  // TODO: GET /config
  const raw = localStorage.getItem('bf_config')
  if (!raw) return DEFAULT_CONFIG
  try { return JSON.parse(raw) } catch { return DEFAULT_CONFIG }
}

export async function saveConfig(config) {
  // TODO: POST /config  { ...config }
  localStorage.setItem('bf_config', JSON.stringify(config))
}
