import { useState } from 'react'
import { Navigate, Link, useSearchParams } from 'react-router-dom'
import { useSession } from '../context/SessionContext.jsx'
import Card from '../components/shared/Card.jsx'
import Button from '../components/shared/Button.jsx'
import Icon from '../components/shared/Icon.jsx'
import RecategorizeModal from '../components/transactions/RecategorizeModal.jsx'

const LOW_FUZZY_CONFIDENCE_THRESHOLD = 85

function getMatchIndicator(txn) {
  if (txn.Category === 'Uncategorized') {
    return { text: 'needs review', className: 'text-error' }
  }
  if (txn.MatchMethod === 'p2p_heuristic') {
    return { text: 'guessed from name', className: 'text-on-surface-variant' }
  }
  if (txn.MatchMethod === 'fuzzy' && txn.Confidence < LOW_FUZZY_CONFIDENCE_THRESHOLD) {
    return { text: `low confidence match (${Math.round(txn.Confidence)}%)`, className: 'text-tertiary' }
  }
  return null
}

export default function TransactionsPage() {
  const { hasSession, transactions, recategorize, isLoading } = useSession()
  const [editingTxn, setEditingTxn] = useState(null)
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [toast, setToast] = useState(null)

  if (!hasSession) {
    return <Navigate to="/upload" replace />
  }

  const categoryFilter = searchParams.get('category')

  const filtered = transactions.filter((txn) => {
    const matchesSearch =
      txn.Description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      txn.Merchant.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = !categoryFilter || txn.Category === categoryFilter
    return matchesSearch && matchesCategory
  })

  const sorted = [...filtered].sort((a, b) => new Date(b.Date) - new Date(a.Date))

  function clearCategoryFilter() {
    setSearchParams({})
  }

  async function handleRecategorize({ description, merchant, category, isSubscription }) {
    try {
      const result = await recategorize(description, merchant, category, isSubscription)
      setToast(`Updated ${result.updated_count} transaction${result.updated_count !== 1 ? 's' : ''}.`)
      setEditingTxn(null)
      setTimeout(() => setToast(null), 4000)
    } catch {
      // error surfaces via SessionContext's `error` state; modal stays open
      // so the user can retry rather than losing their edits.
    }
  }

  return (
    <div className="flex flex-col gap-lg">
      <Link
        to="/"
        className="flex items-center gap-xs font-label-md text-primary hover:underline w-fit"
      >
        <Icon name="arrow_back" className="text-lg" /> Dashboard
      </Link>

      <div>
        <h1 className="font-headline-lg text-headline-lg mb-xs">All Transactions</h1>
        <p className="text-on-surface-variant font-body-lg">{transactions.length} total. Click any row to correct it.</p>
      </div>

      {categoryFilter && (
        <div className="flex items-center gap-sm bg-primary-fixed/30 border border-primary/20 rounded-xl px-md py-sm w-fit">
          <span className="font-label-md text-on-surface">Filtered to: <strong>{categoryFilter}</strong></span>
          <button onClick={clearCategoryFilter} className="text-primary hover:underline flex items-center">
            <Icon name="close" className="text-sm" />
          </button>
        </div>
      )}

      <div className="relative max-w-md">
        <Icon name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by merchant or description..."
          className="w-full pl-10 pr-md py-sm border border-outline-variant rounded-xl bg-surface-container-lowest focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {toast && (
        <div className="bg-secondary-container text-on-secondary-container px-md py-sm rounded-lg font-label-md">
          {toast}
        </div>
      )}

      <Card className="p-0 overflow-hidden">
        {sorted.length === 0 ? (
          <p className="p-lg text-on-surface-variant font-body-md">No transactions match this filter.</p>
        ) : (
          <div className="flex flex-col divide-y divide-outline-variant">
            {sorted.map((txn, i) => {
              const indicator = getMatchIndicator(txn)
              return (
                <button
                  key={i}
                  onClick={() => setEditingTxn(txn)}
                  className="flex items-center justify-between p-md hover:bg-surface-container-low transition-colors text-left"
                >
                  <div className="min-w-0 flex-1">
                    <p className="font-label-md text-on-surface truncate">{txn.Merchant}</p>
                    <p className="font-body-md text-on-surface-variant text-sm truncate">{txn.Description}</p>
                    <p className="font-label-sm text-on-surface-variant mt-1">{txn.Date} · {txn.Category}</p>
                  </div>
                  <div className="text-right flex-shrink-0 ml-md">
                    <p className={`font-headline-md ${txn.Type === 'CREDIT' ? 'text-secondary' : 'text-error'}`}>
                      {txn.Type === 'CREDIT' ? '+' : '-'}₹{txn.Amount.toLocaleString('en-IN')}
                    </p>
                    {indicator && (
                      <p className={`font-label-sm ${indicator.className}`}>{indicator.text}</p>
                    )}
                  </div>
                </button>
              )
            })}
          </div>
        )}
      </Card>

      {editingTxn && (
        <RecategorizeModal
          transaction={editingTxn}
          onClose={() => setEditingTxn(null)}
          onSubmit={handleRecategorize}
          isSubmitting={isLoading}
        />
      )}
    </div>
  )
}