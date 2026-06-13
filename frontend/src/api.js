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
// Notion OAuth
// ---------------------------------------------------------------------------

export async function getNotionOAuthUrl() {
  const res = await fetch('/oauth/notion/start')
  if (!res.ok) throw new Error('Failed to get Notion auth URL')
  const data = await res.json()
  return data.auth_url
}

export async function disconnectNotion() {
  const res = await fetch('/oauth/notion/disconnect', { method: 'POST', credentials: 'include' })
  if (!res.ok) throw new Error('Failed to disconnect Notion')
  return res.json()
}

// ---------------------------------------------------------------------------
// Google Sheets — fetch header row + preview from a spreadsheet
// ---------------------------------------------------------------------------

export async function fetchSheetPreview(spreadsheetId, sheetName = 'Sheet1') {
  const res = await fetch('/sheets/preview', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ spreadsheet_id: spreadsheetId, sheet_name: sheetName }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to fetch sheet headers')
  }
  return res.json()  // { headers: string[], preview: dict[] }
}

// ---------------------------------------------------------------------------
// Notion — create a database with the given property schema
// ---------------------------------------------------------------------------

export async function createNotionDatabase({ parentPageId, title, properties }) {
  const res = await fetch('/notion/database', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      parent_page_id: parentPageId,
      title,
      properties,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to create Notion database')
  }
  return res.json()  // { database_id: string, url: string }
}

// ---------------------------------------------------------------------------
// Config — DB-backed per-user config (replaces localStorage)
// ---------------------------------------------------------------------------

export async function getConfig() {
  const res = await fetch('/config', { credentials: 'include' })
  if (!res.ok) throw new Error('Failed to load config')
  return res.json()
}

export async function saveConfig(config) {
  const res = await fetch('/config', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      spreadsheet_id:        config.spreadsheet_id ?? null,
      sheet_name:            config.sheet_name ?? null,
      notion_database_id:    config.notion_database_id ?? null,
      column_mappings:       config.column_mappings ?? null,
      sync_interval_minutes: config.sync_interval_minutes ?? null,
    }),
  })
  if (!res.ok) throw new Error('Failed to save config')
  return res.json()
}
