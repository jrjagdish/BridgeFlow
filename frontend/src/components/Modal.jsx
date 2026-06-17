import { useEffect } from 'react'

export default function Modal({ open, onClose, title, children, isDark, width = 'max-w-lg' }) {
  // close on Escape
  useEffect(() => {
    if (!open) return
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      />

      {/* Panel */}
      <div className={`relative w-full ${width} glass rounded-3xl shadow-2xl animate-slide-up
        ${isDark ? 'glass-card-dark shadow-violet-900/30' : 'glass-card-light shadow-violet-200/50'}`}>

        {/* Header */}
        <div className={`flex items-center justify-between px-7 pt-7 pb-5 border-b
          ${isDark ? 'border-white/[0.06]' : 'border-slate-100'}`}>
          <h2 className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-800'}`}>
            {title}
          </h2>
          <button
            onClick={onClose}
            className={`w-8 h-8 rounded-xl flex items-center justify-center text-lg transition-colors
              ${isDark ? 'hover:bg-white/10 text-slate-400 hover:text-white' : 'hover:bg-slate-100 text-slate-400 hover:text-slate-700'}`}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="px-7 py-6">
          {children}
        </div>
      </div>
    </div>
  )
}
