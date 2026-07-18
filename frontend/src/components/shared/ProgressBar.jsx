const COLOR_MAP = {
  primary: 'bg-primary',
  secondary: 'bg-secondary',
  tertiary: 'bg-tertiary',
  error: 'bg-error',
}

/**
 * pct expected as a 0-100 number. Clamped defensively -- upstream data
 * (e.g. a category's % of total spend) should already be 0-100, but a
 * silently-broken bar (>100% width, negative width) is a worse failure
 * mode than clamping.
 */
export default function ProgressBar({ pct, color = 'primary', className = '' }) {
  const clamped = Math.max(0, Math.min(100, pct))
  return (
    <div className={`w-full h-2 bg-surface-container rounded-full overflow-hidden ${className}`}>
      <div
        className={`h-full rounded-full ${COLOR_MAP[color]}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}