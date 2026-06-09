import { useState } from 'react'
import { loadConfig, saveConfig } from '../api'

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
    <div className={`glass rounded-2xl p-6 space-y-5
      ${isDark ? 'glass-card-dark' : 'glass-card-light'}`}>
      <div>
        <h3 className={`font-semibold text-base ${isDark ? 'text-white' : 'text-slate-800'}`}>{title}</h3>
        {desc && <p className={`text-xs mt-0.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{desc}</p>}
      </div>
      <div className={`border-t ${isDark ? 'border-white/5' : 'border-slate-100'}`} />
      {children}
    </div>
  )
}

export default function Settings({ isDark }) {
  const initial = loadConfig()

  const [google, setGoogle] = useState(initial.google)
  const [notion, setNotion] = useState(initial.notion)
  const [mappings, setMappings] = useState(
    // normalise: config.json stores as object, we use array internally
    Array.isArray(initial.column_mapping)
      ? initial.column_mapping
      : Object.entries(initial.column_mapping).map(([sheet_col, v]) => ({
          sheet_col,
          notion_property: v.notion_property,
          type: v.type,
        }))
  )
  const [interval, setInterval] = useState(initial.sync_interval_minutes ?? 5)
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)

  const setG = (key) => (val) => setGoogle(g => ({ ...g, [key]: val }))
  const setN = (key) => (val) => setNotion(n => ({ ...n, [key]: val }))

  const updateMapping = (i, key, val) =>
    setMappings(ms => ms.map((m, idx) => idx === i ? { ...m, [key]: val } : m))

  const addMapping = () =>
    setMappings(ms => [...ms, { sheet_col: '', notion_property: '', type: 'rich_text' }])

  const removeMapping = (i) =>
    setMappings(ms => ms.filter((_, idx) => idx !== i))

  const handleSave = async () => {
    setSaving(true)
    const config = {
      google,
      notion,
      column_mapping: mappings,
      sync_interval_minutes: Number(interval),
    }
    await saveConfig(config)
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
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

      {/* Local-storage notice */}
      <div className={`flex items-start gap-3 px-4 py-3 rounded-xl border text-sm
        ${isDark ? 'bg-amber-400/5 border-amber-400/20 text-amber-300' : 'bg-amber-50 border-amber-200 text-amber-700'}`}>
        <span className="text-base shrink-0">⚠️</span>
        <span>Settings are saved locally in your browser for now. Backend persistence is coming soon.</span>
      </div>

      {/* Google Sheets */}
      <SectionCard
        title="Google Sheets"
        desc="Which spreadsheet and sheet to sync from"
        isDark={isDark}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Spreadsheet ID" hint="from the URL" isDark={isDark}>
            <Input value={google.spreadsheet_id} onChange={setG('spreadsheet_id')}
              placeholder="1tXdvBTf9LExJNci…" isDark={isDark} mono />
          </Field>
          <Field label="Sheet Name" isDark={isDark}>
            <Input value={google.sheet_name} onChange={setG('sheet_name')}
              placeholder="Sheet1" isDark={isDark} />
          </Field>
          <Field label="ID Column" hint="unique row identifier" isDark={isDark}>
            <Input value={google.id_column} onChange={setG('id_column')}
              placeholder="ID" isDark={isDark} />
          </Field>
        </div>
      </SectionCard>

      {/* Notion */}
      <SectionCard
        title="Notion"
        desc="Target Notion database to sync rows into"
        isDark={isDark}
      >
        <Field label="Database ID" hint="from the Notion database URL" isDark={isDark}>
          <Input value={notion.database_id} onChange={setN('database_id')}
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
