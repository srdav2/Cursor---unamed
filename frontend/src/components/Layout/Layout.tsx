import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChartBarIcon, 
  BanknotesIcon, 
  GlobeAltIcon, 
  ScaleIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface LayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: ChartBarIcon },
  { name: 'Bank Comparison', href: '/comparison', icon: BanknotesIcon },
  { name: 'Economic Analysis', href: '/economic', icon: GlobeAltIcon },
  { name: 'Country View', href: '/country', icon: GlobeAltIcon },
  { name: 'Benchmarking', href: '/benchmarking', icon: ScaleIcon },
]

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Mobile sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 lg:hidden"
          >
            <div className="fixed inset-0 bg-neutral-900/80" onClick={() => setSidebarOpen(false)} />
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 20, stiffness: 100 }}
              className="fixed left-0 top-0 bottom-0 w-80 bg-white shadow-xl"
            >
              <div className="flex h-full flex-col">
                <div className="flex h-16 items-center justify-between px-6">
                  <h1 className="text-xl font-bold gradient-text">Bank Analytics</h1>
                  <button
                    onClick={() => setSidebarOpen(false)}
                    className="rounded-md p-2 text-neutral-400 hover:text-neutral-600"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>
                <nav className="flex-1 space-y-1 px-4 py-4">
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      onClick={() => setSidebarOpen(false)}
                      className={`group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                        location.pathname === item.href
                          ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                          : 'text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900'
                      }`}
                    >
                      <item.icon className="mr-3 h-5 w-5" />
                      {item.name}
                    </Link>
                  ))}
                </nav>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-80 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-xl">
          <div className="flex h-16 items-center">
            <h1 className="text-2xl font-bold gradient-text">Bank Analytics</h1>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={`group flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 transition-colors ${
                          location.pathname === item.href
                            ? 'bg-primary-50 text-primary-700'
                            : 'text-neutral-700 hover:bg-neutral-100 hover:text-primary-700'
                        }`}
                      >
                        <item.icon className="h-6 w-6 shrink-0" />
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-80">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-neutral-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-neutral-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1"></div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* Add user profile, notifications, etc. here */}
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}