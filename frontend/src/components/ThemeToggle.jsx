export default function ThemeToggle({ isDark, toggle }) {
  return (
    <button
      onClick={toggle}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className={`relative w-[52px] h-7 rounded-full transition-all duration-300
        focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500
        ${isDark
          ? 'bg-violet-950/60 border border-violet-700/40'
          : 'bg-amber-50 border border-amber-200'
        }`}
    >
      <span
        className={`absolute top-0.5 w-6 h-6 rounded-full flex items-center justify-center text-[13px]
          shadow-md transition-all duration-300 ease-in-out
          ${isDark
            ? 'left-[calc(100%-26px)] bg-violet-900'
            : 'left-0.5 bg-white'
          }`}
      >
        {isDark ? '🌙' : '☀️'}
      </span>
    </button>
  )
}
