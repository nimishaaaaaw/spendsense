import Card from '../shared/Card.jsx'
import ProgressBar from '../shared/ProgressBar.jsx'

export default function SpendingLeaksCard({ leaks }) {
  if (!leaks || leaks.length === 0) {
    return (
      <Card>
        <h2 className="font-headline-md text-headline-md mb-md">Spending Leaks</h2>
        <p className="text-on-surface-variant font-body-md">
          No leak categories detected yet — need more frequent small transactions to identify a pattern.
        </p>
      </Card>
    )
  }

  const maxTotal = leaks[0].total

  return (
    <Card>
      <h2 className="font-headline-md text-headline-md mb-xs">Spending Leaks</h2>
      <p className="font-body-md text-on-surface-variant mb-lg">
        Categories with frequent, small transactions that add up.
      </p>
      <div className="flex flex-col gap-md">
        {leaks.map((leak) => (
          <div key={leak.category}>
            <div className="flex justify-between font-label-md mb-xs">
              <span className="text-on-surface">{leak.category}</span>
              <span className="font-bold text-on-surface">₹{leak.total.toLocaleString('en-IN')}</span>
            </div>
            <ProgressBar pct={(leak.total / maxTotal) * 100} color="tertiary" />
            <p className="font-label-sm text-on-surface-variant mt-xs">
              {leak.count} transactions · ₹{leak.avg_transaction.toLocaleString('en-IN')} average
            </p>
          </div>
        ))}
      </div>
    </Card>
  )
}