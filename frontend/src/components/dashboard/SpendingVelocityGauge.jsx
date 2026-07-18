import Card from '../shared/Card.jsx'

const LABEL_COLOR = {
  slow: 'text-secondary',
  moderate: 'text-primary',
  fast: 'text-error',
  unknown: 'text-on-surface-variant',
}

const LABEL_COPY = {
  slow: 'Your spending pace is gentle relative to your salary.',
  moderate: "You're spending at a steady, moderate pace after each paycheck.",
  fast: "You're burning through your paycheck quickly after each credit.",
  unknown: 'Not enough salary credits detected yet to measure this.',
}

export default function SpendingVelocityGauge({ velocity }) {
  const label = velocity?.velocity_label || 'unknown'
  const pct = velocity?.average_pct_spent_within_7_days

  return (
    <Card className="flex flex-col items-center justify-center text-center">
      <h2 className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider mb-lg self-start">
        Spending Velocity
      </h2>
      <div className="relative w-48 h-24 overflow-hidden mb-md">
        <div
          className="w-48 h-48 rounded-full border border-outline-variant"
          style={{
            background: 'conic-gradient(from 180deg at 50% 50%, #2c2abc 0deg, #6cf8bb 180deg, #f0ede9 180deg)',
          }}
        />
      </div>
      <p className={`font-display text-headline-lg uppercase ${LABEL_COLOR[label]}`}>{label}</p>
      {pct !== null && pct !== undefined && (
        <p className="font-label-md text-on-surface-variant mt-xs">{pct}% of salary spent within 7 days</p>
      )}
      <p className="font-body-md text-on-surface-variant mt-sm max-w-xs">{LABEL_COPY[label]}</p>
    </Card>
  )
}