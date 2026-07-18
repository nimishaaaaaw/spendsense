import Card from '../shared/Card.jsx'
import ProgressBar from '../shared/ProgressBar.jsx'
import Icon from '../shared/Icon.jsx'

const CATEGORY_ICONS = {
  'Food Delivery': 'restaurant',
  Transport: 'commute',
  Shopping: 'shopping_bag',
  Groceries: 'local_grocery_store',
  Entertainment: 'movie',
  Health: 'medical_services',
  Utilities: 'bolt',
  Housing: 'home',
  'Personal Transfer': 'sync_alt',
}

const CATEGORY_COLORS = {
  'Food Delivery': 'tertiary',
  Transport: 'primary',
  Shopping: 'secondary',
}

function getLatestMonthTotals(categoryTrends) {
  if (!categoryTrends || categoryTrends.length === 0) return []

  const latestMonth = categoryTrends.reduce((max, row) => (row.month > max ? row.month : max), categoryTrends[0].month)
  const latestRows = categoryTrends.filter((row) => row.month === latestMonth)

  return latestRows
    .filter((row) => row.category !== 'Income') // income isn't a "spend" category
    .sort((a, b) => b.total - a.total)
    .slice(0, 3)
}

export default function TopCategoriesCard({ categoryTrends }) {
  const topThree = getLatestMonthTotals(categoryTrends)
  const maxTotal = topThree[0]?.total || 1

  if (topThree.length === 0) {
    return (
      <Card>
        <h2 className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider mb-lg">Top Categories</h2>
        <p className="text-on-surface-variant font-body-md">No spending data yet for the most recent month.</p>
      </Card>
    )
  }

  return (
    <Card>
      <h2 className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider mb-lg">Top Categories</h2>
      <div className="flex flex-col gap-lg">
        {topThree.map((row) => (
          <div key={row.category} className="flex items-center gap-md">
            <div className="w-12 h-12 bg-primary-fixed/30 rounded-xl flex items-center justify-center flex-shrink-0">
              <Icon name={CATEGORY_ICONS[row.category] || 'category'} className="text-primary" filled />
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-end mb-xs">
                <span className="font-headline-md text-headline-md text-on-surface">{row.category}</span>
                <span className="font-label-md text-label-md text-on-surface">₹{row.total.toLocaleString('en-IN')}</span>
              </div>
              <ProgressBar pct={(row.total / maxTotal) * 100} color={CATEGORY_COLORS[row.category] || 'primary'} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}