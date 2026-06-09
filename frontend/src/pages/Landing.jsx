import { useState } from 'react'
import Navbar from '../components/Navbar'
import { getOAuthStartUrl } from '../api'

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="w-5 h-5 shrink-0">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
    </svg>
  )
}

function NotionIcon() {
  return (
    <svg viewBox="0 0 24 24" className="w-5 h-5 shrink-0" fill="currentColor">
      <path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.139c-.093-.514.28-.887.747-.933z"/>
    </svg>
  )
}

const features = [
  {
    icon: '⚡',
    title: 'Real-time Sync',
    desc: 'Automatically syncs your Google Sheets data to Notion every 5 minutes. No manual exports.',
  },
  {
    icon: '👥',
    title: 'Multi-user',
    desc: 'Each user connects their own Google account. Tokens are stored securely per user in the database.',
  },
  {
    icon: '🔒',
    title: 'Secure by design',
    desc: 'HTTP-only session cookies. Tokens never touch the browser. Built with OAuth 2.0 best practices.',
  },
]

export default function Landing({ isDark, toggleTheme, onLogin }) {
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState(null)

  const handleGoogleConnect = async () => {
    setLoading(true)
    setErr(null)
    try {
      const url = await getOAuthStartUrl()
      window.location.href = url
    } catch {
      setErr('Could not reach the server. Make sure the backend is running on port 8000.')
      setLoading(false)
    }
  }

  const orb = 'absolute rounded-full blur-3xl pointer-events-none'

  return (
    <div className="relative min-h-screen flex flex-col overflow-hidden">

      {/* Background orbs */}
      <div className={`${orb} w-[500px] h-[500px] top-[-100px] left-[-80px]
        ${isDark ? 'bg-violet-700/15' : 'bg-violet-400/20'} animate-float`} />
      <div className={`${orb} w-[400px] h-[400px] bottom-[-60px] right-[-60px]
        ${isDark ? 'bg-cyan-600/10' : 'bg-cyan-400/15'} animate-float-slow`} />
      <div className={`${orb} w-[300px] h-[300px] top-[40%] right-[10%]
        ${isDark ? 'bg-indigo-600/10' : 'bg-indigo-400/15'} animate-float-fast`} />

      <Navbar isDark={isDark} toggleTheme={toggleTheme} />

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 pt-24 pb-16 text-center">

        {/* Tag chip */}
        <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold mb-8 border
          animate-fade-in
          ${isDark
            ? 'bg-violet-500/10 border-violet-500/20 text-violet-300'
            : 'bg-violet-100 border-violet-200 text-violet-700'}`}>
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
          Open Source · Self-hosted · v2
        </div>

        {/* Headline */}
        <h1 className="text-5xl sm:text-7xl font-black tracking-tight leading-[1.05] mb-6 animate-slide-up max-w-3xl">
          Bridge your data.<br />
          <span className="text-gradient">Automate</span> your workflow.
        </h1>

        {/* Subtitle */}
        <p className={`text-lg sm:text-xl max-w-xl leading-relaxed mb-10 animate-slide-up-d1
          ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
          Sync Google Sheets to Notion automatically — for every user on your team.
          Set it up once, forget about it.
        </p>

        {/* Error */}
        {err && (
          <p className="mb-6 text-sm text-red-400 bg-red-400/10 border border-red-400/20 px-4 py-2 rounded-xl">
            {err}
          </p>
        )}

        {/* CTA buttons */}
        <div className="flex flex-col sm:flex-row items-center gap-4 animate-slide-up-d2">
          <button
            onClick={handleGoogleConnect}
            disabled={loading}
            className={`inline-flex items-center gap-3 px-8 py-4 rounded-2xl font-semibold text-base
              transition-all duration-200 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed
              ${isDark
                ? 'bg-white text-slate-800 hover:bg-slate-50 shadow-2xl shadow-white/10'
                : 'bg-slate-900 text-white hover:bg-slate-800 shadow-2xl shadow-slate-900/20'}`}
          >
            {loading
              ? <span className="w-5 h-5 rounded-full border-2 border-current/30 border-t-current animate-spin" />
              : <GoogleIcon />
            }
            {loading ? 'Redirecting…' : 'Connect with Google'}
          </button>

          <button
            disabled
            className={`inline-flex items-center gap-3 px-8 py-4 rounded-2xl font-semibold text-base
              cursor-not-allowed opacity-50 border
              ${isDark
                ? 'border-white/10 text-slate-300'
                : 'border-slate-200 text-slate-500'}`}
          >
            <NotionIcon />
            Notion — Coming soon
          </button>
        </div>

        {/* Feature cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-24 max-w-3xl w-full animate-slide-up-d3">
          {features.map((f) => (
            <div
              key={f.title}
              className={`glass rounded-2xl p-5 text-left
                ${isDark ? 'glass-card-dark' : 'glass-card-light'}`}
            >
              <div className="text-2xl mb-3">{f.icon}</div>
              <h3 className={`font-semibold mb-1.5 ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
                {f.title}
              </h3>
              <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className={`text-center py-6 text-xs ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
        BridgeFlow v2 · Built with FastAPI + React
      </footer>
    </div>
  )
}
