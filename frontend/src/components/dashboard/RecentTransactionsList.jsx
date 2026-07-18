import { Link } from 'react-router-dom'
import Card from '../shared/Card.jsx'
import Icon from '../shared/Icon.jsx'

const CATEGORY_ICONS = {
  'Food Delivery': 'restaurant',
  Transport: 'directions_car',
  Shopping: 'shopping_bag',
  Groceries: 'local_grocery_store',
  Entertainment: 'movie',
  Income: 'payments',
  'Personal Transfer': 'sync_alt',
}

export default function RecentTransactionsList({ transactions }) {
  const recent = [...transactions]
    .sort((a, b) => new Date(b.Date) - new Date(a.Date))
    .slice(0, 6)

  return (
    <Card className="md:col-span-2">
      <div className="flex justify-between items-center mb-md">
        <h2 className="font-headline-md text-headline-md text-on-surface">Recent Transactions</h2>
        <Link
          to="/transactions"
          className="flex items-center gap-xs font-label-md text-primary hover:underline"
        >
          View All <Icon name="arrow_forward" className="text-sm" />
        </Link>
      </div>
      <div className="flex flex-col gap-sm">
        {recent.map((txn, i) => (
          <div
            key={i}
            className="flex items-center justify-between p-md bg-surface-container-lowest border border-outline-variant rounded-lg"
          >
            <div className="flex items-center gap-md min-w-0">
              <div className="w-10 h-10 bg-primary-fixed/30 rounded-lg flex items-center justify-center flex-shrink-0">
                <Icon name={CATEGORY_ICONS[txn.Category] || 'receipt_long'} className="text-primary" />
              </div>
              <div className="min-w-0">
                <p className="font-label-md text-on-surface truncate">{txn.Merchant}</p>
                <p className="font-body-md text-on-surface-variant text-sm">{txn.Date}</p>
              </div>
            </div>
            <p className={`font-headline-md flex-shrink-0 ${txn.Type === 'CREDIT' ? 'text-secondary' : 'text-error'}`}>
              {txn.Type === 'CREDIT' ? '+' : '-'}₹{txn.Amount.toLocaleString('en-IN')}
            </p>
          </div>
        ))}
      </div>
    </Card>
  )
}