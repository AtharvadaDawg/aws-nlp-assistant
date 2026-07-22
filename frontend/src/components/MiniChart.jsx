import React from 'react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'

export default function MiniChart({ data, type = 'line' }) {
  if (!data || data.length === 0) return null

  // Ensure values are numbers
  const formattedData = data.map((item) => ({
    name: item.name,
    value: Number(item.value),
  }))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div
          className="px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider"
          style={{
            backgroundColor: '#151515',
            border: '2px solid #00d9ff',
            color: '#f0f0f0',
          }}
        >
          <p className="label">{`${payload[0].name}: ${payload[0].value}`}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-32 mt-4 text-[9px] font-bold tracking-wider relative select-none">
      <ResponsiveContainer width="100%" height="100%">
        {type === 'line' ? (
          <AreaChart data={formattedData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
            <defs>
              <linearGradient id="colorCyan" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d9ff" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#00d9ff" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#222222" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#666666"
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#888888', fontSize: 9 }}
            />
            <YAxis
              stroke="#666666"
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#888888', fontSize: 9 }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#333333' }} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#00d9ff"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorCyan)"
            />
          </AreaChart>
        ) : (
          <BarChart data={formattedData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222222" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#666666"
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#888888', fontSize: 9 }}
            />
            <YAxis
              stroke="#666666"
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#888888', fontSize: 9 }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(34, 34, 34, 0.4)' }} />
            <Bar dataKey="value" fill="#00d9ff" radius={[2, 2, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}

