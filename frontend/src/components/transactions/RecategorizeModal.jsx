import { useState } from 'react'
import Button from '../shared/Button.jsx'
import Icon from '../shared/Icon.jsx'

const KNOWN_CATEGORIES = [
  'Food Delivery', 'Shopping', 'Transport', 'Subscription-Entertainment',
  'Subscription-Fitness', 'Subscription-Wellness', 'Utilities', 'Housing',
  'Income', 'Groceries', 'Personal Transfer', 'Entertainment', 'Health', 'Refund',
]

export default function RecategorizeModal({ transaction, onClose, onSubmit, isSubmitting }) {
  const [merchant, setMerchant] = useState(transaction.Merchant)
  const [category, setCategory] = useState(transaction.Category)
  const [isSubscription, setIsSubscription] = useState(transaction.IsSubscription)

  function handleSubmit(e) {
    e.preventDefault()
    onSubmit({ description: transaction.Description, merchant, category, isSubscription })
  }

  return (
    <div className="fixed inset-0 bg-on-surface/40 backdrop-blur-sm z-[100] flex items-center justify-center p-md">
      <div className="bg-surface-container-lowest rounded-xl p-lg max-w-md w-full shadow-xl">
        <div className="flex justify-between items-start mb-md">
          <h3 className="font-headline-md text-headline-md">Fix this transaction</h3>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface">
            <Icon name="close" />
          </button>
        </div>

        <p className="font-body-md text-on-surface-variant mb-lg truncate">
          {transaction.Description}
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-md">
          <div>
            <label className="font-label-sm text-on-surface-variant uppercase block mb-xs">Merchant</label>
            <input
              type="text"
              value={merchant}
              onChange={(e) => setMerchant(e.target.value)}
              className="w-full px-md py-sm border border-outline-variant rounded-lg font-body-md focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>

          <div>
            <label className="font-label-sm text-on-surface-variant uppercase block mb-xs">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-md py-sm border border-outline-variant rounded-lg font-body-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {KNOWN_CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <label className="flex items-center gap-sm font-body-md">
            <input
              type="checkbox"
              checked={isSubscription}
              onChange={(e) => setIsSubscription(e.target.checked)}
              className="w-4 h-4"
            />
            This is a recurring subscription
          </label>

          <div className="flex gap-sm mt-md">
            <Button type="submit" variant="primary" className="flex-1" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save correction'}
            </Button>
            <Button type="button" variant="secondary" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
          </div>

          <p className="font-label-sm text-on-surface-variant mt-xs">
            Note: this will update every transaction with a matching description, not just this one.
          </p>
        </form>
      </div>
    </div>
  )
}