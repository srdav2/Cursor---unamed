import React from 'react'
import { motion } from 'framer-motion'
import { useDashboard } from '../contexts/DashboardContext'
import BankSelector from '../components/BankSelector/BankSelector'
import MetricCard from '../components/Metrics/MetricCard'
import PerformanceChart from '../components/Charts/PerformanceChart'
import EconomicOverlay from '../components/Charts/EconomicOverlay'
import { 
  BanknotesIcon, 
  TrendingUpIcon, 
  GlobeAltIcon, 
  ScaleIcon 
} from '@heroicons/react/24/outline'

export default function Dashboard() {
  const { state } = useDashboard()

  const metrics = [
    {
      title: 'Total Banks',
      value: '24',
      change: '+2',
      changeType: 'positive' as const,
      icon: BanknotesIcon,
      color: 'primary'
    },
    {
      title: 'Avg ROE',
      value: '12.4%',
      change: '+0.8%',
      changeType: 'positive' as const,
      icon: TrendingUpIcon,
      color: 'success'
    },
    {
      title: 'Countries',
      value: '18',
      change: '+3',
      changeType: 'positive' as const,
      icon: GlobeAltIcon,
      color: 'warning'
    },
    {
      title: 'Risk Score',
      value: '7.2/10',
      change: '-0.3',
      changeType: 'negative' as const,
      icon: ScaleIcon,
      color: 'danger'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Bank Performance Dashboard</h1>
          <p className="mt-2 text-neutral-600">
            Comprehensive analysis of bank performance across global markets with economic context
          </p>
        </div>
        <div className="flex gap-3">
          <button className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors">
            Export Report
          </button>
          <button className="rounded-lg border border-neutral-300 bg-white px-4 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-50 transition-colors">
            Settings
          </button>
        </div>
      </motion.div>

      {/* Bank Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <BankSelector />
      </motion.div>

      {/* Metrics Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4"
      >
        {metrics.map((metric, index) => (
          <MetricCard key={metric.title} {...metric} delay={index * 0.1} />
        ))}
      </motion.div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Performance Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-effect rounded-xl p-6"
        >
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Performance Overview</h3>
          <PerformanceChart />
        </motion.div>

        {/* Economic Context */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-effect rounded-xl p-6"
        >
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Economic Context</h3>
          <EconomicOverlay />
        </motion.div>
      </div>

      {/* Additional Insights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-effect rounded-xl p-6"
      >
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Key Insights</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-lg bg-success-50 p-4">
            <h4 className="font-medium text-success-800">Strong Performance</h4>
            <p className="text-sm text-success-600 mt-1">
              European banks showing resilience despite economic headwinds
            </p>
          </div>
          <div className="rounded-lg bg-warning-50 p-4">
            <h4 className="font-medium text-warning-800">Watch Areas</h4>
            <p className="text-sm text-warning-600 mt-1">
              NPL ratios increasing in emerging markets
            </p>
          </div>
          <div className="rounded-lg bg-primary-50 p-4">
            <h4 className="font-medium text-primary-800">Opportunities</h4>
            <p className="text-sm text-primary-600 mt-1">
              Digital transformation driving efficiency gains
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}