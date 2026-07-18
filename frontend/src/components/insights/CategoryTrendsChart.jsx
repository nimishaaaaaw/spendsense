import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'
import Card from '../shared/Card.jsx'

const LINE_COLORS = ['#2c2abc', '#006c49', '#8e0028', '#767586', '#4648d4', '#0c714d']

function pivotForChart(categoryTrends) {
  if (!categoryTrends || categoryTrends.length === 0) return { data: [], categories: [] }

  const categories = [...new Set(categoryTrends.map((row) => row.category))].filter((c) => c !== 'Income')
  const months = [...new Set(categoryTrends.map((row) => row.month))].sort()

  const data = months.map((month) => {
    const point = { month: month.slice(5) }
    for (const category of categories) {
      const match = categoryTrends.find((row) => row.month === month && row.category === category)
      point[category] = match ? match.total : 0
    }
    return point
  })

  return { data, categories }
}

export default function CategoryTrendsChart({ categoryTrends }) {
  const { data, categories } = pivotForChart(categoryTrends)

  // Limit to top 5 categories by final-month total, so the chart doesn't
  // become an unreadable tangle of 13 overlapping lines for every category.
  const topCategories = [...categories]
    .sort((a, b) => (data[data.length - 1]?.[b] || 0) - (data[data.length - 1]?.[a] || 0))
    .slice(0, 5)

  return (
    <Card className="md:col-span-2">
      <h2 className="font-headline-md text-headline-md mb-lg">Category Trends</h2>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e2de" />
            <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#464554' }} />
            <YAxis tick={{ fontSize: 12, fill: '#464554' }} />
            <Tooltip formatter={(value) => `₹${value.toLocaleString('en-IN')}`} />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            {topCategories.map((category, i) => (
              <Line
                key={category}
                type="monotone"
                dataKey={category}
                stroke={LINE_COLORS[i % LINE_COLORS.length]}
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}