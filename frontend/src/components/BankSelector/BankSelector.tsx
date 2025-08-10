import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDashboard } from '../../contexts/DashboardContext'
import { 
  ChevronDownIcon, 
  FunnelIcon, 
  MagnifyingGlassIcon,
  GlobeAltIcon,
  BanknotesIcon
} from '@heroicons/react/24/outline'

const mockBanks = [
  { id: 'jpm', name: 'JPMorgan Chase', country: 'US', region: 'North America', sector: 'Commercial Banking' },
  { id: 'bac', name: 'Bank of America', country: 'US', region: 'North America', sector: 'Commercial Banking' },
  { id: 'wells', name: 'Wells Fargo', country: 'US', region: 'North America', sector: 'Commercial Banking' },
  { id: 'citi', name: 'Citigroup', country: 'US', region: 'North America', sector: 'Commercial Banking' },
  { id: 'hsbc', name: 'HSBC', country: 'UK', region: 'Europe', sector: 'Commercial Banking' },
  { id: 'barclays', name: 'Barclays', country: 'UK', region: 'Europe', sector: 'Commercial Banking' },
  { id: 'deutsche', name: 'Deutsche Bank', country: 'Germany', region: 'Europe', sector: 'Commercial Banking' },
  { id: 'bnp', name: 'BNP Paribas', country: 'France', region: 'Europe', sector: 'Commercial Banking' },
  { id: 'santander', name: 'Santander', country: 'Spain', region: 'Europe', sector: 'Commercial Banking' },
  { id: 'unicredit', name: 'UniCredit', country: 'Italy', region: 'Europe', sector: 'Commercial Banking' },
  { id: 'mizuho', name: 'Mizuho Financial', country: 'Japan', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'mufg', name: 'MUFG', country: 'Japan', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'smfg', name: 'SMFG', country: 'Japan', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'icbc', name: 'ICBC', country: 'China', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'ccb', name: 'China Construction Bank', country: 'China', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'abc', name: 'Agricultural Bank of China', country: 'China', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'boc', name: 'Bank of China', country: 'China', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'nab', name: 'National Australia Bank', country: 'Australia', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'cba', name: 'Commonwealth Bank', country: 'Australia', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'anz', name: 'ANZ', country: 'Australia', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'westpac', name: 'Westpac', country: 'Australia', region: 'Asia-Pacific', sector: 'Commercial Banking' },
  { id: 'td', name: 'TD Bank', country: 'Canada', region: 'North America', sector: 'Commercial Banking' },
  { id: 'rbc', name: 'Royal Bank of Canada', country: 'Canada', region: 'North America', sector: 'Commercial Banking' },
  { id: 'scotiabank', name: 'Scotiabank', country: 'Canada', region: 'North America', sector: 'Commercial Banking' }
]

const regions = ['All Regions', 'North America', 'Europe', 'Asia-Pacific', 'Latin America', 'Middle East & Africa']
const countries = ['All Countries', 'US', 'UK', 'Germany', 'France', 'Spain', 'Italy', 'Japan', 'China', 'Australia', 'Canada']

export default function BankSelector() {
  const { state, dispatch } = useDashboard()
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRegion, setSelectedRegion] = useState('All Regions')
  const [selectedCountry, setSelectedCountry] = useState('All Countries')

  const filteredBanks = mockBanks.filter(bank => {
    const matchesSearch = bank.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRegion = selectedRegion === 'All Regions' || bank.region === selectedRegion
    const matchesCountry = selectedCountry === 'All Countries' || bank.country === selectedCountry
    return matchesSearch && matchesRegion && matchesCountry
  })

  const handleBankToggle = (bankId: string) => {
    const newSelection = state.selectedBanks.includes(bankId)
      ? state.selectedBanks.filter(id => id !== bankId)
      : [...state.selectedBanks, bankId]
    dispatch({ type: 'SET_SELECTED_BANKS', payload: newSelection })
  }

  const handleViewModeChange = (mode: 'single' | 'comparison' | 'benchmark') => {
    dispatch({ type: 'SET_VIEW_MODE', payload: mode })
  }

  return (
    <div className="glass-effect rounded-xl p-6">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        {/* View Mode Toggle */}
        <div className="flex flex-col gap-3">
          <h3 className="text-lg font-semibold text-neutral-900">Analysis Mode</h3>
          <div className="flex rounded-lg bg-neutral-100 p-1">
            {[
              { key: 'single', label: 'Single Bank', icon: BanknotesIcon },
              { key: 'comparison', label: 'Comparison', icon: BanknotesIcon },
              { key: 'benchmark', label: 'Benchmark', icon: ScaleIcon }
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => handleViewModeChange(key as 'single' | 'comparison' | 'benchmark')}
                className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-all ${
                  state.viewMode === key
                    ? 'bg-white text-primary-700 shadow-sm'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-3 sm:flex-row">
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

          <div className="relative">
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="rounded-lg border border-neutral-300 bg-white px-3 py-2 pr-8 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              {countries.map(country => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
            <FunnelIcon className="absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          </div>
        </div>
      </div>

      {/* Bank Selection */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-base font-medium text-neutral-900">
            Select Banks ({state.selectedBanks.length} selected)
          </h4>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-2 rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-50 transition-colors"
          >
            {isOpen ? 'Hide' : 'Show'} Banks
            <ChevronDownIcon className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>
        </div>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              {/* Search */}
              <div className="relative mb-4">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
                <input
                  type="text"
                  placeholder="Search banks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full rounded-lg border border-neutral-300 bg-white pl-10 pr-4 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
              </div>

              {/* Bank Grid */}
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 max-h-96 overflow-y-auto">
                {filteredBanks.map(bank => (
                  <motion.div
                    key={bank.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-white p-3 hover:border-primary-300 transition-colors"
                  >
                    <input
                      type="checkbox"
                      id={bank.id}
                      checked={state.selectedBanks.includes(bank.id)}
                      onChange={() => handleBankToggle(bank.id)}
                      className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                    />
                    <div className="flex-1 min-w-0">
                      <label htmlFor={bank.id} className="block text-sm font-medium text-neutral-900 cursor-pointer">
                        {bank.name}
                      </label>
                      <p className="text-xs text-neutral-500">{bank.country} • {bank.region}</p>
                    </div>
                  </motion.div>
                ))}
              </div>

              {filteredBanks.length === 0 && (
                <div className="text-center py-8 text-neutral-500">
                  No banks found matching your criteria
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}