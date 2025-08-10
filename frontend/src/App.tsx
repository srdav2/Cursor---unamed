import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { DashboardProvider } from './contexts/DashboardContext'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard'
import BankComparison from './pages/BankComparison'
import EconomicAnalysis from './pages/EconomicAnalysis'
import CountryView from './pages/CountryView'
import Benchmarking from './pages/Benchmarking'

function App() {
  return (
    <DashboardProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/comparison" element={<BankComparison />} />
          <Route path="/economic" element={<EconomicAnalysis />} />
          <Route path="/country" element={<CountryView />} />
          <Route path="/benchmarking" element={<Benchmarking />} />
        </Routes>
      </Layout>
    </DashboardProvider>
  )
}

export default App