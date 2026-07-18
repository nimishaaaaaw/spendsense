import Card from '../shared/Card.jsx'
import Chip from '../shared/Chip.jsx'
import Icon from '../shared/Icon.jsx'

const MERCHANT_ICONS = {
  Netflix: 'movie',
  Spotify: 'music_note',
  Hotstar: 'live_tv',
  CultFit: 'fitness_center',
  'Local Gym': 'fitness_center',
  Broadband: 'wifi',
  'MindWell App': 'self_improvement',
}

const CYCLE_LABEL = {
  monthly: 'Monthly',
  quarterly: 'Quarterly',
  annual: 'Annual',
}

export default function SubscriptionCard({ subscription }) {
  const { merchant, billing_cycle, amount, is_forgotten, confidence, occurrences } = subscription

  return (
    <Card className="flex items-center gap-lg">
      <div className="w-14 h-14 rounded-xl bg-primary-fixed/30 flex items-center justify-center flex-shrink-0">
        <Icon name={MERCHANT_ICONS[merchant] || 'loyalty'} className="text-primary text-3xl" filled />
      </div>
      <div className="flex-grow min-w-0">
        <h3 className="font-headline-md text-on-surface truncate">{merchant}</h3>
        <div className="flex items-center gap-sm mt-xs flex-wrap">
          <span className="font-label-sm text-on-surface-variant">
            {CYCLE_LABEL[billing_cycle]} · {occurrences} charges seen
          </span>
          {is_forgotten && (
            <Chip variant="warning">
              <Icon name="visibility_off" className="text-sm" /> Easy to overlook
            </Chip>
          )}
        </div>
      </div>
      <div className="text-right flex-shrink-0">
        <p className="font-headline-md text-on-surface">₹{amount.toLocaleString('en-IN')}</p>
        <p className="font-label-sm text-on-surface-variant">{confidence}% confidence</p>
      </div>
    </Card>
  )
}