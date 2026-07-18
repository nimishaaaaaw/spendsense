import { useState, useEffect } from 'react'
import { getInsights, getSubscriptions, ApiError } from '../api/client'

/**
 * Fetches insights + subscriptions for the current session. Re-fetches
 * whenever sessionId changes (e.g. after a fresh upload) or refreshKey
 * changes (e.g. after a recategorization, so callers can force a refetch).
 *
 * isSessionExpired is exposed as a distinct flag (rather than making
 * callers parse the error string) since backend/session_store.py returns
 * a 404 specifically when a session has expired or never existed --
 * that's a known, expected state a page should handle gracefully (prompt
 * re-upload), unlike a genuine network failure or server error.
 */
export function useInsights(sessionId, refreshKey = 0) {
  const [insights, setInsights] = useState(null)
  const [subscriptions, setSubscriptions] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isSessionExpired, setIsSessionExpired] = useState(false)

  useEffect(() => {
    if (!sessionId) return

    let cancelled = false
    setIsLoading(true)
    setError(null)
    setIsSessionExpired(false)

    Promise.all([getInsights(sessionId), getSubscriptions(sessionId)])
      .then(([insightsResult, subsResult]) => {
        if (cancelled) return
        setInsights(insightsResult)
        setSubscriptions(subsResult)
      })
      .catch((err) => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 404) {
          setIsSessionExpired(true)
        } else {
          setError(err.detail || err.message)
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => { cancelled = true }
  }, [sessionId, refreshKey])

  return { insights, subscriptions, isLoading, error, isSessionExpired }
}