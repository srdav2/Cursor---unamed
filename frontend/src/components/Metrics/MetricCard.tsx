import React from 'react'
import { motion } from 'framer-motion'
import { IconType } from '@heroicons/react/24/outline'

interface MetricCardProps {
  title: string
  value: string
  change: string
  changeType: 'positive' | 'negative' | 'neutral'
  icon: IconType
  color: 'primary' | 'success' | 'warning' | 'danger'
  delay?: number
}

const colorClasses = {
  primary: {
    bg: 'bg-primary-50',
    icon: 'text-primary-600',
    change: 'text-primary-700',
    border: 'border-primary-200'
  },
  success: {
    bg: 'bg-success-50',
    icon: 'text-success-600',
    change: 'text-success-700',
    border: 'border-success-200'
  },
  warning: {
    bg: 'bg-warning-50',
    icon: 'text-warning-600',
    change: 'text-warning-700',
    border: 'border-warning-200'
  },
  danger: {
    bg: 'bg-danger-50',
    icon: 'text-danger-600',
    change: 'text-danger-700',
    border: 'border-danger-200'
  }
}

export default function MetricCard({ 
  title, 
  value, 
  change, 
  changeType, 
  icon: Icon, 
  color, 
  delay = 0 
}: MetricCardProps) {
  const colors = colorClasses[color]
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className={`${colors.bg} ${colors.border} rounded-xl border p-6 card-hover`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-neutral-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-neutral-900">{value}</p>
          <div className="mt-2 flex items-center gap-2">
            <span className={`text-sm font-medium ${colors.change}`}>
              {changeType === 'positive' && '+'}
              {change}
            </span>
            <span className="text-xs text-neutral-500">
              from last period
            </span>
          </div>
        </div>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: delay + 0.2, type: 'spring', stiffness: 200 }}
          className={`${colors.icon} p-3 rounded-lg bg-white shadow-sm`}
        >
          <Icon className="h-6 w-6" />
        </motion.div>
      </div>
      
      {/* Trend indicator */}
      <div className="mt-4 flex items-center gap-2">
        <div className={`h-1 flex-1 rounded-full ${
          changeType === 'positive' ? 'bg-success-200' : 
          changeType === 'negative' ? 'bg-danger-200' : 'bg-neutral-200'
        }`}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: changeType === 'positive' ? '75%' : changeType === 'negative' ? '25%' : '50%' }}
            transition={{ delay: delay + 0.4, duration: 0.8 }}
            className={`h-full rounded-full ${
              changeType === 'positive' ? 'bg-success-500' : 
              changeType === 'negative' ? 'bg-danger-500' : 'bg-neutral-400'
            }`}
          />
        </div>
        <span className={`text-xs font-medium ${
          changeType === 'positive' ? 'text-success-600' : 
          changeType === 'negative' ? 'text-danger-600' : 'text-neutral-500'
        }`}>
          {changeType === 'positive' ? '↗' : changeType === 'negative' ? '↘' : '→'}
        </span>
      </div>
    </motion.div>
  )
}