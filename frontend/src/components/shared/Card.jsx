export default function Card({ children, className = '', accent = false }) {
  return (
    <div
      className={`
        bg-surface-container-lowest border border-outline-variant rounded-xl p-lg
        shadow-[0_4px_12px_-2px_rgba(28,28,26,0.08),0_2px_4px_-2px_rgba(28,28,26,0.04)]
        ${accent ? 'bg-primary text-on-primary border-primary' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  )
}