import { Navigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext.jsx'
import { useInsights } from '../hooks/useInsights.js'
import SubscriptionBleedHero from '../components/subscriptions/SubscriptionBleedHero.jsx'
import SubscriptionCard from '../components/subscriptions/SubscriptionCard.jsx'
import Card from '../components/shared/Card.jsx'
import SessionExpiredPrompt from '../components/shared/SessionExpiredPrompt.jsx'

export default function SubscriptionsPage() {
  const { sessionId, hasSession, refreshKey } = useSession()
  const { subscriptions, isLoading, error, isSessionExpired } = useInsights(sessionId, refreshKey)

  if (!hasSession) {
    return <Navigate to="/upload" replace />
  }

  if (isSessionExpired) {
    return <SessionExpiredPrompt />
  }

  if (isLoading) {
    return <p className="font-body-md text-on-surface-variant">Loading subscriptions...</p>
  }

  if (error) {
    return <p className="font-body-md text-error">Failed to load subscriptions: {error}</p>
  }

  const subList = subscriptions?.subscriptions || []
  const bleed = subscriptions?.bleed

  return (
    <div className="flex flex-col gap-lg max-w-3xl">
      {bleed && <SubscriptionBleedHero bleed={bleed} />}

      <div>
        <div className="flex justify-between items-center mb-md">
          <h2 className="font-headline-md text-headline-md text-on-surface">Active Subscriptions</h2>
          <span className="font-label-sm text-on-surface-variant">{subList.length} detected</span>
        </div>

        {subList.length === 0 ? (
          <Card>
            <p className="text-on-surface-variant font-body-md">No recurring subscriptions detected yet.</p>
          </Card>
        ) : (
          <div className="flex flex-col gap-md">
            {subList.map((sub) => (
              <SubscriptionCard key={sub.merchant} subscription={sub} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}