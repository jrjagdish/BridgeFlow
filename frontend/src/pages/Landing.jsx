import { useState } from 'react'
import Navbar from '../components/Navbar'
import { getOAuthStartUrl } from '../api'
import { useInView } from '../hooks/useInView'

// ─── Brand icons ─────────────────────────────────────────────────────────────

function GoogleSheetsIcon({ className = 'w-8 h-8' }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none">
      <rect width="24" height="24" rx="4" fill="#1FA463"/>
      <rect x="6" y="7" width="12" height="1.5" rx="0.5" fill="white" opacity="0.9"/>
      <rect x="6" y="10.5" width="12" height="1.5" rx="0.5" fill="white" opacity="0.7"/>
      <rect x="6" y="14" width="8" height="1.5" rx="0.5" fill="white" opacity="0.5"/>
      <rect x="15" y="3" width="5" height="5" rx="0" fill="#16803A"/>
      <path d="M15 3 l5 5" stroke="#0F5C2E" strokeWidth="0.5"/>
      <rect x="15" y="3" width="5" height="5" rx="0" fill="white" opacity="0.15"/>
    </svg>
  )
}

function NotionIcon({ className = 'w-8 h-8' }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor">
      <path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.139c-.093-.514.28-.887.747-.933z"/>
    </svg>
  )
}

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

// ─── Flow diagram (hero visual) ───────────────────────────────────────────────

function FlowDiagram({ isDark }) {
  const card = `flex flex-col items-center gap-2 px-5 py-4 rounded-2xl border transition-all duration-300
    ${isDark ? 'bg-white/5 border-white/10' : 'bg-white/80 border-violet-100'}`

  return (
    <div className="flex items-center gap-3 sm:gap-5 mt-8 mb-1 animate-slide-up-d3">
      {/* Google Sheets node */}
      <div className={card}>
        <GoogleSheetsIcon className="w-9 h-9" />
        <span className={`text-xs font-semibold ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
          Google Sheets
        </span>
        <div className={`flex flex-col gap-1 mt-1 w-24`}>
          {['Row 1','Row 2','Row 3'].map((r, i) => (
            <div key={r} className={`h-1.5 rounded-full ${isDark ? 'bg-emerald-400/40' : 'bg-emerald-400/50'}`}
              style={{ width: `${70 + i * 10}%`, animationDelay: `${i * 0.2}s` }} />
          ))}
        </div>
      </div>

      {/* Arrow with animated dots */}
      <div className="flex flex-col items-center gap-1.5 relative">
        <div className={`text-[10px] font-medium ${isDark ? 'text-violet-300' : 'text-violet-600'}`}>auto-sync</div>
        <div className={`relative w-20 sm:w-28 h-0.5 ${isDark ? 'bg-violet-500/20' : 'bg-violet-200'} overflow-hidden`}>
          <div className={`absolute top-0 left-0 h-full w-3 rounded-full bg-violet-500 animate-flow-dot`} />
          <div className={`absolute top-0 left-0 h-full w-3 rounded-full bg-violet-400 animate-flow-dot-d1`} />
          <div className={`absolute top-0 left-0 h-full w-3 rounded-full bg-violet-300 animate-flow-dot-d2`} />
        </div>
        <svg className={`w-3 h-3 ${isDark ? 'text-violet-400' : 'text-violet-500'}`} viewBox="0 0 12 12" fill="currentColor">
          <path d="M6 0l6 6-6 6V8H0V4h6V0z"/>
        </svg>
      </div>

      {/* BridgeFlow node */}
      <div className={`${card} ring-2 ${isDark ? 'ring-violet-500/30' : 'ring-violet-400/30'}`}>
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
          <span className="text-white text-base font-black">B</span>
        </div>
        <span className={`text-xs font-semibold ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>BridgeFlow</span>
        <div className={`flex items-center gap-1 mt-1`}>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className={`text-[10px] ${isDark ? 'text-emerald-400' : 'text-emerald-600'}`}>Live</span>
        </div>
      </div>

      {/* Arrow */}
      <div className="flex flex-col items-center gap-1.5 relative">
        <div className={`text-[10px] font-medium ${isDark ? 'text-cyan-300' : 'text-cyan-600'}`}>push</div>
        <div className={`relative w-20 sm:w-28 h-0.5 ${isDark ? 'bg-cyan-500/20' : 'bg-cyan-200'} overflow-hidden`}>
          <div className={`absolute top-0 left-0 h-full w-3 rounded-full bg-cyan-500 animate-flow-dot`} />
          <div className={`absolute top-0 left-0 h-full w-3 rounded-full bg-cyan-400 animate-flow-dot-d1`} />
          <div className={`absolute top-0 left-0 h-full w-3 rounded-full bg-cyan-300 animate-flow-dot-d2`} />
        </div>
        <svg className={`w-3 h-3 ${isDark ? 'text-cyan-400' : 'text-cyan-500'}`} viewBox="0 0 12 12" fill="currentColor">
          <path d="M6 0l6 6-6 6V8H0V4h6V0z"/>
        </svg>
      </div>

      {/* Notion node */}
      <div className={card}>
        <div className={`w-9 h-9 flex items-center justify-center rounded-xl ${isDark ? 'bg-white/10 text-white' : 'bg-slate-800 text-white'}`}>
          <NotionIcon className="w-5 h-5" />
        </div>
        <span className={`text-xs font-semibold ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>Notion DB</span>
        <div className="flex flex-col gap-1 mt-1 w-24">
          {['Page 1','Page 2','Page 3'].map((p, i) => (
            <div key={p} className={`flex items-center gap-1`}>
              <span className="w-1 h-1 rounded-full bg-cyan-400 opacity-70" />
              <div className={`h-1.5 rounded-full ${isDark ? 'bg-cyan-400/30' : 'bg-cyan-400/40'}`}
                style={{ width: `${65 + i * 8}%` }} />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ─── Section: How it works ────────────────────────────────────────────────────

const steps = [
  {
    num: '01',
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z"/>
      </svg>
    ),
    title: 'Connect your Google account',
    desc: 'Sign in with Google OAuth in one click. Your credentials are never stored — only secure tokens.',
  },
  {
    num: '02',
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75.125V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m0 0h17.25m0 0h1.5c.621 0 1.125-.504 1.125-1.125V5.625m-18.75 0A1.125 1.125 0 014.5 4.5h15a1.125 1.125 0 011.125 1.125M21.75 5.625v12.75"/>
      </svg>
    ),
    title: 'Pick your Google Sheet',
    desc: 'Paste the spreadsheet ID and choose the sheet. BridgeFlow previews your columns instantly.',
  },
  {
    num: '03',
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5"/>
      </svg>
    ),
    title: 'Map columns to Notion properties',
    desc: 'Drag and drop your sheet columns to Notion database properties. Supports text, numbers, dates, and selects.',
  },
  {
    num: '04',
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>
      </svg>
    ),
    title: 'Syncs automatically every 5 minutes',
    desc: 'BridgeFlow detects new and changed rows and pushes only the diff to Notion. Zero duplicates.',
  },
]

// ─── Section: Features ────────────────────────────────────────────────────────

const features = [
  {
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>
      </svg>
    ),
    color: 'text-violet-400',
    bg: 'bg-violet-500/10',
    title: 'Real-time Sync',
    desc: 'Automatically syncs every 5 minutes. No manual exports, no copy-pasting.',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M7.5 3.75H6A2.25 2.25 0 003.75 6v1.5M7.5 3.75h9M7.5 3.75v16.5m9-16.5H18A2.25 2.25 0 0120.25 6v1.5m-9-3.75v16.5m0 0h-2.25m2.25 0h2.25M3.75 7.5H1.5m2.25 0H6m-2.25 0v9A2.25 2.25 0 006 18.75h1.5m12-11.25H22.5m-2.25 0H18m2.25 0v9a2.25 2.25 0 01-2.25 2.25H16.5"/>
      </svg>
    ),
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
    title: 'Smart diffing',
    desc: 'Hashes every row. Only changed or new rows are pushed — Notion API quota stays low.',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z"/>
      </svg>
    ),
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10',
    title: 'Multi-user',
    desc: 'Each user connects their own Google and Notion accounts. Fully isolated per-user config.',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
      </svg>
    ),
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    title: 'Secure by design',
    desc: 'HTTP-only cookies, OAuth 2.0, tokens stored encrypted in Postgres. Nothing in localStorage.',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15"/>
      </svg>
    ),
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
    title: 'Full audit trail',
    desc: 'Every sync run is logged — rows fetched, created, updated, skipped, errors. Nothing is hidden.',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"/>
      </svg>
    ),
    color: 'text-pink-400',
    bg: 'bg-pink-500/10',
    title: 'Open source',
    desc: 'Self-host on your own infra. Full source on GitHub — no vendor lock-in, ever.',
  },
]

// ─── Section: Pricing ─────────────────────────────────────────────────────────

const plans = [
  {
    name: 'Free',
    tag: 'Self-hosted',
    price: '$0',
    period: 'forever',
    desc: 'Everything you need to run BridgeFlow on your own server.',
    cta: 'Get started',
    ctaAction: true,
    highlight: false,
    perks: [
      'Unlimited syncs',
      '5-minute sync interval',
      'Unlimited users',
      'Full feature access',
      'Audit logs',
      'Open source (MIT)',
    ],
  },
  {
    name: 'Pro',
    tag: 'Coming soon',
    price: '$9',
    period: 'per month',
    desc: 'Hosted by us — no server, no ops. Just connect and go.',
    cta: 'Join waitlist',
    ctaAction: false,
    highlight: true,
    perks: [
      'Everything in Free',
      'Hosted — no server needed',
      '1-minute sync intervals',
      'Priority support',
      'Multiple workspaces',
      'Analytics dashboard',
    ],
  },
]

// ─── Reusable section wrapper ────────────────────────────────────────────────

function Section({ id, children, className = '' }) {
  const [ref, inView] = useInView()
  return (
    <section
      id={id}
      ref={ref}
      className={`reveal ${inView ? 'in-view' : ''} ${className}`}
    >
      {children}
    </section>
  )
}

function SectionLabel({ isDark, children }) {
  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold mb-4 border
      ${isDark ? 'bg-violet-500/10 border-violet-500/20 text-violet-300' : 'bg-violet-100 border-violet-200 text-violet-700'}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
      {children}
    </div>
  )
}

// ─── Landing page ─────────────────────────────────────────────────────────────

export default function Landing({ isDark, toggleTheme }) {
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
    <div className="relative flex flex-col overflow-hidden">
      {/* Background orbs */}
      <div className={`${orb} w-[600px] h-[600px] top-[-120px] left-[-100px]
        ${isDark ? 'bg-violet-700/15' : 'bg-violet-400/20'} animate-float`} />
      <div className={`${orb} w-[400px] h-[400px] bottom-[10%] right-[-80px]
        ${isDark ? 'bg-cyan-600/10' : 'bg-cyan-400/15'} animate-float-slow`} />
      <div className={`${orb} w-[300px] h-[300px] top-[45%] right-[8%]
        ${isDark ? 'bg-indigo-600/10' : 'bg-indigo-400/15'} animate-float-fast`} />

      <Navbar
        isDark={isDark}
        toggleTheme={toggleTheme}
        landingLinks={[
          { label: 'How it works', href: '#how-it-works' },
          { label: 'Features', href: '#features' },
          { label: 'Pricing', href: '#pricing' },
        ]}
      />

      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <section className="flex flex-col items-center justify-center px-6 pt-28 pb-10 text-center">
        <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold mb-5 border animate-fade-in
          ${isDark ? 'bg-violet-500/10 border-violet-500/20 text-violet-300' : 'bg-violet-100 border-violet-200 text-violet-700'}`}>
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
          Open Source · Self-hosted · v2
        </div>

        <h1 className="text-5xl sm:text-7xl font-black tracking-tight leading-[1.05] mb-4 animate-slide-up max-w-4xl">
          Your spreadsheet data,<br />
          <span className="text-gradient">live in Notion.</span>
        </h1>

        <p className={`text-lg sm:text-xl max-w-xl leading-relaxed mb-7 animate-slide-up-d1
          ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
          BridgeFlow syncs Google Sheets to Notion automatically — for every user on your team.
          Set it up once, forget about it.
        </p>

        {err && (
          <p className="mb-6 text-sm text-red-400 bg-red-400/10 border border-red-400/20 px-4 py-2 rounded-xl">
            {err}
          </p>
        )}

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
              : <GoogleIcon />}
            {loading ? 'Redirecting…' : 'Get started free'}
          </button>

          <a
            href="#how-it-works"
            className={`inline-flex items-center gap-2 px-8 py-4 rounded-2xl font-semibold text-base border
              transition-all duration-200 hover:scale-105
              ${isDark ? 'border-white/10 text-slate-300 hover:bg-white/5' : 'border-slate-200 text-slate-600 hover:bg-white'}`}
          >
            See how it works
            <svg viewBox="0 0 20 20" className="w-4 h-4" fill="currentColor">
              <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd"/>
            </svg>
          </a>
        </div>

        {/* Flow diagram */}
        <FlowDiagram isDark={isDark} />

        {/* Stats strip */}
        <div className={`flex gap-8 sm:gap-16 mt-6 animate-slide-up-d3`}>
          {[
            { num: '5 min', label: 'sync interval' },
            { num: '100%', label: 'open source' },
            { num: '0', label: 'vendor lock-in' },
          ].map(s => (
            <div key={s.label} className="flex flex-col items-center gap-0.5">
              <span className={`text-2xl font-black ${isDark ? 'text-white' : 'text-slate-800'}`}>{s.num}</span>
              <span className={`text-xs ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── Integration logos ─────────────────────────────────────────── */}
      <Section className="py-6 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <p className={`text-sm font-medium mb-5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
            Connects the tools your team already uses
          </p>
          <div className="flex items-center justify-center gap-10 sm:gap-16 flex-wrap">
            <div className="flex flex-col items-center gap-2 opacity-80 hover:opacity-100 transition-opacity">
              <GoogleSheetsIcon className="w-12 h-12" />
              <span className={`text-sm font-medium ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Google Sheets</span>
            </div>
            <div className={`text-3xl font-thin ${isDark ? 'text-slate-600' : 'text-slate-300'}`}>→</div>
            <div className="flex flex-col items-center gap-2 opacity-80 hover:opacity-100 transition-opacity">
              <div className={`w-12 h-12 flex items-center justify-center rounded-2xl
                ${isDark ? 'bg-white/10 text-white' : 'bg-slate-800 text-white'}`}>
                <NotionIcon className="w-7 h-7" />
              </div>
              <span className={`text-sm font-medium ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Notion</span>
            </div>
          </div>
        </div>
      </Section>

      {/* ── How it works ─────────────────────────────────────────────── */}
      <Section id="how-it-works" className="py-14 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <SectionLabel isDark={isDark}>How it works</SectionLabel>
          <h2 className={`text-3xl sm:text-4xl font-black mb-2 ${isDark ? 'text-white' : 'text-slate-900'}`}>
            Up and running in 4 steps
          </h2>
          <p className={`text-base mb-8 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
            No code. No complicated setup. Just connect and configure.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 stagger">
            {steps.map((step) => (
              <div
                key={step.num}
                className={`reveal in-view group relative p-6 rounded-2xl border text-left
                  transition-all duration-300 cursor-default
                  ${isDark
                    ? 'bg-white/[0.03] border-white/[0.07] hover:bg-white/[0.06] card-glow-dark'
                    : 'bg-white/70 border-violet-100 hover:bg-white card-glow-light'}`}
              >
                <div className={`absolute -top-3 -left-3 w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-black
                  bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-500/30`}>
                  {step.num.slice(1)}
                </div>
                <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-4 text-violet-400
                  ${isDark ? 'bg-violet-500/10' : 'bg-violet-50'}`}>
                  {step.icon}
                </div>
                <h3 className={`font-bold text-sm mb-2 ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
                  {step.title}
                </h3>
                <p className={`text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* ── Features ─────────────────────────────────────────────────── */}
      <Section id="features" className="py-14 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <SectionLabel isDark={isDark}>Features</SectionLabel>
          <h2 className={`text-3xl sm:text-4xl font-black mb-2 ${isDark ? 'text-white' : 'text-slate-900'}`}>
            Everything you need, nothing you don't
          </h2>
          <p className={`text-base mb-8 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
            Built for reliability. Designed for developers who want full control.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 stagger">
            {features.map((f) => (
              <div
                key={f.title}
                className={`reveal in-view group p-6 rounded-2xl border text-left
                  transition-all duration-300 cursor-default
                  ${isDark
                    ? 'bg-white/[0.03] border-white/[0.07] hover:bg-white/[0.06] card-glow-dark'
                    : 'bg-white/70 border-violet-100 hover:bg-white card-glow-light'}`}
              >
                <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-4 ${f.bg} ${f.color}`}>
                  {f.icon}
                </div>
                <h3 className={`font-bold mb-2 ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>{f.title}</h3>
                <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* ── Pricing ──────────────────────────────────────────────────── */}
      <Section id="pricing" className="py-14 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <SectionLabel isDark={isDark}>Pricing</SectionLabel>
          <h2 className={`text-3xl sm:text-4xl font-black mb-2 ${isDark ? 'text-white' : 'text-slate-900'}`}>
            Simple, honest pricing
          </h2>
          <p className={`text-base mb-8 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
            Free forever if you self-host. Pay only if you want us to host it for you.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 stagger">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`reveal in-view relative p-8 rounded-3xl border text-left
                  transition-all duration-300
                  ${plan.highlight
                    ? isDark
                      ? 'bg-gradient-to-b from-violet-900/40 to-indigo-900/30 border-violet-500/30 shadow-2xl shadow-violet-500/10'
                      : 'bg-gradient-to-b from-violet-50 to-indigo-50 border-violet-300 shadow-2xl shadow-violet-200/50'
                    : isDark
                      ? 'bg-white/[0.03] border-white/[0.08]'
                      : 'bg-white/80 border-violet-100'}`}
              >
                {plan.highlight && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-xs font-bold
                    bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg">
                    Coming soon
                  </div>
                )}

                <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold mb-4
                  ${isDark ? 'bg-white/10 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                  {plan.tag}
                </div>

                <div className="flex items-end gap-1 mb-2">
                  <span className={`text-4xl font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>{plan.price}</span>
                  <span className={`text-sm mb-1.5 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>/{plan.period}</span>
                </div>

                <p className={`text-sm mb-4 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{plan.desc}</p>

                <button
                  onClick={plan.ctaAction ? handleGoogleConnect : undefined}
                  disabled={!plan.ctaAction || loading}
                  className={`w-full py-3 rounded-xl font-semibold text-sm mb-5 transition-all duration-200 active:scale-95
                    ${plan.highlight
                      ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white opacity-60 cursor-not-allowed'
                      : isDark
                        ? 'bg-white text-slate-900 hover:bg-slate-100'
                        : 'bg-slate-900 text-white hover:bg-slate-800'}`}
                >
                  {plan.cta}
                </button>

                <ul className="space-y-3">
                  {plan.perks.map(perk => (
                    <li key={perk} className="flex items-center gap-2.5 text-sm">
                      <svg viewBox="0 0 20 20" className={`w-4 h-4 shrink-0 ${plan.highlight ? 'text-violet-400' : 'text-emerald-400'}`} fill="currentColor">
                        <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clipRule="evenodd"/>
                      </svg>
                      <span className={isDark ? 'text-slate-300' : 'text-slate-600'}>{perk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* ── Final CTA ─────────────────────────────────────────────────── */}
      <Section className="py-14 px-6">
        <div className={`max-w-2xl mx-auto text-center p-10 rounded-3xl border relative overflow-hidden
          ${isDark
            ? 'bg-gradient-to-br from-violet-900/30 to-indigo-900/20 border-violet-500/20'
            : 'bg-gradient-to-br from-violet-50 to-indigo-50 border-violet-200'}`}>
          <div className={`${orb} w-64 h-64 -top-12 -right-12 ${isDark ? 'bg-violet-600/20' : 'bg-violet-300/30'}`} />
          <h2 className={`text-3xl sm:text-4xl font-black mb-4 relative ${isDark ? 'text-white' : 'text-slate-900'}`}>
            Ready to bridge your data?
          </h2>
          <p className={`text-base mb-8 relative ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
            Free to use. No credit card. Takes 2 minutes to set up.
          </p>
          <button
            onClick={handleGoogleConnect}
            disabled={loading}
            className="relative inline-flex items-center gap-3 px-8 py-4 rounded-2xl font-semibold
              bg-gradient-to-r from-violet-600 to-indigo-600 text-white
              hover:from-violet-500 hover:to-indigo-500
              shadow-xl shadow-violet-500/30 hover:shadow-violet-500/50
              transition-all duration-200 active:scale-95 disabled:opacity-60"
          >
            {loading
              ? <span className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              : <GoogleIcon />}
            {loading ? 'Redirecting…' : 'Connect with Google — it\'s free'}
          </button>
        </div>
      </Section>

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <footer className={`border-t py-6 px-6 ${isDark ? 'border-white/[0.06]' : 'border-violet-100'}`}>
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
              <span className="text-white text-xs font-black">B</span>
            </div>
            <span className={`font-bold ${isDark ? 'text-white' : 'text-slate-800'}`}>
              Bridge<span className="text-gradient">Flow</span>
            </span>
          </div>
          <p className={`text-xs ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
            © 2025 BridgeFlow · Open source · Built with FastAPI + React
          </p>
          <div className="flex items-center gap-6">
            {['Features', 'Pricing'].map(link => (
              <a
                key={link}
                href={`#${link.toLowerCase()}`}
                className={`text-xs hover:text-violet-500 transition-colors
                  ${isDark ? 'text-slate-500' : 'text-slate-400'}`}
              >
                {link}
              </a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  )
}
