import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

export default function MiniChart({ data, type = 'line' }) {
  if (!data || data.length === 0) return null

  const labels = data.map((d) => d.name)
  const values = data.map((d) => d.value)

  const chartData = {
    labels,
    datasets: [
      {
        data: values,
        borderColor: '#00d9ff',
        backgroundColor: 'rgba(0, 217, 255, 0.3)',
        borderWidth: 2,
        pointRadius: 0,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#1a1a1a',
        titleColor: '#f0f0f0',
        bodyColor: '#f0f0f0',
        borderColor: '#00d9ff',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: {
          color: '#333333',
        },
        ticks: {
          color: '#888888',
          font: {
            size: 10,
          },
        },
      },
      y: {
        grid: {
          color: '#333333',
        },
        ticks: {
          color: '#888888',
          font: {
            size: 10,
          },
        },
      },
    },
  }

  return (
    <div className="w-full h-32 mt-4 relative">
      {type === 'line' ? (
        <Line data={chartData} options={options} />
      ) : (
        <Bar data={chartData} options={options} />
      )}
    </div>
  )
}
