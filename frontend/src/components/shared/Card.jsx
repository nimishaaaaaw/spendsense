export default function Card({ children, className = '', accent = false }) {
  const baseClasses = accent
    ? 'bg-primary text-on-primary border border-primary'
    : 'bg-surface-container-lowest border border-outline-variant'

  return (
    <div
      className={`
        ${baseClasses} rounded-xl p-lg
        shadow-[0_4px_12px_-2px_rgba(28,28,26,0.08),0_2px_4px_-2px_rgba(28,28,26,0.04)]
        ${className}
      `}
    >
      {children}
    </div>
  )
}