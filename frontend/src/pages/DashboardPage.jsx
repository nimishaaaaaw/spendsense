import { Navigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext.jsx'
import { useInsights } from '../hooks/useInsights.js'
import MonthlySpendCard from '../components/dashboard/MonthlySpendCard.jsx'
import SpendingVelocityGauge from '../components/dashboard/SpendingVelocityGauge.jsx'
import QuickInsightCard from '../components/dashboard/QuickInsightCard.jsx'
import TopCategoriesCard from '../components/dashboard/TopCategoriesCard.jsx'
import RecentTransactionsList from '../components/dashboard/RecentTransactionsList.jsx'
import SessionExpiredPrompt from '../components/shared/SessionExpiredPrompt.jsx'

export default function DashboardPage() {
  const { sessionId, hasSession, refreshKey, transactions } = useSession()
  const { insights, isLoading, error, isSessionExpired } = useInsights(sessionId, refreshKey)

  if (!hasSession) {
    return <Navigate to="/upload" replace />
  }

  if (isSessionExpired) {
    return <SessionExpiredPrompt />
  }

  if (isLoading) {
    return <p className="font-body-md text-on-surface-variant">Loading your dashboard...</p>
  }

  if (error) {
    return <p className="font-body-md text-error">Failed to load insights: {error}</p>
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
      <MonthlySpendCard categoryTrends={insights?.category_trends} />
      <SpendingVelocityGauge velocity={insights?.velocity} />
      <QuickInsightCard topLeaks={insights?.top_leaks} />
      <TopCategoriesCard categoryTrends={insights?.category_trends} />
      <RecentTransactionsList transactions={transactions} />
    </div>
  )
}