import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useDashboard } from '../contexts/DashboardContext'
import {
  ChartBarIcon,
  ScaleIcon,
  TrophyIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  StarIcon,
  BanknotesIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, ScatterChart, Scatter, Cell, ComposedChart, Area, PieChart, Pie } from 'recharts'

interface BenchmarkData {
  id: string
  name: string
  category: 'Tier 1' | 'Tier 2' | 'Regional' | 'Specialized'
  assets: number
  marketCap: number
  metrics: {
    roe: number
    roa: number
    nim: number
    efficiency: number
    capitalAdequacy: number
    assetQuality: number
    liquidity: number
    profitability: number
    riskScore: number
  }
  performance: Array<{
    date: string
    roe: number
    roa: number
    nim: number
    efficiency: number
    marketCap: number
  }>
  peerGroup: string
  industryRank: number
  percentile: number
}

interface IndustryBenchmark {
  metric: string
  tier1: number
  tier2: number
  regional: number
  specialized: number
  industry: number
}

const mockBenchmarkData: BenchmarkData[] = [
  {
    id: 'jpm',
    name: 'JPMorgan Chase',
    category: 'Tier 1',
    assets: 3874.2,
    marketCap: 485.6,
    metrics: {
      roe: 15.2,
      roa: 1.4,
      nim: 2.8,
      efficiency: 58.3,
      capitalAdequacy: 14.2,
      assetQuality: 0.8,
      liquidity: 85.4,
      profitability: 92.1,
      riskScore: 8.7
    },
    performance: [
      { date: '2023-01', roe: 14.8, roa: 1.3, nim: 2.7, efficiency: 59.1, marketCap: 420.1 },
      { date: '2023-04', roe: 15.1, roa: 1.4, nim: 2.8, efficiency: 58.5, marketCap: 445.2 },
      { date: '2023-07', roe: 15.5, roa: 1.4, nim: 2.9, efficiency: 57.9, marketCap: 465.8 },
      { date: '2023-10', roe: 15.2, roa: 1.4, nim: 2.8, efficiency: 58.3, marketCap: 485.6 }
    ],
    peerGroup: 'Global Systemically Important Banks',
    industryRank: 1,
    percentile: 95
  },
  {
    id: 'bac',
    name: 'Bank of America',
    category: 'Tier 1',
    assets: 3180.1,
    marketCap: 245.8,
    metrics: {
      roe: 12.8,
      roa: 1.1,
      nim: 2.4,
      efficiency: 62.1,
      capitalAdequacy: 13.8,
      assetQuality: 0.9,
      liquidity: 82.7,
      profitability: 88.9,
      riskScore: 8.2
    },
    performance: [
      { date: '2023-01', roe: 12.5, roa: 1.0, nim: 2.3, efficiency: 62.8, marketCap: 210.3 },
      { date: '2023-04', roe: 12.9, roa: 1.1, nim: 2.4, efficiency: 62.3, marketCap: 225.7 },
      { date: '2023-07', roe: 13.2, roa: 1.1, nim: 2.5, efficiency: 61.7, marketCap: 235.4 },
      { date: '2023-10', roe: 12.8, roa: 1.1, nim: 2.4, efficiency: 62.1, marketCap: 245.8 }
    ],
    peerGroup: 'Global Systemically Important Banks',
    industryRank: 2,
    percentile: 88
  },
  {
    id: 'wells',
    name: 'Wells Fargo',
    category: 'Tier 1',
    assets: 1883.5,
    marketCap: 156.2,
    metrics: {
      roe: 11.9,
      roa: 1.0,
      nim: 2.9,
      efficiency: 65.8,
      capitalAdequacy: 14.5,
      assetQuality: 1.1,
      liquidity: 79.3,
      profitability: 85.6,
      riskScore: 7.8
    },
    performance: [
      { date: '2023-01', roe: 11.5, roa: 0.9, nim: 2.8, efficiency: 66.2, marketCap: 135.8 },
      { date: '2023-04', roe: 11.8, roa: 1.0, nim: 2.9, efficiency: 65.9, marketCap: 142.3 },
      { date: '2023-07', roe: 12.1, roa: 1.0, nim: 3.0, efficiency: 65.5, marketCap: 149.7 },
      { date: '2023-10', roe: 11.9, roa: 1.0, nim: 2.9, efficiency: 65.8, marketCap: 156.2 }
    ],
    peerGroup: 'Global Systemically Important Banks',
    industryRank: 3,
    percentile: 82
  },
  {
    id: 'citi',
    name: 'Citigroup',
    category: 'Tier 1',
    assets: 2418.0,
    marketCap: 89.4,
    metrics: {
      roe: 9.8,
      roa: 0.8,
      nim: 2.1,
      efficiency: 68.2,
      capitalAdequacy: 13.1,
      assetQuality: 1.3,
      liquidity: 76.8,
      profitability: 78.4,
      riskScore: 7.2
    },
    performance: [
      { date: '2023-01', roe: 9.2, roa: 0.7, nim: 2.0, efficiency: 69.1, marketCap: 78.5 },
      { date: '2023-04', roe: 9.5, roa: 0.8, nim: 2.1, efficiency: 68.7, marketCap: 82.3 },
      { date: '2023-07', roe: 9.8, roa: 0.8, nim: 2.1, efficiency: 68.4, marketCap: 85.9 },
      { date: '2023-10', roe: 9.8, roa: 0.8, nim: 2.1, efficiency: 68.2, marketCap: 89.4 }
    ],
    peerGroup: 'Global Systemically Important Banks',
    industryRank: 4,
    percentile: 75
  },
  {
    id: 'usb',
    name: 'U.S. Bancorp',
    category: 'Tier 2',
    assets: 651.2,
    marketCap: 58.7,
    metrics: {
      roe: 13.2,
      roa: 1.2,
      nim: 3.1,
      efficiency: 61.5,
      capitalAdequacy: 14.8,
      assetQuality: 0.7,
      liquidity: 83.2,
      profitability: 89.3,
      riskScore: 8.5
    },
    performance: [
      { date: '2023-01', roe: 12.8, roa: 1.1, nim: 3.0, efficiency: 62.1, marketCap: 52.4 },
      { date: '2023-04', roe: 13.0, roa: 1.2, nim: 3.1, efficiency: 61.8, marketCap: 55.2 },
      { date: '2023-07', roe: 13.3, roa: 1.2, nim: 3.2, efficiency: 61.6, marketCap: 57.1 },
      { date: '2023-10', roe: 13.2, roa: 1.2, nim: 3.1, efficiency: 61.5, marketCap: 58.7 }
    ],
    peerGroup: 'Super Regional Banks',
    industryRank: 5,
    percentile: 78
  }
]

const industryBenchmarks: IndustryBenchmark[] = [
  { metric: 'ROE (%)', tier1: 12.5, tier2: 11.8, regional: 10.2, specialized: 9.5, industry: 11.2 },
  { metric: 'ROA (%)', tier1: 1.2, tier2: 1.1, regional: 0.9, specialized: 0.8, industry: 1.0 },
  { metric: 'NIM (%)', tier1: 2.6, tier2: 2.9, regional: 3.2, specialized: 3.5, industry: 2.8 },
  { metric: 'Efficiency (%)', tier1: 61.5, tier2: 63.2, regional: 65.8, specialized: 68.4, industry: 64.7 },
  { metric: 'Capital (%)', tier1: 13.8, tier2: 14.2, regional: 14.8, specialized: 15.2, industry: 14.5 },
  { metric: 'Asset Quality (%)', tier1: 0.9, tier2: 0.7, regional: 0.6, specialized: 0.5, industry: 0.7 }
]

const peerGroups = ['All Banks', 'Tier 1', 'Tier 2', 'Regional', 'Specialized', 'Global Systemically Important Banks', 'Super Regional Banks']

export default function Benchmarking() {
  const { state } = useDashboard()
  const [selectedBanks, setSelectedBanks] = useState<string[]>(['jpm', 'bac'])
  const [selectedPeerGroup, setSelectedPeerGroup] = useState('All Banks')
  const [selectedView, setSelectedView] = useState<'performance' | 'benchmarks' | 'ranking' | 'analysis'>('performance')
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['roe', 'roa', 'nim'])

  const views = [
    { key: 'performance', label: 'Performance', description: 'Performance comparison' },
    { key: 'benchmarks', label: 'Benchmarks', description: 'Industry benchmarks' },
    { key: 'ranking', label: 'Ranking', description: 'Performance ranking' },
    { key: 'analysis', label: 'Analysis', description: 'Deep dive analysis' }
  ]

  const metrics = [
    { key: 'roe', label: 'ROE (%)', color: '#3b82f6' },
    { key: 'roa', label: 'ROA (%)', color: '#10b981' },
    { key: 'nim', label: 'NIM (%)', color: '#f59e0b' },
    { key: 'efficiency', label: 'Efficiency (%)', color: '#ef4444' },
    { key: 'capitalAdequacy', label: 'Capital (%)', color: '#8b5cf6' },
    { key: 'assetQuality', label: 'Asset Quality (%)', color: '#06b6d4' }
  ]

  const filteredBanks = mockBenchmarkData.filter(bank => 
    selectedPeerGroup === 'All Banks' || bank.category === selectedPeerGroup || bank.peerGroup === selectedPeerGroup
  )
  const selectedBankData = mockBenchmarkData.filter(bank => selectedBanks.includes(bank.id))

  const getMetricColor = (index: number) => {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
    return colors[index % colors.length]
  }

  const getPercentileColor = (percentile: number) => {
    if (percentile >= 90) return 'text-success-600 bg-success-50'
    if (percentile >= 75) return 'text-primary-600 bg-primary-50'
    if (percentile >= 50) return 'text-warning-600 bg-warning-50'
    return 'text-danger-600 bg-danger-50'
  }

  const renderPerformanceChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={selectedBankData[0]?.performance || []}>
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
            metrics.find(m => m.key === name)?.label || name
          ]}
        />
        <Legend />
        {selectedMetrics.map((metric, index) => (
          <Line
            key={metric}
            type="monotone"
            dataKey={metric}
            stroke={getMetricColor(index)}
            strokeWidth={2}
            dot={{ fill: getMetricColor(index), strokeWidth: 2, r: 4 }}
            name={metrics.find(m => m.key === metric)?.label}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )

  const renderBenchmarksChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={industryBenchmarks}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="metric" stroke="#6b7280" />
        <YAxis stroke="#6b7280" />
        <Tooltip
          formatter={(value: any, name: string) => [
            `${value.toFixed(2)}%`,
            name
          ]}
        />
        <Legend />
        <Bar dataKey="tier1" fill="#3b82f6" name="Tier 1" />
        <Bar dataKey="tier2" fill="#10b981" name="Tier 2" />
        <Bar dataKey="regional" fill="#f59e0b" name="Regional" />
        <Bar dataKey="specialized" fill="#ef4444" name="Specialized" />
        <Bar dataKey="industry" fill="#8b5cf6" name="Industry" />
      </BarChart>
    </ResponsiveContainer>
  )

  const renderRankingChart = () => {
    const rankingData = selectedBankData.map(bank => ({
      name: bank.name,
      roe: bank.metrics.roe,
      roa: bank.metrics.roa,
      nim: bank.metrics.nim,
      efficiency: bank.metrics.efficiency,
      percentile: bank.percentile
    }))

    return (
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={rankingData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" stroke="#6b7280" />
          <YAxis stroke="#6b7280" />
          <Tooltip
            formatter={(value: any, name: string) => [
              `${value.toFixed(2)}%`,
              metrics.find(m => m.key === name)?.label || name
            ]}
          />
          <Legend />
          <Bar dataKey="roe" fill="#3b82f6" name="ROE (%)" />
          <Bar dataKey="roa" fill="#10b981" name="ROA (%)" />
          <Bar dataKey="nim" fill="#f59e0b" name="NIM (%)" />
          <Line type="monotone" dataKey="efficiency" stroke="#ef4444" strokeWidth={2} name="Efficiency (%)" />
        </ComposedChart>
      </ResponsiveContainer>
    )
  }

  const renderAnalysisChart = () => {
    const analysisData = selectedBankData.map(bank => ({
      name: bank.name,
      riskScore: bank.metrics.riskScore,
      profitability: bank.metrics.profitability,
      marketCap: bank.marketCap / 100
    }))

    return (
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis type="number" dataKey="riskScore" name="Risk Score" stroke="#6b7280" />
          <YAxis type="number" dataKey="profitability" name="Profitability" stroke="#6b7280" />
          <Tooltip
            formatter={(value: any, name: string) => [
              name === 'marketCap' ? `$${value.toFixed(1)}B` : value.toFixed(2),
              name === 'marketCap' ? 'Market Cap' : name
            ]}
          />
          <Legend />
          <Scatter name="Banks" data={analysisData} fill="#3b82f6">
            {analysisData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getMetricColor(index)} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    )
  }

  const renderChart = () => {
    switch (selectedView) {
      case 'performance':
        return renderPerformanceChart()
      case 'benchmarks':
        return renderBenchmarksChart()
      case 'ranking':
        return renderRankingChart()
      case 'analysis':
        return renderAnalysisChart()
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Bank Benchmarking</h1>
          <p className="text-neutral-600">Compare bank performance against industry benchmarks and peers</p>
        </div>

        <div className="flex flex-wrap gap-3">
          {/* Bank Selector */}
          <div className="relative">
            <select
              multiple
              value={selectedBanks}
              onChange={(e) => {
                const values = Array.from(e.target.selectedOptions, option => option.value)
                setSelectedBanks(values)
              }}
              className="rounded-lg border border-neutral-300 bg-white px-3 py-2 pr-8 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 min-w-[200px]"
            >
              {mockBenchmarkData.map(bank => (
                <option key={bank.id} value={bank.id}>
                  {bank.name} ({bank.category})
                </option>
              ))}
            </select>
            <BanknotesIcon className="absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          </div>

          {/* Peer Group Filter */}
          <div className="relative">
            <select
              value={selectedPeerGroup}
              onChange={(e) => setSelectedPeerGroup(e.target.value)}
              className="rounded-lg border border-neutral-300 bg-white px-3 py-2 pr-8 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              {peerGroups.map(group => (
                <option key={group} value={group}>{group}</option>
              ))}
            </select>
            <BuildingOfficeIcon className="absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          </div>
        </div>
      </div>

      {/* Selected Banks Overview */}
      {selectedBankData.length > 0 && (
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Selected Banks Overview</h3>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
            {selectedBankData.map((bank) => (
              <motion.div
                key={bank.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-lg border border-neutral-200 p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-neutral-900">{bank.name}</h4>
                    <p className="text-sm text-neutral-500">{bank.category}</p>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${getPercentileColor(bank.percentile)}`}>
                    {bank.percentile}th percentile
                  </div>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Assets:</span>
                    <span className="font-medium">${bank.assets.toFixed(0)}B</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Market Cap:</span>
                    <span className="font-medium">${bank.marketCap.toFixed(1)}B</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">ROE:</span>
                    <span className="font-medium text-success-600">{bank.metrics.roe}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Industry Rank:</span>
                    <span className="font-medium">#{bank.industryRank}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

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

      {/* Metric Selection */}
      {(selectedView === 'performance' || selectedView === 'ranking') && (
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Select Performance Metrics</h3>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {metrics.map((metric) => (
              <button
                key={metric.key}
                onClick={() => {
                  if (selectedMetrics.includes(metric.key)) {
                    setSelectedMetrics(selectedMetrics.filter(m => m !== metric.key))
                  } else {
                    setSelectedMetrics([...selectedMetrics, metric.key])
                  }
                }}
                className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                  selectedMetrics.includes(metric.key)
                    ? 'bg-primary-100 text-primary-700 border-primary-300'
                    : 'bg-white text-neutral-600 border-neutral-200 hover:border-primary-300 hover:text-primary-600'
                }`}
              >
                <div className="text-center">
                  <div className="font-semibold">{metric.label}</div>
                  <div className="w-3 h-3 rounded-full mx-auto mt-1" style={{ backgroundColor: metric.color }}></div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Chart */}
      <div className="glass-effect rounded-xl p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">
          {selectedView === 'performance' && 'Performance Comparison'}
          {selectedView === 'benchmarks' && 'Industry Benchmarks'}
          {selectedView === 'ranking' && 'Performance Ranking'}
          {selectedView === 'analysis' && 'Risk vs. Performance Analysis'}
        </h3>
        {renderChart()}
      </div>

      {/* Benchmark Comparison Table */}
      {selectedView === 'benchmarks' && (
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Detailed Benchmark Comparison</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="text-left py-3 px-4 font-medium text-neutral-700">Metric</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">Tier 1</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">Tier 2</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">Regional</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">Specialized</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">Industry</th>
                </tr>
              </thead>
              <tbody>
                {industryBenchmarks.map((benchmark, index) => (
                  <tr key={benchmark.metric} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="py-3 px-4 font-medium text-neutral-900">{benchmark.metric}</td>
                    <td className="text-center py-3 px-4">
                      <div className="flex items-center justify-center gap-2">
                        <span className="font-medium">{benchmark.tier1.toFixed(2)}%</span>
                        {index === 0 && <TrophyIcon className="h-4 w-4 text-yellow-500" />}
                      </div>
                    </td>
                    <td className="text-center py-3 px-4 font-medium">{benchmark.tier2.toFixed(2)}%</td>
                    <td className="text-center py-3 px-4 font-medium">{benchmark.regional.toFixed(2)}%</td>
                    <td className="text-center py-3 px-4 font-medium">{benchmark.specialized.toFixed(2)}%</td>
                    <td className="text-center py-3 px-4 font-medium">{benchmark.industry.toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Performance Insights */}
      <div className="glass-effect rounded-xl p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Performance Insights</h3>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="space-y-3">
            <h4 className="font-medium text-neutral-900">Top Performers</h4>
            <div className="space-y-2 text-sm">
              {selectedBankData
                .sort((a, b) => b.metrics.roe - a.metrics.roe)
                .slice(0, 3)
                .map((bank, index) => (
                  <div key={bank.id} className="flex items-center gap-2 text-success-600">
                    <div className="flex items-center gap-1">
                      {index === 0 && <StarIcon className="h-4 w-4 text-yellow-500" />}
                      <span>{bank.name}</span>
                    </div>
                    <span className="ml-auto font-medium">{bank.metrics.roe}% ROE</span>
                  </div>
                ))}
            </div>
          </div>
          <div className="space-y-3">
            <h4 className="font-medium text-neutral-900">Key Observations</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-primary-600">
                <TrendingUpIcon className="h-4 w-4" />
                <span>Tier 1 banks show superior ROE performance</span>
              </div>
              <div className="flex items-center gap-2 text-warning-600">
                <ScaleIcon className="h-4 w-4" />
                <span>Efficiency ratios vary significantly by category</span>
              </div>
              <div className="flex items-center gap-2 text-success-600">
                <ChartBarIcon className="h-4 w-4" />
                <span>Regional banks excel in NIM performance</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}