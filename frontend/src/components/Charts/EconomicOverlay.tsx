import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  AreaChart,
  ComposedChart,
  Bar
} from 'recharts'

interface EconomicData {
  date: string
  gdpGrowth: number
  inflation: number
  interestRate: number
  unemployment: number
  bankPerformance: number
}

const mockEconomicData: EconomicData[] = [
  { date: '2020-01', gdpGrowth: 2.1, inflation: 2.3, interestRate: 1.75, unemployment: 3.5, bankPerformance: 12.5 },
  { date: '2020-04', gdpGrowth: -9.1, inflation: 0.1, interestRate: 0.25, unemployment: 14.8, bankPerformance: 11.8 },
  { date: '2020-07', gdpGrowth: 33.4, inflation: 1.4, interestRate: 0.25, unemployment: 8.4, bankPerformance: 10.2 },
  { date: '2020-10', gdpGrowth: 4.5, inflation: 1.2, interestRate: 0.25, unemployment: 6.7, bankPerformance: 9.8 },
  { date: '2021-01', gdpGrowth: 6.3, inflation: 2.6, interestRate: 0.25, unemployment: 6.0, bankPerformance: 11.2 },
  { date: '2021-04', gdpGrowth: 6.7, inflation: 4.2, interestRate: 0.25, unemployment: 5.8, bankPerformance: 12.8 },
  { date: '2021-07', gdpGrowth: 2.3, inflation: 5.4, interestRate: 0.25, unemployment: 5.2, bankPerformance: 13.5 },
  { date: '2021-10', gdpGrowth: 5.7, inflation: 6.8, interestRate: 0.25, unemployment: 4.9, bankPerformance: 14.2 },
  { date: '2022-01', gdpGrowth: -1.6, inflation: 8.5, interestRate: 0.50, unemployment: 3.6, bankPerformance: 13.8 },
  { date: '2022-04', gdpGrowth: -0.6, inflation: 9.1, interestRate: 1.75, unemployment: 3.5, bankPerformance: 12.9 },
  { date: '2022-07', gdpGrowth: 3.2, inflation: 8.3, interestRate: 3.25, unemployment: 3.5, bankPerformance: 11.5 },
  { date: '2022-10', gdpGrowth: 2.6, inflation: 7.1, interestRate: 4.50, unemployment: 3.4, bankPerformance: 10.8 },
  { date: '2023-01', gdpGrowth: 2.2, inflation: 5.0, interestRate: 5.25, unemployment: 3.4, bankPerformance: 11.9 },
  { date: '2023-04', gdpGrowth: 2.1, inflation: 3.0, interestRate: 5.50, unemployment: 3.4, bankPerformance: 12.6 },
  { date: '2023-07', gdpGrowth: 2.4, inflation: 3.2, interestRate: 5.50, unemployment: 3.4, bankPerformance: 13.2 },
  { date: '2023-10', gdpGrowth: 2.8, inflation: 3.1, interestRate: 5.50, unemployment: 3.3, bankPerformance: 13.8 }
]

export default function EconomicOverlay() {
  const [selectedView, setSelectedView] = useState<'correlation' | 'trends' | 'impact'>('correlation')

  const views = [
    { key: 'correlation', label: 'Correlation', description: 'Bank performance vs economic indicators' },
    { key: 'trends', label: 'Trends', description: 'Economic indicator trends over time' },
    { key: 'impact', label: 'Impact', description: 'Interest rate impact on banking' }
  ]

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white border border-neutral-200 rounded-lg shadow-lg p-3"
        >
          <p className="font-medium">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </motion.div>
      )
    }
    return null
  }

  const renderChart = () => {
    switch (selectedView) {
      case 'correlation':
        return (
          <ResponsiveContainer width="100%" height={250}>
            <ComposedChart data={mockEconomicData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
                stroke="#6b7280"
              />
              <YAxis yAxisId="left" stroke="#3b82f6" />
              <YAxis yAxisId="right" orientation="right" stroke="#ef4444" />
              <Tooltip content={<CustomTooltip />} />
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="bankPerformance" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                name="Bank ROE (%)"
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="interestRate" 
                stroke="#ef4444" 
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: '#ef4444', strokeWidth: 2, r: 3 }}
                name="Interest Rate (%)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        )

      case 'trends':
        return (
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={mockEconomicData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
                stroke="#6b7280"
              />
              <YAxis stroke="#6b7280" />
              <Tooltip content={<CustomTooltip />} />
              <Area 
                type="monotone" 
                dataKey="gdpGrowth" 
                stackId="1"
                stroke="#10b981" 
                fill="#10b981" 
                fillOpacity={0.6}
                name="GDP Growth (%)"
              />
              <Area 
                type="monotone" 
                dataKey="inflation" 
                stackId="1"
                stroke="#f59e0b" 
                fill="#f59e0b" 
                fillOpacity={0.6}
                name="Inflation (%)"
              />
              <Area 
                type="monotone" 
                dataKey="unemployment" 
                stackId="1"
                stroke="#ef4444" 
                fill="#ef4444" 
                fillOpacity={0.6}
                name="Unemployment (%)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )

      case 'impact':
        return (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={mockEconomicData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
                stroke="#6b7280"
              />
              <YAxis stroke="#6b7280" />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="interestRate" 
                fill="#8b5cf6" 
                radius={[2, 2, 0, 0]}
                name="Interest Rate (%)"
              />
              <Line 
                type="monotone" 
                dataKey="bankPerformance" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                name="Bank ROE (%)"
              />
            </BarChart>
          </ResponsiveContainer>
        )

      default:
        return null
    }
  }

  return (
    <div className="space-y-4">
      {/* View Selector */}
      <div className="flex flex-wrap gap-2">
        {views.map((view) => (
          <button
            key={view.key}
            onClick={() => setSelectedView(view.key as any)}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedView === view.key
                ? 'bg-primary-100 text-primary-700 border border-primary-300'
                : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
            }`}
          >
            <div className="text-center">
              <div className="font-semibold">{view.label}</div>
              <div className="text-xs opacity-75">{view.description}</div>
            </div>
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="h-64">
        {renderChart()}
      </div>

      {/* Insights */}
      <div className="space-y-3">
        <h4 className="font-medium text-neutral-900">Key Insights</h4>
        <div className="grid grid-cols-1 gap-3 text-sm">
          {selectedView === 'correlation' && (
            <>
              <div className="flex items-center gap-2 text-success-600">
                <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                <span>Strong negative correlation between interest rates and bank ROE</span>
              </div>
              <div className="flex items-center gap-2 text-warning-600">
                <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
                <span>Bank performance lags interest rate changes by 2-3 quarters</span>
              </div>
            </>
          )}
          {selectedView === 'trends' && (
            <>
              <div className="flex items-center gap-2 text-danger-600">
                <div className="w-2 h-2 bg-danger-500 rounded-full"></div>
                <span>Inflation peaked in 2022 and has been declining since</span>
              </div>
              <div className="flex items-center gap-2 text-success-600">
                <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                <span>GDP growth stabilized after COVID recovery period</span>
              </div>
            </>
          )}
          {selectedView === 'impact' && (
            <>
              <div className="flex items-center gap-2 text-primary-600">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span>Rising interest rates initially boost bank margins</span>
              </div>
              <div className="flex items-center gap-2 text-warning-600">
                <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
                <span>Higher rates may pressure loan demand and asset quality</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}