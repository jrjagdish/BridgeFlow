import { useState, useEffect } from 'react'
import { getSyncStatus } from '../api'
import StatusBadge from './StatusBadge'

function fmt(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

export default function SyncLogs({ isDark }) {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getSyncStatus()
      .then(data => setLogs(data.logs ?? []))
      .catch(() => setError('Could not load sync logs.'))
      .finally(() => setLoading(false))
  }, [])

  const th = `text-left text-xs font-semibold uppercase tracking-wider pb-3
    ${isDark ? 'text-slate-500' : 'text-slate-400'}`

  const td = `py-3.5 text-sm ${isDark ? 'text-slate-300' : 'text-slate-700'}`

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-6 h-6 rounded-full border-2 border-violet-500/20 border-t-violet-500 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <p className="text-center py-8 text-sm text-red-400">{error}</p>
    )
  }

  if (!logs.length) {
    return (
      <p className={`text-center py-8 text-sm ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
        No sync runs yet. Trigger a sync to get started.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className={`border-b ${isDark ? 'border-white/5' : 'border-slate-100'}`}>
            <th className={th}>Time</th>
            <th className={th}>Fetched</th>
            <th className={th}>Created</th>
            <th className={th}>Updated</th>
            <th className={th}>Status</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, i) => {
            const hasErrors = log.errors && log.errors.length > 0
            const status = hasErrors ? 'error' : 'success'
            return (
              <tr
                key={i}
                className={`border-b transition-colors duration-150
                  ${isDark ? 'border-white/[0.04] hover:bg-white/[0.02]' : 'border-slate-50 hover:bg-violet-50/40'}`}
              >
                <td className={`${td} font-mono text-xs`}>{fmt(log.sync_time)}</td>
                <td className={td}>{log.rows_fetched}</td>
                <td className={`${td} text-emerald-400 font-medium`}>+{log.rows_created}</td>
                <td className={`${td} text-sky-400 font-medium`}>~{log.rows_updated}</td>
                <td className={td}>
                  <StatusBadge
                    status={status}
                    label={hasErrors ? `${log.errors.length} error${log.errors.length > 1 ? 's' : ''}` : 'Clean'}
                    pulse={false}
                  />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
