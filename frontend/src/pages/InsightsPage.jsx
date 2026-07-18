import { Navigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext.jsx'
import { useInsights } from '../hooks/useInsights.js'
import WeekdayVsWeekendCard from '../components/insights/WeekdayVsWeekendCard.jsx'
import SpendingLeaksCard from '../components/insights/SpendingLeaksCard.jsx'
import CategoryTrendsChart from '../components/insights/CategoryTrendsChart.jsx'
import SessionExpiredPrompt from '../components/shared/SessionExpiredPrompt.jsx'

export default function InsightsPage() {
  const { sessionId, hasSession, refreshKey } = useSession()
  const { insights, isLoading, error, isSessionExpired } = useInsights(sessionId, refreshKey)

  if (!hasSession) {
    return <Navigate to="/upload" replace />
  }

  if (isSessionExpired) {
    return <SessionExpiredPrompt />
  }

  if (isLoading) {
    return <p className="font-body-md text-on-surface-variant">Loading insights...</p>
  }

  if (error) {
    return <p className="font-body-md text-error">Failed to load insights: {error}</p>
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
      <CategoryTrendsChart categoryTrends={insights?.category_trends} />
      <WeekdayVsWeekendCard data={insights?.weekday_vs_weekend} />
      <SpendingLeaksCard leaks={insights?.top_leaks} />
    </div>
  )
}