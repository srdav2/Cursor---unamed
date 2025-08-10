import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useDashboard } from '../contexts/DashboardContext'
import { 
  ChartBarIcon, 
  GlobeAltIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, AreaChart, Area, ComposedChart, Bar, ScatterChart, Scatter, PieChart, Pie, Cell } from 'recharts'

interface EconomicIndicator {
  date: string
  gdpGrowth: number
  inflation: number
  interestRate: number
  unemployment: number
  consumerConfidence: number
  housingStarts: number
  retailSales: number
  manufacturingPMI: number
  bankLending: number
  creditSpreads: number
}

interface CountryData {
  country: string
  region: string
  gdpGrowth: number
  inflation: number
  interestRate: number
  unemployment: number
  bankPerformance: number
  riskScore: number
}

const mockEconomicData: EconomicIndicator[] = [
  { date: '2020-01', gdpGrowth: 2.1, inflation: 2.3, interestRate: 1.75, unemployment: 3.5, consumerConfidence: 101.4, housingStarts: 1.56, retailSales: 2.8, manufacturingPMI: 50.9, bankLending: 4.2, creditSpreads: 1.2 },
  { date: '2020-04', gdpGrowth: -9.1, inflation: 0.1, interestRate: 0.25, unemployment: 14.8, consumerConfidence: 85.7, housingStarts: 0.93, retailSales: -14.7, manufacturingPMI: 41.5, bankLending: 2.1, creditSpreads: 3.8 },
  { date: '2020-07', gdpGrowth: 33.4, inflation: 1.4, interestRate: 0.25, unemployment: 8.4, consumerConfidence: 101.4, housingStarts: 1.48, retailSales: 6.2, manufacturingPMI: 54.2, bankLending: 3.8, creditSpreads: 2.1 },
  { date: '2020-10', gdpGrowth: 4.5, inflation: 1.2, interestRate: 0.25, unemployment: 6.7, consumerConfidence: 96.1, housingStarts: 1.63, retailSales: 1.4, manufacturingPMI: 58.8, bankLending: 4.5, creditSpreads: 1.8 },
  { date: '2021-01', gdpGrowth: 6.3, inflation: 2.6, interestRate: 0.25, unemployment: 6.0, consumerConfidence: 109.7, housingStarts: 1.74, retailSales: 7.6, manufacturingPMI: 60.8, bankLending: 5.2, creditSpreads: 1.5 },
  { date: '2021-04', gdpGrowth: 6.7, inflation: 4.2, interestRate: 0.25, unemployment: 5.8, consumerConfidence: 117.5, housingStarts: 1.68, retailSales: 2.7, manufacturingPMI: 61.2, bankLending: 5.8, creditSpreads: 1.3 },
  { date: '2021-07', gdpGrowth: 2.3, inflation: 5.4, interestRate: 0.25, unemployment: 5.2, consumerConfidence: 113.8, housingStarts: 1.62, retailSales: 1.8, manufacturingPMI: 59.9, bankLending: 6.1, creditSpreads: 1.4 },
  { date: '2021-10', gdpGrowth: 5.7, inflation: 6.8, interestRate: 0.25, unemployment: 4.9, consumerConfidence: 111.9, housingStarts: 1.70, retailSales: 2.5, manufacturingPMI: 58.7, bankLending: 6.5, creditSpreads: 1.6 },
  { date: '2022-01', gdpGrowth: -1.6, inflation: 8.5, interestRate: 0.50, unemployment: 3.6, consumerConfidence: 103.4, housingStarts: 1.59, retailSales: 1.1, manufacturingPMI: 55.4, bankLending: 6.8, creditSpreads: 2.1 },
  { date: '2022-04', gdpGrowth: -0.6, inflation: 9.1, interestRate: 1.75, unemployment: 3.5, consumerConfidence: 98.4, housingStarts: 1.55, retailSales: 0.8, manufacturingPMI: 52.7, bankLending: 7.2, creditSpreads: 2.8 },
  { date: '2022-07', gdpGrowth: 3.2, inflation: 8.3, interestRate: 3.25, unemployment: 3.5, consumerConfidence: 95.3, housingStarts: 1.48, retailSales: 0.3, manufacturingPMI: 50.3, bankLending: 7.5, creditSpreads: 3.2 },
  { date: '2022-10', gdpGrowth: 2.6, inflation: 7.1, interestRate: 4.50, unemployment: 3.4, consumerConfidence: 102.5, housingStarts: 1.42, retailSales: 1.2, manufacturingPMI: 49.0, bankLending: 7.8, creditSpreads: 3.5 },
  { date: '2023-01', gdpGrowth: 2.2, inflation: 5.0, interestRate: 5.25, unemployment: 3.4, consumerConfidence: 104.2, housingStarts: 1.38, retailSales: 2.1, manufacturingPMI: 47.1, bankLending: 8.1, creditSpreads: 3.8 },
  { date: '2023-04', gdpGrowth: 2.1, inflation: 3.0, interestRate: 5.50, unemployment: 3.4, consumerConfidence: 108.0, housingStarts: 1.35, retailSales: 3.2, manufacturingPMI: 46.0, bankLending: 8.3, creditSpreads: 4.1 },
  { date: '2023-07', gdpGrowth: 2.4, inflation: 3.2, interestRate: 5.50, unemployment: 3.4, consumerConfidence: 108.7, housingStarts: 1.32, retailSales: 3.8, manufacturingPMI: 47.6, bankLending: 8.5, creditSpreads: 4.3 },
  { date: '2023-10', gdpGrowth: 2.8, inflation: 3.1, interestRate: 5.50, unemployment: 3.3, consumerConfidence: 109.7, housingStarts: 1.30, retailSales: 4.1, manufacturingPMI: 48.2, bankLending: 8.7, creditSpreads: 4.5 }
]

const mockCountryData: CountryData[] = [
  { country: 'US', region: 'North America', gdpGrowth: 2.8, inflation: 3.1, interestRate: 5.50, unemployment: 3.3, bankPerformance: 13.8, riskScore: 0.25 },
  { country: 'UK', region: 'Europe', gdpGrowth: 1.2, inflation: 4.6, interestRate: 5.25, unemployment: 4.2, bankPerformance: 10.5, riskScore: 0.45 },
  { country: 'Germany', region: 'Europe', gdpGrowth: -0.3, inflation: 3.2, interestRate: 4.50, unemployment: 3.1, bankPerformance: 8.9, riskScore: 0.38 },
  { country: 'Japan', region: 'Asia-Pacific', gdpGrowth: 1.9, inflation: 2.8, interestRate: -0.10, unemployment: 2.6, bankPerformance: 6.2, riskScore: 0.52 },
  { country: 'China', region: 'Asia-Pacific', gdpGrowth: 5.2, inflation: 2.1, interestRate: 3.85, unemployment: 5.1, bankPerformance: 12.1, riskScore: 0.31 },
  { country: 'Canada', region: 'North America', gdpGrowth: 1.1, inflation: 3.8, interestRate: 5.00, unemployment: 5.5, bankPerformance: 11.8, riskScore: 0.42 }
]

export default function EconomicAnalysis() {
  const { state } = useDashboard()
  const [selectedView, setSelectedView] = useState<'overview' | 'correlation' | 'regional' | 'forecast'>('overview')
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>(['gdpGrowth', 'inflation', 'interestRate'])
  const [timeRange, setTimeRange] = useState<'1y' | '2y' | '3y'>('3y')

  const views = [
    { key: 'overview', label: 'Overview', description: 'Economic indicators overview' },
    { key: 'correlation', label: 'Correlation', description: 'Bank performance correlations' },
    { key: 'regional', label: 'Regional', description: 'Regional economic analysis' },
    { key: 'forecast', label: 'Forecast', description: 'Economic outlook' }
  ]

  const indicators = [
    { key: 'gdpGrowth', label: 'GDP Growth', color: '#10b981' },
    { key: 'inflation', label: 'Inflation', color: '#f59e0b' },
    { key: 'interestRate', label: 'Interest Rate', color: '#ef4444' },
    { key: 'unemployment', label: 'Unemployment', color: '#8b5cf6' },
    { key: 'consumerConfidence', label: 'Consumer Confidence', color: '#06b6d4' },
    { key: 'housingStarts', label: 'Housing Starts', color: '#84cc16' }
  ]

  const getRiskColor = (score: number) => {
    if (score < 0.3) return 'text-success-600 bg-success-50'
    if (score < 0.5) return 'text-warning-600 bg-warning-50'
    return 'text-danger-600 bg-danger-50'
  }

  const renderOverviewChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={mockEconomicData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis 
          dataKey="date" 
          tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
          stroke="#6b7280"
        />
        <YAxis yAxisId="left" stroke="#6b7280" />
        <YAxis yAxisId="right" orientation="right" stroke="#ef4444" />
        <Tooltip 
          formatter={(value: any, name: string) => [
            typeof value === 'number' ? value.toFixed(2) : value,
            indicators.find(i => i.key === name)?.label || name
          ]}
        />
        <Legend />
        {selectedIndicators.map((indicator, index) => {
          const config = indicators.find(i => i.key === indicator)
          if (!config) return null
          
          if (indicator === 'interestRate') {
            return (
              <Line
                key={indicator}
                yAxisId="right"
                type="monotone"
                dataKey={indicator}
                stroke={config.color}
                strokeWidth={3}
                strokeDasharray="5 5"
                dot={{ fill: config.color, strokeWidth: 2, r: 4 }}
                name={config.label}
              />
            )
          }
          
          return (
            <Line
              key={indicator}
              yAxisId="left"
              type="monotone"
              dataKey={indicator}
              stroke={config.color}
              strokeWidth={2}
              dot={{ fill: config.color, strokeWidth: 2, r: 3 }}
              name={config.label}
            />
          )
        })}
      </ComposedChart>
    </ResponsiveContainer>
  )

  const renderCorrelationChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <ScatterChart data={mockEconomicData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis 
          dataKey="interestRate" 
          name="Interest Rate (%)"
          stroke="#6b7280"
        />
        <YAxis 
          dataKey="bankLending" 
          name="Bank Lending Growth (%)"
          stroke="#6b7280"
        />
        <Tooltip 
          formatter={(value: any, name: string) => [
            `${value.toFixed(2)}%`,
            name
          ]}
        />
        <Scatter 
          dataKey="bankLending" 
          fill="#3b82f6" 
          name="Bank Lending vs Interest Rates"
        />
      </ScatterChart>
    </ResponsiveContainer>
  )

  const renderRegionalChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={mockCountryData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="country" stroke="#6b7280" />
        <YAxis stroke="#6b7280" />
        <Tooltip 
          formatter={(value: any, name: string) => [
            `${value.toFixed(2)}%`,
            name
          ]}
        />
        <Legend />
        <Bar dataKey="gdpGrowth" fill="#10b981" name="GDP Growth (%)" />
        <Bar dataKey="inflation" fill="#f59e0b" name="Inflation (%)" />
        <Bar dataKey="bankPerformance" fill="#3b82f6" name="Bank Performance (%)" />
      </BarChart>
    </ResponsiveContainer>
  )

  const renderForecastChart = () => {
    const forecastData = mockEconomicData.slice(-8).map((item, index) => ({
      ...item,
      forecast: item.gdpGrowth + (Math.random() - 0.5) * 2,
      confidence: 85 + Math.random() * 10
    }))
    
    return (
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={forecastData}>
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
              name
            ]}
          />
          <Legend />
          <Area 
            type="monotone" 
            dataKey="gdpGrowth" 
            stroke="#10b981" 
            fill="#10b981" 
            fillOpacity={0.6}
            name="Actual GDP Growth"
          />
          <Area 
            type="monotone" 
            dataKey="forecast" 
            stroke="#8b5cf6" 
            fill="#8b5cf6" 
            fillOpacity={0.3}
            strokeDasharray="5 5"
            name="Forecast GDP Growth"
          />
        </AreaChart>
      </ResponsiveContainer>
    )
  }

  const renderChart = () => {
    switch (selectedView) {
      case 'overview':
        return renderOverviewChart()
      case 'correlation':
        return renderCorrelationChart()
      case 'regional':
        return renderRegionalChart()
      case 'forecast':
        return renderForecastChart()
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Economic Analysis</h1>
          <p className="text-neutral-600">Analyze economic factors and their impact on banking performance</p>
        </div>
        
        <div className="flex flex-wrap gap-3">
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

      {/* View Selector */}
      <div className="glass-effect rounded-xl p-6">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {views.map((view) => (
            <button
              key={view.key}
              onClick={() => setSelectedView(view.key as any)}
              className={`p-4 rounded-lg border text-center transition-all ${
                selectedView === view.key
                  ? 'bg-primary-100 text-primary-700 border-primary-300'
                  : 'bg-white text-neutral-600 border-neutral-200 hover:border-primary-300 hover:text-primary-600'
              }`}
            >
              <div className="font-semibold">{view.label}</div>
              <div className="text-xs opacity-75">{view.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Indicator Selection */}
      {selectedView === 'overview' && (
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Select Economic Indicators</h3>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {indicators.map((indicator) => (
              <button
                key={indicator.key}
                onClick={() => {
                  if (selectedIndicators.includes(indicator.key)) {
                    setSelectedIndicators(selectedIndicators.filter(i => i !== indicator.key))
                  } else {
                    setSelectedIndicators([...selectedIndicators, indicator.key])
                  }
                }}
                className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                  selectedIndicators.includes(indicator.key)
                    ? 'bg-primary-100 text-primary-700 border-primary-300'
                    : 'bg-white text-neutral-600 border-neutral-200 hover:border-primary-300 hover:text-primary-600'
                }`}
              >
                <div className="text-center">
                  <div className="font-semibold">{indicator.label}</div>
                  <div className="w-3 h-3 rounded-full mx-auto mt-1" style={{ backgroundColor: indicator.color }}></div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Chart */}
      <div className="glass-effect rounded-xl p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">
          {selectedView === 'overview' && 'Economic Indicators Overview'}
          {selectedView === 'correlation' && 'Bank Performance Correlations'}
          {selectedView === 'regional' && 'Regional Economic Analysis'}
          {selectedView === 'forecast' && 'Economic Outlook Forecast'}
        </h3>
        {renderChart()}
      </div>

      {/* Key Insights */}
      <div className="glass-effect rounded-xl p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Key Insights</h3>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {selectedView === 'overview' && (
            <>
              <div className="space-y-3">
                <h4 className="font-medium text-neutral-900">Interest Rate Impact</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-warning-600">
                    <ArrowTrendingUpIcon className="h-4 w-4" />
                    <span>Rising rates are pressuring consumer spending and housing</span>
                  </div>
                  <div className="flex items-center gap-2 text-success-600">
                    <ArrowTrendingDownIcon className="h-4 w-4" />
                    <span>Inflation has declined significantly from 2022 peak</span>
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <h4 className="font-medium text-neutral-900">Economic Recovery</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-success-600">
                    <ArrowTrendingUpIcon className="h-4 w-4" />
                    <span>GDP growth stabilized after COVID recovery period</span>
                  </div>
                  <div className="flex items-center gap-2 text-primary-600">
                    <ArrowTrendingUpIcon className="h-4 w-4" />
                    <span>Consumer confidence improving despite rate environment</span>
                  </div>
                </div>
              </div>
            </>
          )}
          
          {selectedView === 'correlation' && (
            <>
              <div className="space-y-3">
                <h4 className="font-medium text-neutral-900">Bank Lending Trends</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-danger-600">
                    <ArrowTrendingDownIcon className="h-4 w-4" />
                    <span>Higher rates are reducing loan demand</span>
                  </div>
                  <div className="flex items-center gap-2 text-warning-600">
                    <ArrowTrendingDownIcon className="h-4 w-4" />
                    <span>Credit spreads widening in higher rate environment</span>
                  </div>
                </div>
              </div>
            </>
          )}

          {selectedView === 'regional' && (
            <>
              <div className="space-y-3">
                <h4 className="font-medium text-neutral-900">Regional Performance</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-success-600">
                    <ArrowTrendingUpIcon className="h-4 w-4" />
                    <span>North America showing strongest bank performance</span>
                  </div>
                  <div className="flex items-center gap-2 text-warning-600">
                    <ArrowTrendingDownIcon className="h-4 w-4" />
                    <span>Europe facing economic headwinds</span>
                  </div>
                </div>
              </div>
            </>
          )}

          {selectedView === 'forecast' && (
            <>
              <div className="space-y-3">
                <h4 className="font-medium text-neutral-900">Economic Outlook</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-success-600">
                    <ArrowTrendingUpIcon className="h-4 w-4" />
                    <span>Moderate growth expected in 2024</span>
                  </div>
                  <div className="flex items-center gap-2 text-warning-600">
                    <ArrowTrendingDownIcon className="h-4 w-4" />
                    <span>Rates expected to remain elevated</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Country Risk Analysis */}
      {selectedView === 'regional' && (
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Country Risk Analysis</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {mockCountryData.map((country, index) => (
              <motion.div
                key={country.country}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-lg border border-neutral-200 p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-neutral-900">{country.country}</h4>
                    <p className="text-sm text-neutral-500">{country.region}</p>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(country.riskScore)}`}>
                    Risk: {(country.riskScore * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-neutral-500">GDP Growth:</span>
                    <span className="font-medium">{country.gdpGrowth}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Inflation:</span>
                    <span className="font-medium">{country.inflation}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Bank Performance:</span>
                    <span className="font-medium">{country.bankPerformance}%</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}