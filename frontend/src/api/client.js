/**
 * Thin fetch wrapper around the FastAPI backend.
 *
 * Every function here maps 1:1 to a route we already built and manually
 * verified in backend/app/api/routes/. No endpoints are invented -- if
 * something's missing here, it's because we haven't built it on the
 * backend yet, not because it was forgotten.
 */

const BASE_URL = `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/api`
class ApiError extends Error {
  constructor(message, status, detail) {
    super(message)
    this.status = status
    this.detail = detail
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    let detail = 'Unknown error'
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch {
      // response body wasn't JSON -- fall back to status text
      detail = response.statusText
    }
    throw new ApiError(`Request failed: ${detail}`, response.status, detail)
  }
  return response.json()
}

/**
 * POST /api/upload -- uploads a CSV file, returns { session_id,
 * transaction_count, date_range_start, date_range_end, unmatched_count,
 * transactions }.
 */
export async function uploadStatement(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  })
  return handleResponse(response)
}

/**
 * POST /api/transactions/recategorize -- corrects a merchant/category for
 * a transaction (by raw description). Returns { updated_count, transactions }.
 */
export async function recategorizeTransaction(sessionId, description, merchant, category, isSubscription = false) {
  const response = await fetch(`${BASE_URL}/transactions/recategorize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      description,
      merchant,
      category,
      is_subscription: isSubscription,
    }),
  })
  return handleResponse(response)
}

/**
 * GET /api/subscriptions/{session_id} -- returns { subscriptions, bleed }.
 */
export async function getSubscriptions(sessionId) {
  const response = await fetch(`${BASE_URL}/subscriptions/${sessionId}`)
  return handleResponse(response)
}

/**
 * GET /api/insights/{session_id} -- returns { weekday_vs_weekend,
 * category_trends, top_leaks, velocity, subscription_bleed }.
 */
export async function getInsights(sessionId) {
  const response = await fetch(`${BASE_URL}/insights/${sessionId}`)
  return handleResponse(response)
}

/**
 * GET /api/health -- liveness check.
 */
export async function checkHealth() {
  const response = await fetch(`${BASE_URL}/health`)
  return handleResponse(response)
}

/**
 * POST /api/upload/sample -- loads the bundled sample dataset through the
 * real pipeline, same response shape as uploadStatement. Lets a user
 * explore the app without needing their own CSV on hand.
 */
export async function uploadSampleData() {
  const response = await fetch(`${BASE_URL}/upload/sample`, {
    method: 'POST',
  })
  return handleResponse(response)
}

export { ApiError }