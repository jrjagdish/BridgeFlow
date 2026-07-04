import { useState } from 'react'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import SyncLogs from '../components/SyncLogs'
import FeedbackWidget from '../components/FeedbackWidget'
import Settings from './Settings'
import Setup from './Setup'
import { logout, triggerSync, getNotionOAuthUrl, disconnectNotion } from '../api'

// ---------------------------------------------------------------------------
// Sidebar nav item
// ---------------------------------------------------------------------------
function NavItem({ icon, label, active, onClick, isDark }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 text-left
        ${active
          ? isDark
            ? 'bg-violet-500/15 text-violet-300 border border-violet-500/20'
            : 'bg-violet-100 text-violet-700 border border-violet-200'
          : isDark
            ? 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
            : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
        }`}
    >
      <span className="text-base">{icon}</span>
      {label}
    </button>
  )
}

// ---------------------------------------------------------------------------
// Stat card
// ---------------------------------------------------------------------------
function StatCard({ label, value, sub, accent, isDark }) {
  return (
    <div className={`glass rounded-2xl p-5 transition-all duration-200
      ${isDark ? 'glass-card-dark card-glow-dark' : 'glass-card-light card-glow-light'}`}>
      <p className={`text-xs font-semibold uppercase tracking-wider mb-2 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
        {label}
      </p>
      <p className={`text-3xl font-black mb-1 ${accent}`}>{value}</p>
      {sub && <p className={`text-xs ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{sub}</p>}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Service card
// ---------------------------------------------------------------------------
function ServiceCard({ icon, name, connected, detail, onConnect, connecting, connectErr, onDisconnect, disconnecting, isDark }) {
  return (
    <div className={`glass rounded-2xl p-5 transition-all duration-200
      ${isDark ? 'glass-card-dark card-glow-dark' : 'glass-card-light card-glow-light'}`}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className={`w-11 h-11 rounded-xl flex items-center justify-center text-xl shrink-0
            ${isDark ? 'bg-white/5' : 'bg-slate-100'}`}>
            {icon}
          </div>
          <div>
            <p className={`font-semibold text-sm ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>{name}</p>
            <p className={`text-xs mt-0.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              {connected ? detail : 'Not connected'}
            </p>
          </div>
        </div>

        <div className="shrink-0 flex items-center gap-2">
          {connected ? (
            <>
              <StatusBadge status="success" label="Connected" pulse />
              {onDisconnect && (
                <button
                  onClick={onDisconnect}
                  disabled={disconnecting}
                  title="Disconnect"
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-all duration-150
                    disabled:opacity-50 disabled:cursor-not-allowed
                    ${isDark
                      ? 'border-white/10 text-slate-500 hover:text-red-400 hover:border-red-400/30 hover:bg-red-400/5'
                      : 'border-slate-200 text-slate-400 hover:text-red-500 hover:border-red-300 hover:bg-red-50'}`}
                >
                  {disconnecting
                    ? <span className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin inline-block" />
                    : 'Disconnect'}
                </button>
              )}
            </>
          ) : (
            <button
              onClick={onConnect}
              disabled={connecting}
              className="btn-primary text-xs px-4 py-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {connecting
                ? <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                : 'Connect'
              }
            </button>
          )}
        </div>
      </div>

      {connectErr && (
        <p className="mt-3 text-xs text-red-400 bg-red-400/10 border border-red-400/20 px-3 py-2 rounded-xl">
          {connectErr}
        </p>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main Dashboard
// ---------------------------------------------------------------------------
export default function Dashboard({ user, isDark, toggleTheme, onLogout, onUserRefresh }) {
  const [view, setView]               = useState('overview')
  const [syncing, setSyncing]         = useState(false)
  const [syncMsg, setSyncMsg]         = useState(null)
  const [notionConnecting, setNotionConnecting]   = useState(false)
  const [notionDisconnecting, setNotionDisconnecting] = useState(false)
  const [notionErr, setNotionErr]     = useState(null)

  const handleLogout = async () => {
    await logout()
    onLogout()
  }

  const handleSync = async () => {
    setSyncing(true)
    setSyncMsg(null)
    try {
      await triggerSync()
      setSyncMsg({ ok: true, text: 'Sync triggered! Logs will update shortly.' })
    } catch {
      setSyncMsg({ ok: false, text: 'Failed to trigger sync. Check the server.' })
    } finally {
      setSyncing(false)
      setTimeout(() => setSyncMsg(null), 4000)
    }
  }

  // Same pattern as Google: fetch auth URL → redirect browser to Notion consent screen.
  // Notion redirects back to /notion/oauth/callback on the backend, which sets the token
  // in DB and redirects back here. On reload, /me returns notion_connected: true.
  const handleNotionConnect = async () => {
    setNotionConnecting(true)
    setNotionErr(null)
    try {
      const url = await getNotionOAuthUrl()
      window.location.href = url
    } catch {
      setNotionErr('Could not reach the server. Make sure the backend is running.')
      setNotionConnecting(false)
    }
  }

  const handleNotionDisconnect = async () => {
    setNotionDisconnecting(true)
    try {
      await disconnectNotion()
      onUserRefresh()
    } catch {
      // silent — worst case user can reload
    } finally {
      setNotionDisconnecting(false)
    }
  }

  const orb = 'fixed rounded-full blur-3xl pointer-events-none opacity-30'

  return (
    <div className="relative min-h-screen flex flex-col">
      {/* Bg orbs */}
      <div className={`${orb} w-[550px] h-[550px] top-[-120px] right-[-120px]
        ${isDark ? 'bg-violet-900/40' : 'bg-violet-200/50'} animate-float-slow`} />
      <div className={`${orb} w-[350px] h-[350px] bottom-[-60px] left-[-60px]
        ${isDark ? 'bg-indigo-900/30' : 'bg-indigo-200/40'} animate-float`} />

      <Navbar isDark={isDark} toggleTheme={toggleTheme} user={user} onLogout={handleLogout} />
      <FeedbackWidget isDark={isDark} />

      <div className="flex pt-16 min-h-screen">

        {/* ── Sidebar (desktop) ── */}
        <aside className={`fixed left-0 top-16 h-[calc(100vh-64px)] w-56 flex-shrink-0
          hidden md:flex flex-col px-3 py-5 border-r glass backdrop-blur-xl
          ${isDark ? 'border-white/[0.06] bg-black/20' : 'border-slate-100 bg-white/20'}`}>

          <p className={`text-[10px] font-bold uppercase tracking-widest px-4 mb-3
            ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
            Navigation
          </p>

          <nav className="space-y-1">
            <NavItem icon="⚡" label="Overview" active={view === 'overview'} onClick={() => setView('overview')} isDark={isDark} />
            {user.google_connected && user.notion_connected && (
              <NavItem icon="🔧" label="Setup" active={view === 'setup'} onClick={() => setView('setup')} isDark={isDark} />
            )}
            <NavItem icon="⚙️" label="Settings" active={view === 'settings'} onClick={() => setView('settings')} isDark={isDark} />
          </nav>

          <div className={`mt-auto px-4 py-4 rounded-xl border text-xs
            ${isDark ? 'bg-white/[0.02] border-white/5 text-slate-600' : 'bg-slate-50 border-slate-100 text-slate-400'}`}>
            <p className="font-semibold mb-0.5">BridgeFlow v2</p>
            <p>Syncing every 5 min</p>
          </div>
        </aside>

        {/* ── Mobile bottom tab bar ── */}
        <div className={`md:hidden fixed bottom-0 inset-x-0 z-40 flex border-t glass backdrop-blur-xl
          ${isDark ? 'bg-black/40 border-white/[0.06]' : 'bg-white/60 border-slate-100'}`}>
          {[
            { icon: '⚡', label: 'Overview', key: 'overview' },
            ...(user.google_connected && user.notion_connected
              ? [{ icon: '🔧', label: 'Setup', key: 'setup' }]
              : []),
            { icon: '⚙️', label: 'Settings', key: 'settings' },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setView(tab.key)}
              className={`flex-1 flex flex-col items-center gap-1 py-3 text-xs font-medium transition-colors
                ${view === tab.key
                  ? isDark ? 'text-violet-300' : 'text-violet-600'
                  : isDark ? 'text-slate-500' : 'text-slate-400'}`}
            >
              <span className="text-lg">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── Content area ── */}
        <main className="flex-1 md:ml-56 px-5 md:px-8 pt-8 pb-24 md:pb-12">

          {/* ─── OVERVIEW ────────────────────────────────── */}
          {view === 'overview' && (
            <div className="max-w-4xl animate-fade-in">

              {/* Header */}
              <div className="flex items-center justify-between mb-7">
                <div>
                  <h1 className={`text-2xl font-black tracking-tight ${isDark ? 'text-white' : 'text-slate-800'}`}>
                    Overview
                  </h1>
                  <p className={`text-sm mt-0.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                    Your sync pipeline at a glance
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  {syncMsg && (
                    <span className={`hidden sm:block text-xs px-3 py-1.5 rounded-full border animate-fade-in
                      ${syncMsg.ok
                        ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
                        : 'text-red-400 bg-red-400/10 border-red-400/20'}`}>
                      {syncMsg.text}
                    </span>
                  )}
                  <button
                    onClick={handleSync}
                    disabled={syncing}
                    className="btn-primary text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {syncing
                      ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Syncing…</>
                      : <>⚡ Trigger Sync</>
                    }
                  </button>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
                <StatCard
                  label="Pipeline" value="Active" sub="Running every 5 min"
                  accent="text-emerald-400" isDark={isDark}
                />
                <StatCard
                  label="Google Sheets"
                  value={user.google_connected ? '✓' : '—'}
                  sub={user.google_connected ? user.email : 'Not connected'}
                  accent={user.google_connected ? 'text-violet-400' : 'text-slate-500'}
                  isDark={isDark}
                />
                <StatCard
                  label="Notion"
                  value={user.notion_connected ? '✓' : '—'}
                  sub={user.notion_connected ? 'Workspace connected' : 'Not connected'}
                  accent={user.notion_connected ? 'text-cyan-400' : 'text-slate-500'}
                  isDark={isDark}
                />
              </div>

              {/* Connected services */}
              <div className="mb-6">
                <p className={`text-xs font-bold uppercase tracking-widest mb-4
                  ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                  Connected Services
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <ServiceCard
                    icon="📊"
                    name="Google Sheets"
                    connected={user.google_connected}
                    detail={user.email}
                    isDark={isDark}
                  />
                  <ServiceCard
                    icon="📝"
                    name="Notion"
                    connected={user.notion_connected}
                    detail="Workspace connected"
                    onConnect={handleNotionConnect}
                    connecting={notionConnecting}
                    connectErr={notionErr}
                    onDisconnect={handleNotionDisconnect}
                    disconnecting={notionDisconnecting}
                    isDark={isDark}
                  />
                </div>
              </div>

              {/* Setup CTA — shown when both services are connected */}
              {user.google_connected && user.notion_connected && (
                <div className={`flex items-start gap-3 px-5 py-4 rounded-2xl border mb-6 text-sm
                  ${isDark
                    ? 'bg-violet-400/5 border-violet-400/15 text-violet-300'
                    : 'bg-violet-50 border-violet-200 text-violet-700'}`}>
                  <span className="text-xl shrink-0">🔧</span>
                  <div className="flex-1">
                    <p className="font-semibold mb-1">Ready to configure your sync pipeline</p>
                    <p className={`text-xs leading-relaxed ${isDark ? 'text-violet-400/70' : 'text-violet-600'}`}>
                      Both services are connected. Go to <strong>Setup</strong> to provide your spreadsheet ID,
                      map columns, and create a Notion database — then syncing will work automatically.
                    </p>
                  </div>
                  <button
                    onClick={() => setView('setup')}
                    className="btn-primary text-xs px-4 py-2 shrink-0"
                  >
                    Open Setup
                  </button>
                </div>
              )}

              {/* Notion OAuth explainer — shown only when not connected */}
              {!user.notion_connected && (
                <div className={`flex items-start gap-3 px-5 py-4 rounded-2xl border mb-6 text-sm
                  ${isDark
                    ? 'bg-cyan-400/5 border-cyan-400/15 text-cyan-300'
                    : 'bg-cyan-50 border-cyan-200 text-cyan-700'}`}>
                  <span className="text-xl shrink-0">💡</span>
                  <div>
                    <p className="font-semibold mb-1">One-click Notion connection</p>
                    <p className={`text-xs leading-relaxed ${isDark ? 'text-cyan-400/70' : 'text-cyan-600'}`}>
                      Click <strong>Connect</strong> above. You'll be redirected to Notion where you pick which workspace and databases to share with BridgeFlow — no copying tokens, no developer settings.
                    </p>
                  </div>
                </div>
              )}

              {/* Sync logs */}
              <div>
                <p className={`text-xs font-bold uppercase tracking-widest mb-4
                  ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                  Recent Sync Runs
                </p>
                <div className={`glass rounded-2xl p-6 transition-all duration-200
                  ${isDark ? 'glass-card-dark card-glow-dark' : 'glass-card-light card-glow-light'}`}>
                  <SyncLogs isDark={isDark} />
                </div>
              </div>
            </div>
          )}

          {/* ─── SETUP ───────────────────────────────────── */}
          {view === 'setup' && <Setup isDark={isDark} />}

          {/* ─── SETTINGS ────────────────────────────────── */}
          {view === 'settings' && <Settings isDark={isDark} />}

        </main>
      </div>
    </div>
  )
}
