export default function GlassCard({ children, className = '', hover = false, onClick }) {
  return (
    <div
      onClick={onClick}
      className={`glass rounded-2xl transition-all duration-300
        dark:glass-card-dark glass-card-light
        ${hover ? 'cursor-pointer hover:-translate-y-1 hover:shadow-2xl dark:hover:shadow-violet-900/20 hover:shadow-violet-100' : ''}
        ${onClick ? 'cursor-pointer' : ''}
        ${className}`}
    >
      {children}
    </div>
  )
}
