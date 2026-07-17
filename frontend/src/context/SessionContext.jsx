import { createContext, useContext, useState, useCallback } from 'react'
import { uploadStatement as apiUploadStatement, recategorizeTransaction as apiRecategorize } from '../api/client'

const SessionContext = createContext(null)

export function SessionProvider({ children }) {
  const [sessionId, setSessionId] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [uploadMeta, setUploadMeta] = useState(null) // { transaction_count, date_range_start, date_range_end, unmatched_count }
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const uploadStatement = useCallback(async (file) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await apiUploadStatement(file)
      setSessionId(result.session_id)
      setTransactions(result.transactions)
      setUploadMeta({
        transaction_count: result.transaction_count,
        date_range_start: result.date_range_start,
        date_range_end: result.date_range_end,
        unmatched_count: result.unmatched_count,
      })
      return result
    } catch (err) {
      setError(err.detail || err.message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const recategorize = useCallback(async (description, merchant, category, isSubscription = false) => {
    if (!sessionId) {
      throw new Error('No active session -- upload a statement first.')
    }
    setIsLoading(true)
    setError(null)
    try {
      const result = await apiRecategorize(sessionId, description, merchant, category, isSubscription)
      setTransactions(result.transactions)
      return result
    } catch (err) {
      setError(err.detail || err.message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [sessionId])

  const clearSession = useCallback(() => {
    setSessionId(null)
    setTransactions([])
    setUploadMeta(null)
    setError(null)
  }, [])

  const value = {
    sessionId,
    transactions,
    uploadMeta,
    isLoading,
    error,
    uploadStatement,
    recategorize,
    clearSession,
    hasSession: sessionId !== null,
  }

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  )
}

/**
 * Hook to access session state/actions. Throws if used outside
 * SessionProvider -- fail loudly rather than silently return undefined,
 * which would produce confusing "cannot read property of undefined"
 * errors deep in a component instead of a clear message here.
 */
export function useSession() {
  const context = useContext(SessionContext)
  if (context === null) {
    throw new Error('useSession must be used within a SessionProvider')
  }
  return context
}