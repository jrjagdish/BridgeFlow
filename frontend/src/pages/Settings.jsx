import { useState, useEffect } from 'react'
import { getConfig, saveConfig, getApiKeyStatus, createApiKey, revokeApiKey } from '../api'

const PROPERTY_TYPES = [
  'title', 'rich_text', 'number', 'select', 'multi_select',
  'status', 'date', 'checkbox', 'url', 'email', 'phone_number',
]

function Field({ label, hint, children, isDark }) {
  return (
    <div>
      <label className={`block text-sm font-medium mb-1.5 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
        {label}
        {hint && <span className={`ml-2 text-xs font-normal ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{hint}</span>}
      </label>
      {children}
    </div>
  )
}

function Input({ value, onChange, placeholder, isDark, mono = false }) {
  return (
    <input
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      spellCheck={false}
      className={`w-full px-4 py-2.5 rounded-xl text-sm transition-all duration-150 outline-none
        border focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/50
        ${mono ? 'font-mono' : ''}
        ${isDark
          ? 'bg-white/[0.04] border-white/10 text-slate-200 placeholder-slate-600 focus:bg-white/[0.06]'
          : 'bg-white/80 border-slate-200 text-slate-800 placeholder-slate-400 focus:bg-white'}`}
    />
  )
}

function Select({ value, onChange, options, isDark }) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className={`w-full px-3 py-2.5 rounded-xl text-sm transition-all duration-150 outline-none
        border focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/50 cursor-pointer
        ${isDark
          ? 'bg-[#0d0d20] border-white/10 text-slate-200'
          : 'bg-white border-slate-200 text-slate-800'}`}
    >
      {options.map(o => <option key={o} value={o}>{o}</option>)}
    </select>
  )
}

function SectionCard({ title, desc, children, isDark }) {
  return (
    <div className={`glass rounded-2xl p-6 space-y-5 transition-all duration-200
      ${isDark ? 'glass-card-dark card-glow-dark' : 'glass-card-light card-glow-light'}`}>
      <div>
        <h3 className={`font-semibold text-base ${isDark ? 'text-white' : 'text-slate-800'}`}>{title}</h3>
        {desc && <p className={`text-xs mt-0.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{desc}</p>}
      </div>
      <div className={`border-t ${isDark ? 'border-white/5' : 'border-slate-100'}`} />
      {children}
    </div>
  )
}

const DEFAULT = {
  spreadsheet_id: '',
  sheet_name: 'Sheet1',
  notion_database_id: '',
  column_mappings: [],
  sync_interval_minutes: 5,
}

export default function Settings({ isDark }) {
  const [loading, setLoading]   = useState(true)
  const [spreadsheetId, setSpreadsheetId] = useState('')
  const [sheetName, setSheetName]         = useState('Sheet1')
  const [notionDbId, setNotionDbId]       = useState('')
  const [mappings, setMappings]           = useState([])
  const [interval, setInterval]           = useState(5)
  const [saved, setSaved]   = useState(false)
  const [saving, setSaving] = useState(false)

  const [hasApiKey, setHasApiKey]     = useState(false)
  const [newApiKey, setNewApiKey]     = useState('')
  const [keyBusy, setKeyBusy]         = useState(false)
  const [keyCopied, setKeyCopied]     = useState(false)

  useEffect(() => {
    getConfig()
      .then(cfg => {
        setSpreadsheetId(cfg.spreadsheet_id || '')
        setSheetName(cfg.sheet_name || 'Sheet1')
        setNotionDbId(cfg.notion_database_id || '')
        setMappings(Array.isArray(cfg.column_mappings) ? cfg.column_mappings : [])
        setInterval(cfg.sync_interval_minutes ?? 5)
      })
      .catch(() => { /* unauthenticated — leave defaults */ })
      .finally(() => setLoading(false))

    getApiKeyStatus()
      .then(s => setHasApiKey(!!s.has_api_key))
      .catch(() => {})
  }, [])

  const handleGenerateApiKey = async () => {
    setKeyBusy(true)
    setKeyCopied(false)
    try {
      const { api_key } = await createApiKey()
      setNewApiKey(api_key)
      setHasApiKey(true)
    } finally {
      setKeyBusy(false)
    }
  }

  const handleRevokeApiKey = async () => {
    setKeyBusy(true)
    try {
      await revokeApiKey()
      setHasApiKey(false)
      setNewApiKey('')
    } finally {
      setKeyBusy(false)
    }
  }

  const handleCopyApiKey = async () => {
    await navigator.clipboard.writeText(newApiKey)
    setKeyCopied(true)
    setTimeout(() => setKeyCopied(false), 2000)
  }

  const updateMapping = (i, key, val) =>
    setMappings(ms => ms.map((m, idx) => idx === i ? { ...m, [key]: val } : m))

  const addMapping = () =>
    setMappings(ms => [...ms, { sheet_col: '', notion_property: '', type: 'rich_text' }])

  const removeMapping = (i) =>
    setMappings(ms => ms.filter((_, idx) => idx !== i))

  const handleSave = async () => {
    setSaving(true)
    await saveConfig({
      spreadsheet_id:        spreadsheetId,
      sheet_name:            sheetName,
      notion_database_id:    notionDbId,
      column_mappings:       mappings,
      sync_interval_minutes: Number(interval),
    })
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 rounded-full border-2 border-violet-500/20 border-t-violet-500 animate-spin" />
      </div>
    )
  }

  const th = `text-left text-xs font-semibold uppercase tracking-wider pb-3
    ${isDark ? 'text-slate-500' : 'text-slate-400'}`

  return (
    <div className="max-w-3xl space-y-6 animate-fade-in">

      {/* Page title */}
      <div className="mb-2">
        <h1 className={`text-2xl font-black tracking-tight ${isDark ? 'text-white' : 'text-slate-800'}`}>
          Settings
        </h1>
        <p className={`text-sm mt-0.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
          Configure your sync pipeline
        </p>
      </div>

      {/* Google Sheets */}
      <SectionCard
        title="Google Sheets"
        desc="Which spreadsheet and sheet to sync from"
        isDark={isDark}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Spreadsheet ID" hint="from the URL" isDark={isDark}>
            <Input value={spreadsheetId} onChange={setSpreadsheetId}
              placeholder="1tXdvBTf9LExJNci…" isDark={isDark} mono />
          </Field>
          <Field label="Sheet Name" isDark={isDark}>
            <Input value={sheetName} onChange={setSheetName}
              placeholder="Sheet1" isDark={isDark} />
          </Field>
        </div>
      </SectionCard>

      {/* Notion */}
      <SectionCard
        title="Notion"
        desc="Target Notion database to sync rows into"
        isDark={isDark}
      >
        <Field label="Database ID" hint="from the Notion database URL or created via Setup" isDark={isDark}>
          <Input value={notionDbId} onChange={setNotionDbId}
            placeholder="375abee6b0e380…" isDark={isDark} mono />
        </Field>
      </SectionCard>

      {/* Column Mapping */}
      <SectionCard
        title="Column Mapping"
        desc="Map each Google Sheets column to a Notion property"
        isDark={isDark}
      >
        <div className="overflow-x-auto -mx-1">
          <table className="w-full min-w-[520px]">
            <thead>
              <tr className={`border-b ${isDark ? 'border-white/5' : 'border-slate-100'}`}>
                <th className={th}>Sheet Column</th>
                <th className={th}>Notion Property</th>
                <th className={th}>Type</th>
                <th className={th + ' w-10'} />
              </tr>
            </thead>
            <tbody>
              {mappings.map((m, i) => (
                <tr key={i} className={`border-b ${isDark ? 'border-white/[0.04]' : 'border-slate-50'}`}>
                  <td className="py-2.5 pr-3">
                    <Input value={m.sheet_col} onChange={v => updateMapping(i, 'sheet_col', v)}
                      placeholder="Column name" isDark={isDark} />
                  </td>
                  <td className="py-2.5 pr-3">
                    <Input value={m.notion_property} onChange={v => updateMapping(i, 'notion_property', v)}
                      placeholder="Property name" isDark={isDark} />
                  </td>
                  <td className="py-2.5 pr-3">
                    <Select value={m.type} onChange={v => updateMapping(i, 'type', v)}
                      options={PROPERTY_TYPES} isDark={isDark} />
                  </td>
                  <td className="py-2.5">
                    <button
                      onClick={() => removeMapping(i)}
                      className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm transition-colors
                        ${isDark ? 'text-slate-600 hover:text-red-400 hover:bg-red-400/10' : 'text-slate-300 hover:text-red-500 hover:bg-red-50'}`}
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <button
          onClick={addMapping}
          className={`mt-3 flex items-center gap-2 text-sm font-medium px-4 py-2 rounded-xl border transition-all duration-150
            ${isDark
              ? 'border-white/10 text-slate-400 hover:text-violet-300 hover:border-violet-500/30 hover:bg-violet-500/5'
              : 'border-slate-200 text-slate-500 hover:text-violet-600 hover:border-violet-300 hover:bg-violet-50'}`}
        >
          <span className="text-base leading-none">+</span> Add Column
        </button>
      </SectionCard>

      {/* Sync interval */}
      <SectionCard
        title="Sync Schedule"
        desc="How often to pull from Google Sheets"
        isDark={isDark}
      >
        <div className="flex items-center gap-4">
          <Field label="Interval (minutes)" isDark={isDark}>
            <input
              type="number"
              min={1}
              max={1440}
              value={interval}
              onChange={e => setInterval(e.target.value)}
              className={`w-32 px-4 py-2.5 rounded-xl text-sm outline-none border
                focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/50 transition-all
                ${isDark
                  ? 'bg-white/[0.04] border-white/10 text-slate-200'
                  : 'bg-white/80 border-slate-200 text-slate-800'}`}
            />
          </Field>
          <p className={`text-xs mt-5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
            Minimum: 1 min · Recommended: 5 min
          </p>
        </div>
      </SectionCard>

      {/* API Access — CLI / SDK */}
      <SectionCard
        title="API Access"
        desc="Generate an API key to use the BridgeFlow CLI / Python SDK"
        isDark={isDark}
      >
        {newApiKey && (
          <div className={`rounded-xl p-4 border space-y-2
            ${isDark ? 'bg-emerald-500/[0.06] border-emerald-500/20' : 'bg-emerald-50 border-emerald-200'}`}>
            <p className={`text-xs font-medium ${isDark ? 'text-emerald-300' : 'text-emerald-700'}`}>
              Copy this key now — it won't be shown again.
            </p>
            <div className="flex items-center gap-2">
              <code className={`flex-1 px-3 py-2 rounded-lg text-xs font-mono break-all
                ${isDark ? 'bg-black/30 text-slate-200' : 'bg-white text-slate-700'}`}>
                {newApiKey}
              </code>
              <button
                onClick={handleCopyApiKey}
                className={`shrink-0 px-3 py-2 rounded-lg text-xs font-semibold transition-colors
                  ${isDark ? 'bg-white/10 text-slate-200 hover:bg-white/20' : 'bg-slate-800 text-white hover:bg-slate-700'}`}
              >
                {keyCopied ? '✓ Copied' : 'Copy'}
              </button>
            </div>
            <p className={`text-xs font-mono ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              bridgeflow login --api-key {newApiKey.slice(0, 10)}…
            </p>
          </div>
        )}

        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerateApiKey}
            disabled={keyBusy}
            className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all disabled:opacity-60
              ${isDark ? 'bg-violet-500/20 text-violet-300 hover:bg-violet-500/30' : 'bg-violet-100 text-violet-700 hover:bg-violet-200'}`}
          >
            {hasApiKey ? 'Regenerate Key' : 'Generate API Key'}
          </button>
          {hasApiKey && (
            <button
              onClick={handleRevokeApiKey}
              disabled={keyBusy}
              className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all disabled:opacity-60
                ${isDark ? 'text-red-400 hover:bg-red-400/10' : 'text-red-600 hover:bg-red-50'}`}
            >
              Revoke
            </button>
          )}
          {hasApiKey && !newApiKey && (
            <span className={`text-xs ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              An API key is active on your account.
            </span>
          )}
        </div>
      </SectionCard>

      {/* Save button */}
      <div className="flex items-center gap-4 pt-2">
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {saving
            ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Saving…</>
            : '💾 Save Settings'
          }
        </button>
        {saved && (
          <span className="text-sm text-emerald-400 animate-fade-in">
            ✓ Saved successfully
          </span>
        )}
      </div>
    </div>
  )
}
