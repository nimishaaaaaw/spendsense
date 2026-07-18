import { BarChart, Bar, XAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts'
import Card from '../shared/Card.jsx'
import Chip from '../shared/Chip.jsx'
import Icon from '../shared/Icon.jsx'

function aggregateByMonth(categoryTrends) {
  if (!categoryTrends || categoryTrends.length === 0) return []

  const totals = {}
  for (const row of categoryTrends) {
    if (row.category === 'Income') continue // spend chart, not cashflow chart
    totals[row.month] = (totals[row.month] || 0) + row.total
  }

  return Object.entries(totals)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, total]) => ({
      month: month.slice(5), // "2026-03" -> "03"
      total: Math.round(total),
    }))
}

export default function MonthlySpendCard({ categoryTrends }) {
  const monthlyData = aggregateByMonth(categoryTrends)
  const currentMonth = monthlyData[monthlyData.length - 1]
  const prevMonth = monthlyData[monthlyData.length - 2]

  const pctChange = prevMonth && prevMonth.total > 0
    ? Math.round(((currentMonth.total - prevMonth.total) / prevMonth.total) * 100)
    : null

  return (
    <Card className="md:col-span-2">
      <div className="flex justify-between items-start mb-md">
        <div>
          <p className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider mb-xs">
            This Month's Spending
          </p>
          <p className="font-display text-headline-lg text-on-surface">
            ₹{currentMonth?.total.toLocaleString('en-IN') ?? '0'}
          </p>
        </div>
        {pctChange !== null && (
          <Chip variant={pctChange <= 0 ? 'success' : 'danger'}>
            <Icon name={pctChange <= 0 ? 'trending_down' : 'trending_up'} className="text-sm" />
            {pctChange > 0 ? '+' : ''}{pctChange}% vs last month
          </Chip>
        )}
      </div>

      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={monthlyData}>
            <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#464554' }} axisLine={false} tickLine={false} />
            <Tooltip
              formatter={(value) => [`₹${value.toLocaleString('en-IN')}`, 'Spend']}
              contentStyle={{ borderRadius: '0.75rem', border: '1px solid #c6c5d7' }}
            />
            <Bar dataKey="total" radius={[8, 8, 0, 0]}>
              {monthlyData.map((entry, index) => (
                <Cell key={index} fill={index === monthlyData.length - 1 ? '#2c2abc' : '#e1e0ff'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}