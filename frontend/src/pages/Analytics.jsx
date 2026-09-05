import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  CartesianGrid,
} from 'recharts'
import { trends } from '../api'
import toast from 'react-hot-toast'

const COLORS = ['#ffb547', '#e5e5e8', '#9b9ba3', '#6b6b75', '#3a3a42']

export default function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    trends()
      .then((r) => setData(r.data))
      .catch(() => toast.error('Failed to load trends'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="max-w-[1400px] mx-auto px-6 py-12">
        <div className="h-8 w-48 bg-ink-800 rounded animate-pulse mb-8" />
        <div className="grid md:grid-cols-2 gap-4">
          <div className="h-80 bg-ink-800 rounded animate-pulse" />
          <div className="h-80 bg-ink-800 rounded animate-pulse" />
        </div>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-12">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-3xl font-semibold tracking-tight text-ink-100 mb-2">
          Trends
        </h1>
        <p className="text-ink-400 mb-10">
          {data.total_jobs} jobs indexed across {data.top_skills.length} skills.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ChartCard title="Top skills in demand">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={data.top_skills.slice(0, 12)} margin={{ left: 0, right: 8, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="#17171a" vertical={false} />
                <XAxis
                  dataKey="skill"
                  stroke="#6b6b75"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  angle={-30}
                  textAnchor="end"
                  height={60}
                />
                <YAxis stroke="#6b6b75" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: '#17171a',
                    border: '1px solid #2c2c32',
                    borderRadius: 6,
                    fontSize: 12,
                  }}
                  cursor={{ fill: '#1f1f24' }}
                />
                <Bar dataKey="count" fill="#ffb547" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Seniority breakdown">
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={data.seniority_breakdown}
                  dataKey="count"
                  nameKey="level"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  stroke="#0a0a0a"
                  strokeWidth={2}
                  label={(d) => `${d.level} (${d.count})`}
                >
                  {data.seniority_breakdown.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: '#17171a',
                    border: '1px solid #2c2c32',
                    borderRadius: 6,
                    fontSize: 12,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Posting volume (last 30 days)">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data.posting_volume}>
                <CartesianGrid stroke="#17171a" vertical={false} />
                <XAxis
                  dataKey="date"
                  stroke="#6b6b75"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis stroke="#6b6b75" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: '#17171a',
                    border: '1px solid #2c2c32',
                    borderRadius: 6,
                    fontSize: 12,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#ffb547"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Top locations">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={data.top_locations}
                layout="vertical"
                margin={{ left: 60, right: 8, top: 8, bottom: 8 }}
              >
                <CartesianGrid stroke="#17171a" horizontal={false} />
                <XAxis type="number" stroke="#6b6b75" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis
                  type="category"
                  dataKey="location"
                  stroke="#9b9ba3"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  width={120}
                />
                <Tooltip
                  contentStyle={{
                    background: '#17171a',
                    border: '1px solid #2c2c32',
                    borderRadius: 6,
                    fontSize: 12,
                  }}
                  cursor={{ fill: '#1f1f24' }}
                />
                <Bar dataKey="count" fill="#e5e5e8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      </motion.div>
    </div>
  )
}

function ChartCard({ title, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.5 }}
      className="p-6 rounded-xl border border-ink-800 bg-ink-900/40"
    >
      <p className="text-xs font-mono uppercase tracking-wider text-ink-400 mb-4">
        {title}
      </p>
      {children}
    </motion.div>
  )
}