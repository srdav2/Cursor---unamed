import React, { createContext, useContext, useReducer, ReactNode } from 'react'

export interface Bank {
  id: string
  name: string
  country: string
  region: string
  sector: string
  marketCap: number
  totalAssets: number
}

export interface EconomicIndicator {
  id: string
  name: string
  category: string
  frequency: string
  source: string
  lastUpdated: string
}

export interface DashboardState {
  selectedBanks: string[]
  selectedCountries: string[]
  selectedRegions: string[]
  selectedIndicators: string[]
  timeRange: {
    start: string
    end: string
  }
  viewMode: 'single' | 'comparison' | 'benchmark'
  dataGranularity: 'daily' | 'weekly' | 'monthly' | 'quarterly'
  isLoading: boolean
  error: string | null
}

export type DashboardAction =
  | { type: 'SET_SELECTED_BANKS'; payload: string[] }
  | { type: 'SET_SELECTED_COUNTRIES'; payload: string[] }
  | { type: 'SET_SELECTED_REGIONS'; payload: string[] }
  | { type: 'SET_SELECTED_INDICATORS'; payload: string[] }
  | { type: 'SET_TIME_RANGE'; payload: { start: string; end: string } }
  | { type: 'SET_VIEW_MODE'; payload: 'single' | 'comparison' | 'benchmark' }
  | { type: 'SET_DATA_GRANULARITY'; payload: 'daily' | 'weekly' | 'monthly' | 'quarterly' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESET_FILTERS' }

const initialState: DashboardState = {
  selectedBanks: [],
  selectedCountries: [],
  selectedRegions: [],
  selectedIndicators: [],
  timeRange: {
    start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  },
  viewMode: 'single',
  dataGranularity: 'monthly',
  isLoading: false,
  error: null
}

function dashboardReducer(state: DashboardState, action: DashboardAction): DashboardState {
  switch (action.type) {
    case 'SET_SELECTED_BANKS':
      return { ...state, selectedBanks: action.payload }
    case 'SET_SELECTED_COUNTRIES':
      return { ...state, selectedCountries: action.payload }
    case 'SET_SELECTED_REGIONS':
      return { ...state, selectedRegions: action.payload }
    case 'SET_SELECTED_INDICATORS':
      return { ...state, selectedIndicators: action.payload }
    case 'SET_TIME_RANGE':
      return { ...state, timeRange: action.payload }
    case 'SET_VIEW_MODE':
      return { ...state, viewMode: action.payload }
    case 'SET_DATA_GRANULARITY':
      return { ...state, dataGranularity: action.payload }
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    case 'RESET_FILTERS':
      return { ...initialState, timeRange: state.timeRange }
    default:
      return state
  }
}

interface DashboardContextType {
  state: DashboardState
  dispatch: React.Dispatch<DashboardAction>
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined)

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(dashboardReducer, initialState)

  return (
    <DashboardContext.Provider value={{ state, dispatch }}>
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard() {
  const context = useContext(DashboardContext)
  if (context === undefined) {
    throw new Error('useDashboard must be used within a DashboardProvider')
  }
  return context
}