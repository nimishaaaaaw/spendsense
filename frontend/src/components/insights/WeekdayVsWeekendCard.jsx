import Card from '../shared/Card.jsx'

export default function WeekdayVsWeekendCard({ data }) {
  if (!data) return null

  const { weekday_total, weekend_total, weekday_count, weekend_count, weekend_to_weekday_ratio } = data
  const maxTotal = Math.max(weekday_total, weekend_total, 1)

  return (
    <Card>
      <h2 className="font-headline-md text-headline-md mb-lg">Weekday vs Weekend</h2>
      <div className="flex items-end justify-between h-40 gap-lg px-md">
        <div className="flex-1 flex flex-col items-center gap-sm">
          <div className="w-full flex items-end justify-center" style={{ height: '120px' }}>
            <div
              className="w-full bg-primary-fixed rounded-t-xl transition-all"
              style={{ height: `${(weekday_total / maxTotal) * 100}%` }}
            />
          </div>
          <span className="font-label-md text-primary">₹{weekday_total.toLocaleString('en-IN')}</span>
          <span className="font-label-sm text-on-surface-variant uppercase">Weekday · {weekday_count} txns</span>
        </div>
        <div className="flex-1 flex flex-col items-center gap-sm">
          <div className="w-full flex items-end justify-center" style={{ height: '120px' }}>
            <div
              className="w-full bg-secondary-fixed rounded-t-xl transition-all"
              style={{ height: `${(weekend_total / maxTotal) * 100}%` }}
            />
          </div>
          <span className="font-label-md text-secondary">₹{weekend_total.toLocaleString('en-IN')}</span>
          <span className="font-label-sm text-on-surface-variant uppercase">Weekend · {weekend_count} txns</span>
        </div>
      </div>
      {weekend_to_weekday_ratio !== null && (
        <p className="mt-lg font-body-md text-center text-on-surface-variant">
          Your weekend spend is{' '}
          <strong className="text-on-surface">
            {weekend_to_weekday_ratio < 1
              ? `${Math.round(weekend_to_weekday_ratio * 100)}% of`
              : `${weekend_to_weekday_ratio.toFixed(1)}x`}
          </strong>{' '}
          your weekday spend.
        </p>
      )}
    </Card>
  )
}