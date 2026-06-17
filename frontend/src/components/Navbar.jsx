import ThemeToggle from './ThemeToggle'

export default function Navbar({ isDark, toggleTheme, user, onLogout, landingLinks }) {
  return (
    <nav className={`fixed top-0 inset-x-0 z-50 flex items-center justify-between px-6 py-4
      glass backdrop-blur-2xl border-b
      ${isDark ? 'border-white/[0.06] bg-black/20' : 'border-violet-100/60 bg-white/30'}`}>

      {/* Logo */}
      <a href="#" className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
          <span className="text-white text-sm font-black">B</span>
        </div>
        <span className={`font-bold text-lg tracking-tight ${isDark ? 'text-white' : 'text-slate-800'}`}>
          Bridge<span className="text-gradient">Flow</span>
        </span>
      </a>

      {/* Landing nav links */}
      {landingLinks && (
        <div className="hidden sm:flex items-center gap-1">
          {landingLinks.map(link => (
            <a
              key={link.href}
              href={link.href}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                ${isDark
                  ? 'text-slate-400 hover:text-white hover:bg-white/8'
                  : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'}`}
            >
              {link.label}
            </a>
          ))}
        </div>
      )}

      {/* Right side */}
      <div className="flex items-center gap-4">
        {user && (
          <>
            <div className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium
              ${isDark ? 'bg-white/5 text-slate-300 border border-white/10' : 'bg-violet-50 text-violet-700 border border-violet-100'}`}>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              {user.email}
            </div>
            <button
              onClick={onLogout}
              className={`text-sm font-medium px-4 py-1.5 rounded-full transition-all duration-200
                ${isDark
                  ? 'text-slate-400 hover:text-white hover:bg-white/5'
                  : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'}`}
            >
              Logout
            </button>
          </>
        )}
        <ThemeToggle isDark={isDark} toggle={toggleTheme} />
      </div>
    </nav>
  )
}
