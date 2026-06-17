import { useState, useEffect, useCallback } from 'react'
import { useTheme } from './hooks/useTheme'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import { getMe } from './api'

export default function App() {
  const { theme, toggle, isDark } = useTheme()
  const [user, setUser] = useState(null)
  const [checking, setChecking] = useState(true)

  const refreshUser = useCallback(() => {
    getMe().then(setUser).catch(() => setUser(null))
  }, [])

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  const bgClass = isDark ? 'bg-mesh-dark text-slate-100' : 'bg-mesh-light text-slate-800'

  if (checking) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${bgClass}`}>
        <div className="flex flex-col items-center gap-4 animate-fade-in">
          <div className="w-10 h-10 rounded-full border-2 border-violet-500/20 border-t-violet-500 animate-spin" />
          <p className="text-sm text-slate-400 tracking-wide">Loading BridgeFlow…</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen ${bgClass} transition-colors duration-500`}>
      {user
        ? <Dashboard user={user} isDark={isDark} toggleTheme={toggle} onLogout={() => setUser(null)} onUserRefresh={refreshUser} />
        : <Landing isDark={isDark} toggleTheme={toggle} onLogin={setUser} />
      }
    </div>
  )
}
