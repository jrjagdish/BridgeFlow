const variants = {
  success: {
    dot: 'bg-emerald-400',
    text: 'text-emerald-400',
    bg: 'dark:bg-emerald-400/10 bg-emerald-50 dark:border-emerald-400/20 border-emerald-200',
  },
  error: {
    dot: 'bg-red-400',
    text: 'text-red-400',
    bg: 'dark:bg-red-400/10 bg-red-50 dark:border-red-400/20 border-red-200',
  },
  warning: {
    dot: 'bg-amber-400',
    text: 'text-amber-400',
    bg: 'dark:bg-amber-400/10 bg-amber-50 dark:border-amber-400/20 border-amber-200',
  },
  idle: {
    dot: 'bg-slate-400',
    text: 'dark:text-slate-400 text-slate-500',
    bg: 'dark:bg-slate-400/10 bg-slate-100 dark:border-slate-400/20 border-slate-200',
  },
  soon: {
    dot: 'bg-violet-400',
    text: 'text-violet-400',
    bg: 'dark:bg-violet-400/10 bg-violet-50 dark:border-violet-400/20 border-violet-200',
  },
}

export default function StatusBadge({ status = 'idle', label, pulse = false }) {
  const v = variants[status] ?? variants.idle
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${v.bg} ${v.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${v.dot} ${pulse ? 'animate-pulse' : ''}`} />
      {label}
    </span>
  )
}
