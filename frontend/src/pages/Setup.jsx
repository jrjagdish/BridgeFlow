import { useState } from 'react'
import { fetchSheetPreview, createNotionDatabase, saveConfig } from '../api'

const PROPERTY_TYPES = [
  'title', 'rich_text', 'number', 'select', 'multi_select',
  'status', 'date', 'checkbox', 'url', 'email', 'phone_number',
]

// ---------------------------------------------------------------------------
// Shared primitives
// ---------------------------------------------------------------------------

function Input({ value, onChange, placeholder, isDark, mono = false, disabled = false }) {
  return (
    <input
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      spellCheck={false}
      className={`w-full px-4 py-2.5 rounded-xl text-sm transition-all duration-150 outline-none
        border focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/50
        disabled:opacity-50 disabled:cursor-not-allowed
        ${mono ? 'font-mono' : ''}
        ${isDark
          ? 'bg-white/[0.04] border-white/10 text-slate-200 placeholder-slate-600 focus:bg-white/[0.06]'
          : 'bg-white/80 border-slate-200 text-slate-800 placeholder-slate-400 focus:bg-white'}`}
    />
  )
}

function TypeSelect({ value, onChange, isDark }) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className={`w-full px-3 py-2.5 rounded-xl text-sm outline-none border
        focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/50 cursor-pointer
        ${isDark
          ? 'bg-[#0d0d20] border-white/10 text-slate-200'
          : 'bg-white border-slate-200 text-slate-800'}`}
    >
      {PROPERTY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
    </select>
  )
}

function StepBadge({ n, active, done, isDark }) {
  return (
    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0 transition-colors
      ${done
        ? 'bg-emerald-500 text-white'
        : active
          ? 'bg-violet-500 text-white'
          : isDark ? 'bg-white/10 text-slate-500' : 'bg-slate-200 text-slate-400'
      }`}>
      {done ? '✓' : n}
    </div>
  )
}

function StepHeader({ n, label, sub, active, done, isDark }) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <StepBadge n={n} active={active} done={done} isDark={isDark} />
      <div>
        <p className={`font-semibold text-sm ${active || done
          ? isDark ? 'text-white' : 'text-slate-800'
          : isDark ? 'text-slate-600' : 'text-slate-400'}`}>
          {label}
        </p>
        {sub && <p className={`text-xs mt-0.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{sub}</p>}
      </div>
    </div>
  )
}

function Card({ children, isDark }) {
  return (
    <div className={`glass rounded-2xl p-6 ${isDark ? 'glass-card-dark' : 'glass-card-light'}`}>
      {children}
    </div>
  )
}

function ErrorMsg({ msg, isDark }) {
  if (!msg) return null
  return (
    <p className={`mt-3 text-xs px-3 py-2 rounded-xl border
      ${isDark
        ? 'text-red-400 bg-red-400/10 border-red-400/20'
        : 'text-red-600 bg-red-50 border-red-200'}`}>
      {msg}
    </p>
  )
}

// ---------------------------------------------------------------------------
// Step 1 — Spreadsheet ID input + fetch headers
// ---------------------------------------------------------------------------
function Step1({ isDark, onNext }) {
  const [spreadsheetId, setSpreadsheetId] = useState('')
  const [sheetName, setSheetName] = useState('Sheet1')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFetch = async () => {
    if (!spreadsheetId.trim()) {
      setError('Please enter a spreadsheet ID.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await fetchSheetPreview(spreadsheetId.trim(), sheetName.trim() || 'Sheet1')
      if (!data.headers?.length) {
        setError('Sheet appears empty or has no header row.')
        return
      }
      onNext({ spreadsheetId: spreadsheetId.trim(), sheetName: sheetName.trim() || 'Sheet1', ...data })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card isDark={isDark}>
      <StepHeader n={1} label="Connect your Google Sheet" sub="Paste the spreadsheet ID from the URL" active done={false} isDark={isDark} />
      <div className="space-y-4">
        <div>
          <label className={`block text-xs font-semibold mb-1.5 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
            Spreadsheet ID <span className={`font-normal ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>(from the URL)</span>
          </label>
          <Input
            value={spreadsheetId}
            onChange={setSpreadsheetId}
            placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
            isDark={isDark}
            mono
          />
          <p className={`mt-1.5 text-xs ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
            Found between /d/ and /edit in your Google Sheets URL
          </p>
        </div>
        <div>
          <label className={`block text-xs font-semibold mb-1.5 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
            Sheet Tab Name
          </label>
          <Input value={sheetName} onChange={setSheetName} placeholder="Sheet1" isDark={isDark} />
        </div>
        <ErrorMsg msg={error} isDark={isDark} />
        <button
          onClick={handleFetch}
          disabled={loading}
          className="btn-primary w-full disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading
            ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Fetching headers…</>
            : '→ Fetch Headers'}
        </button>
      </div>
    </Card>
  )
}

// ---------------------------------------------------------------------------
// Step 2 — Map sheet columns → Notion properties + create database
// ---------------------------------------------------------------------------
function Step2({ isDark, spreadsheetId, sheetName, headers, preview, onDone }) {
  const initialMappings = headers.map((h, i) => ({
    sheet_col: h,
    notion_property: h,
    type: i === 0 ? 'title' : 'rich_text',
  }))

  const [mappings, setMappings] = useState(initialMappings)
  const [dbTitle, setDbTitle]   = useState('BridgeFlow Sync')
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  const update = (i, key, val) =>
    setMappings(ms => ms.map((m, idx) => idx === i ? { ...m, [key]: val } : m))

  const titleCount = mappings.filter(m => m.type === 'title').length

  const handleCreate = async () => {
    if (titleCount === 0) {
      setError('Exactly one column must have type "title" — it becomes the row name in Notion.')
      return
    }
    if (titleCount > 1) {
      setError('Only one column can have type "title". Change the others to "rich_text".')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const result = await createNotionDatabase({
        title: dbTitle.trim() || 'BridgeFlow Sync',
        properties: mappings,
      })
      // Persist config to DB
      await saveConfig({
        spreadsheet_id:     spreadsheetId,
        sheet_name:         sheetName,
        notion_database_id: result.database_id,
        column_mappings:    mappings,
      })
      onDone(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const th = `text-left text-xs font-semibold uppercase tracking-wider pb-3
    ${isDark ? 'text-slate-500' : 'text-slate-400'}`

  return (
    <Card isDark={isDark}>
      <StepHeader n={2} label="Map columns & create Notion database" sub="Adjust property names and types, then click create" active done={false} isDark={isDark} />

      {/* Column mapping table */}
      <div className="overflow-x-auto -mx-1 mb-6">
        <table className="w-full min-w-[560px]">
          <thead>
            <tr className={`border-b ${isDark ? 'border-white/5' : 'border-slate-100'}`}>
              <th className={th}>Sheet Column</th>
              <th className={th}>Notion Property Name</th>
              <th className={th}>Type</th>
            </tr>
          </thead>
          <tbody>
            {mappings.map((m, i) => (
              <tr key={i} className={`border-b ${isDark ? 'border-white/[0.04]' : 'border-slate-50'}`}>
                <td className="py-2.5 pr-3">
                  <span className={`text-sm font-mono px-2 py-1 rounded-lg
                    ${isDark ? 'bg-white/5 text-slate-300' : 'bg-slate-100 text-slate-700'}`}>
                    {m.sheet_col}
                  </span>
                </td>
                <td className="py-2.5 pr-3">
                  <Input
                    value={m.notion_property}
                    onChange={v => update(i, 'notion_property', v)}
                    placeholder="Property name"
                    isDark={isDark}
                  />
                </td>
                <td className="py-2.5">
                  <TypeSelect value={m.type} onChange={v => update(i, 'type', v)} isDark={isDark} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {titleCount !== 1 && (
        <div className={`flex items-start gap-2 px-4 py-3 rounded-xl border mb-4 text-xs
          ${isDark ? 'bg-amber-400/5 border-amber-400/20 text-amber-300' : 'bg-amber-50 border-amber-200 text-amber-700'}`}>
          <span className="text-sm">⚠️</span>
          Exactly one column must be type <strong>title</strong> (currently {titleCount}). It becomes the primary name in Notion.
        </div>
      )}

      {/* Database name */}
      <div className="mb-4">
        <label className={`block text-xs font-semibold mb-1.5 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
          Database Name
        </label>
        <Input value={dbTitle} onChange={setDbTitle} placeholder="BridgeFlow Sync" isDark={isDark} />
      </div>

      <ErrorMsg msg={error} isDark={isDark} />

      <button
        onClick={handleCreate}
        disabled={loading}
        className="btn-primary w-full mt-3 disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {loading
          ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Creating database…</>
          : '✨ Create Notion Database'}
      </button>
    </Card>
  )
}

// ---------------------------------------------------------------------------
// Step 3 — Success
// ---------------------------------------------------------------------------
function Step3({ isDark, result }) {
  return (
    <Card isDark={isDark}>
      <StepHeader n={3} label="Database created — you're ready to sync!" sub="" active done isDark={isDark} />
      <div className={`flex items-start gap-3 px-5 py-4 rounded-2xl border mb-4
        ${isDark ? 'bg-emerald-400/5 border-emerald-400/15 text-emerald-300' : 'bg-emerald-50 border-emerald-200 text-emerald-700'}`}>
        <span className="text-xl shrink-0">🎉</span>
        <div>
          <p className="font-semibold text-sm mb-1">Notion database ready</p>
          <p className={`text-xs font-mono break-all ${isDark ? 'text-emerald-400/70' : 'text-emerald-600'}`}>
            {result.database_id}
          </p>
        </div>
      </div>
      {result.url && (
        <a
          href={result.url}
          target="_blank"
          rel="noreferrer"
          className={`inline-flex items-center gap-2 text-sm font-medium px-4 py-2.5 rounded-xl border transition-all
            ${isDark
              ? 'border-white/10 text-slate-300 hover:text-violet-300 hover:border-violet-500/30 hover:bg-violet-500/5'
              : 'border-slate-200 text-slate-600 hover:text-violet-600 hover:border-violet-300 hover:bg-violet-50'}`}
        >
          Open in Notion ↗
        </a>
      )}
      <p className={`mt-4 text-xs ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
        Your config is saved. Head to <strong>Overview</strong> and click <strong>Trigger Sync</strong> to start syncing.
      </p>
    </Card>
  )
}

// ---------------------------------------------------------------------------
// Main Setup page
// ---------------------------------------------------------------------------
export default function Setup({ isDark }) {
  const [step, setStep]   = useState(1)
  const [ctx, setCtx]     = useState(null)   // data from step 1
  const [result, setResult] = useState(null) // data from step 2

  const handleStep1Done = (data) => {
    setCtx(data)
    setStep(2)
  }

  const handleStep2Done = (data) => {
    setResult(data)
    setStep(3)
  }

  return (
    <div className="max-w-3xl space-y-6 animate-fade-in">
      <div className="mb-2">
        <h1 className={`text-2xl font-black tracking-tight ${isDark ? 'text-white' : 'text-slate-800'}`}>
          Setup
        </h1>
        <p className={`text-sm mt-0.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
          Connect your spreadsheet and create a Notion database in 3 steps
        </p>
      </div>

      {/* Step progress strip */}
      <div className="flex items-center gap-3">
        {[1, 2, 3].map((n, i) => (
          <div key={n} className="flex items-center gap-3">
            <StepBadge n={n} active={step === n} done={step > n} isDark={isDark} />
            {i < 2 && (
              <div className={`flex-1 h-px w-12 ${step > n
                ? 'bg-emerald-500/50'
                : isDark ? 'bg-white/10' : 'bg-slate-200'}`} />
            )}
          </div>
        ))}
      </div>

      {step === 1 && <Step1 isDark={isDark} onNext={handleStep1Done} />}
      {step === 2 && ctx && (
        <Step2
          isDark={isDark}
          spreadsheetId={ctx.spreadsheetId}
          sheetName={ctx.sheetName}
          headers={ctx.headers}
          preview={ctx.preview}
          onDone={handleStep2Done}
        />
      )}
      {step === 3 && result && <Step3 isDark={isDark} result={result} />}
    </div>
  )
}
