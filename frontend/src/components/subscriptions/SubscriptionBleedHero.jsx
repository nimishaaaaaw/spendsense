import Icon from '../shared/Icon.jsx'

export default function SubscriptionBleedHero({ bleed }) {
  return (
    <div className="rounded-xl p-lg text-on-primary relative overflow-hidden shadow-lg bg-primary">
      <Icon name="event_repeat" className="absolute -right-2 -top-2 text-[120px] opacity-10 rotate-12" filled />
      <div className="relative z-10">
        <p className="font-label-md text-label-md uppercase tracking-[0.1em] opacity-80 mb-xs">
          Subscription Bleed
        </p>
        <h1 className="font-display text-headline-lg md:text-display mb-sm">
          ₹{bleed.total_annual.toLocaleString('en-IN')}
        </h1>
        <p className="font-body-lg opacity-90">
          Estimated annual cost across {bleed.count} recurring subscriptions
          {bleed.forgotten_count > 0 && (
            <> — {bleed.forgotten_count} of them are small charges easy to lose track of.</>
          )}
        </p>
      </div>
    </div>
  )
}