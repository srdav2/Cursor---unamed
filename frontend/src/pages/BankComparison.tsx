import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useDashboard } from '../contexts/DashboardContext'
import { 
  BanknotesIcon, 
  ScaleIcon, 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  MinusIcon
} from '@heroicons/react/24/outline'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

interface BankData {
  id: string
  name: string
  country: string
  region: string
  metrics: {
    roe: number
    roa: number
    nim: number
    efficiency: number
    capitalAdequacy: number
    assetQuality: number
  }
  performance: Array<{
    date: string
    roe: number
    roa: number
    nim: number
    efficiency: number
  }>
}

const mockBankData: BankData[] = [
  {
    id: 'jpm',
    name: 'JPMorgan Chase',
    country: 'US',
    region: 'North America',
    metrics: {
      roe: 15.2,
      roa: 1.4,
      nim: 2.8,
      efficiency: 58.3,
      capitalAdequacy: 14.2,
      assetQuality: 0.8
    },
    performance: [
      { date: '2023-01', roe: 14.8, roa: 1.3, nim: 2.7, efficiency: 59.1 },
      { date: '2023-04', roe: 15.1, roa: 1.4, nim: 2.8, efficiency: 58.5 },
      { date: '2023-07', roe: 15.5, roa: 1.4, nim: 2.9, efficiency: 57.9 },
      { date: '2023-10', roe: 15.2, roa: 1.4, nim: 2.8, efficiency: 58.3 }
    ]
  },
  {
    id: 'bac',
    name: 'Bank of America',
    country: 'US',
    region: 'North America',
    metrics: {
      roe: 12.8,
      roa: 1.1,
      nim: 2.4,
      efficiency: 62.1,
      capitalAdequacy: 13.8,
      assetQuality: 0.9
    },
    performance: [
      { date: '2023-01', roe: 12.5, roa: 1.0, nim: 2.3, efficiency: 62.8 },
      { date: '2023-04', roe: 12.9, roa: 1.1, nim: 2.4, efficiency: 62.3 },
      { date: '2023-07', roe: 13.2, roa: 1.1, nim: 2.5, efficiency: 61.7 },
      { date: '2023-10', roe: 12.8, roa: 1.1, nim: 2.4, efficiency: 62.1 }
    ]
  },
  {
    id: 'hsbc',
    name: 'HSBC',
    country: 'UK',
    region: 'Europe',
    metrics: {
      roe: 10.5,
      roa: 0.8,
      nim: 1.9,
      efficiency: 68.4,
      capitalAdequacy: 15.1,
      assetQuality: 1.2
    },
    performance: [
      { date: '2023-01', roe: 10.2, roa: 0.8, nim: 1.8, efficiency: 69.1 },
      { date: '2023-04', roe: 10.6, roa: 0.8, nim: 1.9, efficiency: 68.7 },
      { date: '2023-07', roe: 10.8, roa: 0.8, nim: 1.9, efficiency: 68.2 },
      { date: '2023-10', roe: 10.5, roa: 0.8, nim: 1.9, efficiency: 68.4 }
    ]
  }
]

const metricConfigs = {
  roe: { label: 'ROE (%)', color: '#3b82f6', description: 'Return on Equity' },
  roa: { label: 'ROA (%)', color: '#10b981', description: 'Return on Assets' },
  nim: { label: 'NIM (%)', color: '#f59e0b', description: 'Net Interest Margin' },
  efficiency: { label: 'Efficiency (%)', color: '#ef4444', description: 'Efficiency Ratio' },
  capitalAdequacy: { label: 'Capital (%)', color: '#8b5cf6', description: 'Capital Adequacy' },
  assetQuality: { label: 'Asset Quality (%)', color: '#06b6d4', description: 'Asset Quality Ratio' }
}

export default function BankComparison() {
  const { state } = useDashboard()
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['roe', 'roa'])
  const [chartType, setChartType] = useState<'line' | 'bar' | 'radar'>('line')
  const [timeRange, setTimeRange] = useState<'1y' | '2y' | '3y'>('1y')

  const selectedBanks = mockBankData.filter(bank => 
    state.selectedBanks.includes(bank.id)
  )

  const getMetricColor = (index: number) => {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
    return colors[index % colors.length]
  }

  const getChangeIndicator = (current: number, previous: number) => {
    const change = current - previous
    if (change > 0) return { icon: ArrowTrendingUpIcon, color: 'text-success-600', bg: 'bg-success-50' }
    if (change < 0) return { icon: ArrowTrendingDownIcon, color: 'text-danger-600', bg: 'bg-danger-50' }
    return { icon: MinusIcon, color: 'text-neutral-600', bg: 'bg-neutral-50' }
  }

  const renderComparisonChart = () => {
    if (selectedBanks.length === 0) {
      return (
        <div className="text-center py-12 text-neutral-500">
          <ChartBarIcon className="h-12 w-12 mx-auto mb-4 text-neutral-300" />
          <p>Select banks to compare their performance</p>
        </div>
      )
    }

    const chartData = selectedBanks[0]?.performance.map((period, index) => {
      const dataPoint: any = { date: period.date }
      selectedBanks.forEach(bank => {
        selectedMetrics.forEach(metric => {
          dataPoint[`${bank.id}_${metric}`] = bank.performance[index]?.[metric as keyof typeof period] || 0
        })
      })
      return dataPoint
    }) || []

    if (chartType === 'line') {
      return (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
              stroke="#6b7280"
            />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              formatter={(value: any, name: string) => [
                `${value.toFixed(2)}%`, 
                `${selectedBanks.find(b => name.startsWith(b.id))?.name} - ${metricConfigs[name.split('_')[1] as keyof typeof metricConfigs]?.label}`
              ]}
            />
            <Legend />
            {selectedBanks.map((bank, bankIndex) =>
              selectedMetrics.map((metric, metricIndex) => (
                <Line
                  key={`${bank.id}_${metric}`}
                  type="monotone"
                  dataKey={`${bank.id}_${metric}`}
                  stroke={getMetricColor(metricIndex)}
                  strokeWidth={2}
                  dot={{ fill: getMetricColor(metricIndex), strokeWidth: 2, r: 4 }}
                  name={`${bank.name} - ${metricConfigs[metric as keyof typeof metricConfigs]?.label}`}
                />
              ))
            )}
          </LineChart>
        </ResponsiveContainer>
      )
    }

    if (chartType === 'bar') {
      return (
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
              stroke="#6b7280"
            />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              formatter={(value: any, name: string) => [
                `${value.toFixed(2)}%`, 
                `${selectedBanks.find(b => name.startsWith(b.id))?.name} - ${metricConfigs[name.split('_')[1] as keyof typeof metricConfigs]?.label}`
              ]}
            />
            <Legend />
            {selectedBanks.map((bank, bankIndex) =>
              selectedMetrics.map((metric, metricIndex) => (
                <Bar
                  key={`${bank.id}_${metric}`}
                  dataKey={`${bank.id}_${metric}`}
                  fill={getMetricColor(metricIndex)}
                  radius={[2, 2, 0, 0]}
                  name={`${bank.name} - ${metricConfigs[metric as keyof typeof metricConfigs]?.label}`}
                />
              ))
            )}
          </BarChart>
        </ResponsiveContainer>
      )
    }

    return null
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Bank Comparison</h1>
          <p className="text-neutral-600">Compare performance metrics across selected banks</p>
        </div>
        
        <div className="flex flex-wrap gap-3">
          {/* Chart Type Toggle */}
          <div className="flex rounded-lg bg-neutral-100 p-1">
            {[
              { key: 'line', label: 'Line', icon: ChartBarIcon },
              { key: 'bar', label: 'Bar', icon: ChartBarIcon }
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setChartType(key as 'line' | 'bar')}
                className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-all ${
                  chartType === key
                    ? 'bg-white text-primary-700 shadow-sm'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </div>

          {/* Time Range */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as '1y' | '2y' | '3y')}
            className="rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="1y">1 Year</option>
            <option value="2y">2 Years</option>
            <option value="3y">3 Years</option>
          </select>
        </div>
      </div>

      {/* Metric Selection */}
      <div className="glass-effect rounded-xl p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Select Metrics to Compare</h3>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {Object.entries(metricConfigs).map(([key, config]) => (
            <button
              key={key}
              onClick={() => {
                if (selectedMetrics.includes(key)) {
                  setSelectedMetrics(selectedMetrics.filter(m => m !== key))
                } else {
                  setSelectedMetrics([...selectedMetrics, key])
                }
              }}
              className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                selectedMetrics.includes(key)
                  ? 'bg-primary-100 text-primary-700 border-primary-300'
                  : 'bg-white text-neutral-600 border-neutral-200 hover:border-primary-300 hover:text-primary-600'
              }`}
            >
              <div className="text-center">
                <div className="font-semibold">{config.label}</div>
                <div className="text-xs opacity-75">{config.description}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Comparison Chart */}
      <div className="glass-effect rounded-xl p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Performance Comparison</h3>
        {renderComparisonChart()}
      </div>

      {/* Metrics Table */}
      <div className="glass-effect rounded-xl p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Current Metrics</h3>
        {selectedBanks.length === 0 ? (
          <div className="text-center py-8 text-neutral-500">
            <BanknotesIcon className="h-12 w-12 mx-auto mb-4 text-neutral-300" />
            <p>Select banks to view their metrics</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="text-left py-3 px-4 font-medium text-neutral-700">Bank</th>
                  {selectedMetrics.map(metric => (
                    <th key={metric} className="text-center py-3 px-4 font-medium text-neutral-700">
                      {metricConfigs[metric as keyof typeof metricConfigs]?.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {selectedBanks.map((bank, index) => (
                  <tr key={bank.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="py-3 px-4">
                      <div>
                        <div className="font-medium text-neutral-900">{bank.name}</div>
                        <div className="text-sm text-neutral-500">{bank.country} • {bank.region}</div>
                      </div>
                    </td>
                    {selectedMetrics.map(metric => {
                      const currentValue = bank.metrics[metric as keyof typeof bank.metrics]
                      const previousValue = bank.performance[bank.performance.length - 2]?.[metric as keyof typeof bank.performance[0]] || currentValue
                      const changeIndicator = getChangeIndicator(currentValue, previousValue)
                      const Icon = changeIndicator.icon
                      
                      return (
                        <td key={metric} className="text-center py-3 px-4">
                          <div className="flex items-center justify-center gap-2">
                            <span className="font-semibold text-neutral-900">{currentValue.toFixed(1)}%</span>
                            <div className={`p-1 rounded-full ${changeIndicator.bg}`}>
                              <Icon className={`h-3 w-3 ${changeIndicator.color}`} />
                            </div>
                          </div>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      {selectedBanks.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {selectedMetrics.map((metric, index) => {
            const values = selectedBanks.map(bank => bank.metrics[metric as keyof typeof bank.metrics])
            const avg = values.reduce((a, b) => a + b, 0) / values.length
            const min = Math.min(...values)
            const max = Math.max(...values)
            const range = max - min
            
            return (
              <motion.div
                key={metric}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-effect rounded-xl p-4"
              >
                <h4 className="text-sm font-medium text-neutral-600 mb-2">
                  {metricConfigs[metric as keyof typeof metricConfigs]?.label}
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Average:</span>
                    <span className="font-semibold text-neutral-900">{avg.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Range:</span>
                    <span className="font-semibold text-neutral-900">{range.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Best:</span>
                    <span className="font-semibold text-success-600">{max.toFixed(1)}%</span>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      )}
    </div>
  )
}