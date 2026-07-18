import Card from '../shared/Card.jsx'
import Button from '../shared/Button.jsx'
import Icon from '../shared/Icon.jsx'

export default function QuickInsightCard({ topLeaks }) {
  const topLeak = topLeaks?.[0]

  return (
    <Card accent className="flex flex-col justify-between relative overflow-hidden">
      <Icon name="lightbulb" className="absolute -right-2 -top-2 text-[100px] opacity-10" filled />
      <div className="relative z-10">
        <div className="flex items-center gap-sm mb-md">
          <Icon name="bolt" />
          <span className="font-label-sm text-label-sm uppercase tracking-widest opacity-80">Quick Insight</span>
        </div>
        {topLeak ? (
          <p className="font-headline-md text-headline-md leading-tight">
            {topLeak.category} is your biggest spending leak — ₹{topLeak.total.toLocaleString('en-IN')} across {topLeak.count} small transactions this period.
          </p>
        ) : (
          <p className="font-headline-md text-headline-md leading-tight">
            Not enough transaction data yet to identify a leak.
          </p>
        )}
      </div>
      {topLeak && (
        <Button variant="secondary" className="mt-lg self-start bg-white text-primary-container">
          Review {topLeak.category}
        </Button>
      )}
    </Card>
  )
}