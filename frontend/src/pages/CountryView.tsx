import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useDashboard } from '../contexts/DashboardContext'
import { 
  GlobeAltIcon, 
  BanknotesIcon,
  ChartBarIcon,
  MapPinIcon,
  FlagIcon,
  BuildingOfficeIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

interface CountryBankData {
  id: string
  name: string
  country: string
  region: string
  sector: string
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
  }
  performance: Array<{
    date: string
    roe: number
    roa: number
    nim: number
    efficiency: number
  }>
}

interface CountryEconomicData {
  country: string
  region: string
  population: number
  gdp: number
  gdpGrowth: number
  inflation: number
  interestRate: number
  unemployment: number
  bankingAssets: number
  bankCount: number
  regulatoryScore: number
  marketAccess: number
}

const mockCountryBanks: CountryBankData[] = [
  {
    id: 'jpm',
    name: 'JPMorgan Chase',
    country: 'US',
    region: 'North America',
    sector: 'Commercial Banking',
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
      profitability: 92.1
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
    sector: 'Commercial Banking',
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
      profitability: 88.9
    },
    performance: [
      { date: '2023-01', roe: 12.5, roa: 1.0, nim: 2.3, efficiency: 62.8 },
      { date: '2023-04', roe: 12.9, roa: 1.1, nim: 2.4, efficiency: 62.3 },
      { date: '2023-07', roe: 13.2, roa: 1.1, nim: 2.5, efficiency: 61.7 },
      { date: '2023-10', roe: 12.8, roa: 1.1, nim: 2.4, efficiency: 62.1 }
    ]
  },
  {
    id: 'wells',
    name: 'Wells Fargo',
    country: 'US',
    region: 'North America',
    sector: 'Commercial Banking',
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
      profitability: 85.6
    },
    performance: [
      { date: '2023-01', roe: 11.5, roa: 0.9, nim: 2.8, efficiency: 66.2 },
      { date: '2023-04', roe: 11.8, roa: 1.0, nim: 2.9, efficiency: 65.9 },
      { date: '2023-07', roe: 12.1, roa: 1.0, nim: 3.0, efficiency: 65.5 },
      { date: '2023-10', roe: 11.9, roa: 1.0, nim: 2.9, efficiency: 65.8 }
    ]
  }
]

const mockCountryEconomics: CountryEconomicData[] = [
  {
    country: 'US',
    region: 'North America',
    population: 331.9,
    gdp: 25462.7,
    gdpGrowth: 2.8,
    inflation: 3.1,
    interestRate: 5.50,
    unemployment: 3.3,
    bankingAssets: 23.8,
    bankCount: 4800,
    regulatoryScore: 8.5,
    marketAccess: 9.2
  },
  {
    country: 'UK',
    region: 'Europe',
    population: 67.3,
    gdp: 3070.7,
    gdpGrowth: 1.2,
    inflation: 4.6,
    interestRate: 5.25,
    unemployment: 4.2,
    bankingAssets: 8.9,
    bankCount: 350,
    regulatoryScore: 8.8,
    marketAccess: 8.9
  },
  {
    country: 'Germany',
    region: 'Europe',
    population: 83.2,
    gdp: 4072.0,
    gdpGrowth: -0.3,
    inflation: 3.2,
    interestRate: 4.50,
    unemployment: 3.1,
    bankingAssets: 7.2,
    bankCount: 1400,
    regulatoryScore: 8.9,
    marketAccess: 8.7
  },
  {
    country: 'Japan',
    region: 'Asia-Pacific',
    population: 125.7,
    gdp: 4231.1,
    gdpGrowth: 1.9,
    inflation: 2.8,
    interestRate: -0.10,
    unemployment: 2.6,
    bankingAssets: 12.1,
    bankCount: 120,
    regulatoryScore: 8.2,
    marketAccess: 8.5
  },
  {
    country: 'China',
    region: 'Asia-Pacific',
    population: 1402.0,
    gdp: 17963.2,
    gdpGrowth: 5.2,
    inflation: 2.1,
    interestRate: 3.85,
    unemployment: 5.1,
    bankingAssets: 45.2,
    bankCount: 4000,
    regulatoryScore: 7.8,
    marketAccess: 8.1
  }
]

const regions = ['All Regions', 'North America', 'Europe', 'Asia-Pacific', 'Latin America', 'Middle East & Africa']

export default function CountryView() {
  const { state } = useDashboard()
  const [selectedCountry, setSelectedCountry] = useState('US')
  const [selectedRegion, setSelectedRegion] = useState('All Regions')
  const [selectedView, setSelectedView] = useState<'overview' | 'banks' | 'economics' | 'comparison'>('overview')
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['roe', 'roa', 'nim'])

  const views = [
    { key: 'overview', label: 'Overview', description: 'Country banking overview' },
    { key: 'banks', label: 'Banks', description: 'Bank performance analysis' },
    { key: 'economics', label: 'Economics', description: 'Economic indicators' },
    { key: 'comparison', label: 'Comparison', description: 'Regional comparison' }
  ]

  const metrics = [
    { key: 'roe', label: 'ROE (%)', color: '#3b82f6' },
    { key: 'roa', label: 'ROA (%)', color: '#10b981' },
    { key: 'nim', label: 'NIM (%)', color: '#f59e0b' },
    { key: 'efficiency', label: 'Efficiency (%)', color: '#ef4444' },
    { key: 'capitalAdequacy', label: 'Capital (%)', color: '#8b5cf6' },
    { key: 'assetQuality', label: 'Asset Quality (%)', color: '#06b6d4' }
  ]

  const selectedCountryData = mockCountryEconomics.find(c => c.country === selectedCountry)
  const selectedCountryBanks = mockCountryBanks.filter(bank => bank.country === selectedCountry)
  const filteredCountries = mockCountryEconomics.filter(c => 
    selectedRegion === 'All Regions' || c.region === selectedRegion
  )

  const getMetricColor = (index: number) => {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
    return colors[index % colors.length]
  }

  const renderOverviewChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={selectedCountryBanks[0]?.performance || []}>
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

  const renderBanksChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={selectedCountryBanks}>
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
        {selectedMetrics.map((metric, index) => (
          <Bar
            key={metric}
            dataKey={metric}
            fill={getMetricColor(index)}
            radius={[2, 2, 0, 0]}
            name={metrics.find(m => m.key === metric)?.label}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )

  const renderEconomicsChart = () => {
    const economicData = filteredCountries.map(country => ({
      country: country.country,
      gdpGrowth: country.gdpGrowth,
      inflation: country.inflation,
      interestRate: country.interestRate,
      unemployment: country.unemployment
    }))

    return (
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={economicData}>
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
          <Bar dataKey="interestRate" fill="#ef4444" name="Interest Rate (%)" />
          <Bar dataKey="unemployment" fill="#8b5cf6" name="Unemployment (%)" />
        </BarChart>
      </ResponsiveContainer>
    )
  }

  const renderComparisonChart = () => {
    const comparisonData = filteredCountries.map(country => ({
      country: country.country,
      regulatoryScore: country.regulatoryScore,
      marketAccess: country.marketAccess,
      bankCount: country.bankCount / 100
    }))

    return (
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={comparisonData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="country" />
          <PolarRadiusAxis />
          <Radar
            name="Regulatory Score"
            dataKey="regulatoryScore"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.3}
          />
          <Radar
            name="Market Access"
            dataKey="marketAccess"
            stroke="#10b981"
            fill="#10b981"
            fillOpacity={0.3}
          />
          <Radar
            name="Bank Count (100s)"
            dataKey="bankCount"
            stroke="#f59e0b"
            fill="#f59e0b"
            fillOpacity={0.3}
          />
        </RadarChart>
      </ResponsiveContainer>
    )
  }

  const renderChart = () => {
    switch (selectedView) {
      case 'overview':
        return renderOverviewChart()
      case 'banks':
        return renderBanksChart()
      case 'economics':
        return renderEconomicsChart()
      case 'comparison':
        return renderComparisonChart()
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Country Analysis</h1>
          <p className="text-neutral-600">Analyze banking performance and economics by country</p>
        </div>
        
        <div className="flex flex-wrap gap-3">
          {/* Country Selector */}
          <div className="relative">
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="rounded-lg border border-neutral-300 bg-white px-3 py-2 pr-8 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              {mockCountryEconomics.map(country => (
                <option key={country.country} value={country.country}>{country.country}</option>
              ))}
            </select>
            <FlagIcon className="absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          </div>

          {/* Region Filter */}
          <div className="relative">
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="rounded-lg border border-neutral-300 bg-white px-3 py-2 pr-8 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              {regions.map(region => (
                <option key={region} value={region}>{region}</option>
              ))}
            </select>
            <GlobeAltIcon className="absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          </div>
        </div>
      </div>

      {/* Country Overview Card */}
      {selectedCountryData && (
        <div className="glass-effect rounded-xl p-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <MapPinIcon className="h-6 w-6 text-primary-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-neutral-900">{selectedCountryData.country}</h2>
                  <p className="text-neutral-600">{selectedCountryData.region}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-neutral-900">{selectedCountryData.population}</div>
                  <div className="text-sm text-neutral-500">Population (M)</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-neutral-900">${selectedCountryData.gdp.toFixed(0)}B</div>
                  <div className="text-sm text-neutral-500">GDP</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-neutral-900">{selectedCountryData.bankCount}</div>
                  <div className="text-sm text-neutral-500">Banks</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-neutral-900">${selectedCountryData.bankingAssets.toFixed(1)}T</div>
                  <div className="text-sm text-neutral-500">Banking Assets</div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="font-semibold text-neutral-900">Key Metrics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-neutral-600">GDP Growth:</span>
                  <span className={`font-medium ${selectedCountryData.gdpGrowth >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                    {selectedCountryData.gdpGrowth >= 0 ? '+' : ''}{selectedCountryData.gdpGrowth}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-600">Inflation:</span>
                  <span className="font-medium text-warning-600">{selectedCountryData.inflation}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-600">Interest Rate:</span>
                  <span className="font-medium text-primary-600">{selectedCountryData.interestRate}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-600">Unemployment:</span>
                  <span className="font-medium text-neutral-600">{selectedCountryData.unemployment}%</span>
                </div>
              </div>
            </div>
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
      {(selectedView === 'overview' || selectedView === 'banks') && (
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
          {selectedView === 'overview' && `${selectedCountry} Banking Performance`}
          {selectedView === 'banks' && `${selectedCountry} Bank Comparison`}
          {selectedView === 'economics' && 'Regional Economic Indicators'}
          {selectedView === 'comparison' && 'Regional Banking Comparison'}
        </h3>
        {renderChart()}
      </div>

      {/* Bank Details Table */}
      {selectedView === 'banks' && selectedCountryBanks.length > 0 && (
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Bank Details</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="text-left py-3 px-4 font-medium text-neutral-700">Bank</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">Assets ($B)</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">Market Cap ($B)</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">ROE (%)</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">ROA (%)</th>
                  <th className="text-center py-3 px-4 font-medium text-neutral-700">NIM (%)</th>
                </tr>
              </thead>
              <tbody>
                {selectedCountryBanks.map((bank, index) => (
                  <tr key={bank.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="py-3 px-4">
                      <div>
                        <div className="font-medium text-neutral-900">{bank.name}</div>
                        <div className="text-sm text-neutral-500">{bank.sector}</div>
                      </div>
                    </td>
                    <td className="text-center py-3 px-4 font-medium">{bank.assets.toFixed(1)}</td>
                    <td className="text-center py-3 px-4 font-medium">{bank.marketCap.toFixed(1)}</td>
                    <td className="text-center py-3 px-4 font-medium">{bank.metrics.roe.toFixed(1)}</td>
                    <td className="text-center py-3 px-4 font-medium">{bank.metrics.roa.toFixed(1)}</td>
                    <td className="text-center py-3 px-4 font-medium">{bank.metrics.nim.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Regional Insights */}
      {selectedView === 'comparison' && (
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Regional Insights</h3>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="space-y-3">
              <h4 className="font-medium text-neutral-900">Regulatory Environment</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-success-600">
                  <ArrowTrendingUpIcon className="h-4 w-4" />
                  <span>Europe has highest regulatory scores</span>
                </div>
                <div className="flex items-center gap-2 text-warning-600">
                  <ArrowTrendingDownIcon className="h-4 w-4" />
                  <span>Asia-Pacific shows regulatory diversity</span>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <h4 className="font-medium text-neutral-900">Market Access</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-success-600">
                  <ArrowTrendingUpIcon className="h-4 w-4" />
                  <span>North America leads in market access</span>
                </div>
                <div className="flex items-center gap-2 text-primary-600">
                  <ArrowTrendingUpIcon className="h-4 w-4" />
                  <span>UK maintains strong financial center status</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}