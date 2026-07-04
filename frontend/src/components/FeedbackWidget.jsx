import { useState } from 'react'
import { sendFeedback } from '../api'

export default function FeedbackWidget({ isDark }) {
  const [open, setOpen]       = useState(false)
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [sent, setSent]       = useState(false)
  const [error, setError]     = useState(null)

  const handleSend = async () => {
    const trimmed = message.trim()
    if (!trimmed) return
    setSending(true)
    setError(null)
    try {
      await sendFeedback(trimmed)
      setMessage('')
      setSent(true)
      setTimeout(() => {
        setSent(false)
        setOpen(false)
      }, 2200)
    } catch (e) {
      setError(e.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      {open && (
        <div className={`fixed bottom-36 md:bottom-24 right-5 z-50 w-80 max-w-[calc(100vw-2.5rem)]
          glass rounded-3xl shadow-2xl animate-slide-up overflow-hidden
          ${isDark ? 'glass-card-dark shadow-violet-900/30' : 'glass-card-light shadow-violet-200/50'}`}>

          <div className={`flex items-start justify-between gap-3 px-5 py-4 border-b
            ${isDark ? 'border-white/[0.06]' : 'border-slate-100'}`}>
            <div>
              <p className={`font-bold text-sm ${isDark ? 'text-white' : 'text-slate-800'}`}>
                💬 Send Feedback
              </p>
              <p className={`text-xs mt-0.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                Found a bug, or got an idea? Let us know.
              </p>
            </div>
            <button
              onClick={() => setOpen(false)}
              className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm shrink-0 transition-colors
                ${isDark ? 'hover:bg-white/10 text-slate-400 hover:text-white' : 'hover:bg-slate-100 text-slate-400 hover:text-slate-700'}`}
            >
              ✕
            </button>
          </div>

          <div className="p-5">
            {sent ? (
              <div className="flex flex-col items-center text-center gap-2 py-4 animate-fade-in">
                <span className="text-3xl">🎉</span>
                <p className={`text-sm font-semibold ${isDark ? 'text-emerald-300' : 'text-emerald-600'}`}>
                  Thanks! We got your feedback.
                </p>
              </div>
            ) : (
              <>
                <textarea
                  value={message}
                  onChange={e => setMessage(e.target.value)}
                  placeholder="Tell us what's working, what's not…"
                  rows={4}
                  maxLength={2000}
                  autoFocus
                  className={`w-full px-4 py-3 rounded-xl text-sm resize-none transition-all duration-150 outline-none
                    border focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/50
                    ${isDark
                      ? 'bg-white/[0.04] border-white/10 text-slate-200 placeholder-slate-600 focus:bg-white/[0.06]'
                      : 'bg-white/80 border-slate-200 text-slate-800 placeholder-slate-400 focus:bg-white'}`}
                />
                {error && (
                  <p className="mt-2 text-xs text-red-400 bg-red-400/10 border border-red-400/20 px-3 py-2 rounded-xl">
                    {error}
                  </p>
                )}
                <button
                  onClick={handleSend}
                  disabled={sending || !message.trim()}
                  className="btn-primary w-full mt-3 justify-center text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {sending
                    ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    : 'Send'}
                </button>
              </>
            )}
          </div>
        </div>
      )}

      <button
        onClick={() => setOpen(o => !o)}
        title="Send feedback"
        className="fixed bottom-20 md:bottom-6 right-5 z-50 w-14 h-14 rounded-full flex items-center justify-center
          text-2xl text-white shadow-lg hover:shadow-xl transition-all duration-200 active:scale-95"
        style={{
          background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
          boxShadow: '0 8px 32px rgba(124, 58, 237, 0.4)',
        }}
      >
        {open ? '✕' : '💬'}
      </button>
    </>
  )
}
