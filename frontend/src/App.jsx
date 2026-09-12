import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, ScanLine, Leaf, Droplets, Cloud, Shield,
  Globe, MessageSquare, Menu, X, Moon, Sun, Bell, ChevronRight
} from 'lucide-react'
import './index.css'

import Dashboard       from './components/Dashboard'
import DiseaseDetection from './components/DiseaseDetection'
import CropRecommendation from './components/CropRecommendation'
import SmartIrrigation  from './components/SmartIrrigation'
import SustainabilityScore from './components/SustainabilityScore'
import FarmerAssistant  from './components/FarmerAssistant'
import FieldGuard       from './components/FieldGuard'

const NAV_ITEMS = [
  { to: '/',              icon: LayoutDashboard, label: 'Dashboard'         },
  { to: '/disease',       icon: ScanLine,        label: 'Disease Detection' },
  { to: '/crops',         icon: Leaf,            label: 'Crop Recommendation'},
  { to: '/irrigation',    icon: Droplets,        label: 'Smart Irrigation'  },
  { to: '/weather',       icon: Cloud,           label: 'Weather Intelligence'},
  { to: '/fieldguard',    icon: Shield,          label: 'FieldGuard',  badge: 'Pro' },
  { to: '/sustainability', icon: Globe,          label: 'Sustainability'    },
  { to: '/assistant',     icon: MessageSquare,   label: 'Farmer Assistant'  },
]

function Sidebar({ open, onClose }) {
  const location = useLocation()

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="sidebar-overlay"
          onClick={onClose}
          aria-label="Close menu"
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`sidebar ${open ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0`}
        aria-label="Main navigation"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-5 border-b border-forest-800">
          <div className="w-9 h-9 rounded-xl bg-forest-500 flex items-center justify-center flex-shrink-0">
            <Leaf size={20} className="text-forest-950" />
          </div>
          <div>
            <div className="text-white font-bold text-base leading-tight">AgriSmart AI</div>
            <div className="text-forest-400 text-xs">Smart Farming · Better Decisions</div>
          </div>
          <button
            className="ml-auto lg:hidden text-forest-400 hover:text-white"
            onClick={onClose}
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>

        {/* Farm indicator */}
        <div className="mx-4 mt-4 mb-2 px-3 py-2.5 rounded-xl bg-forest-800 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-forest-400 flex-shrink-0" />
          <span className="text-forest-200 text-xs font-medium truncate">Green Acres Farm</span>
          <ChevronRight size={14} className="ml-auto text-forest-500 flex-shrink-0" />
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto px-3 py-2 space-y-0.5">
          {NAV_ITEMS.map(({ to, icon: Icon, label, badge }) => {
            const isActive = to === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(to)
            return (
              <NavLink
                key={to}
                to={to}
                onClick={onClose}
                className={`nav-item ${isActive ? 'active' : ''}`}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon size={18} className="flex-shrink-0" />
                <span className="flex-1">{label}</span>
                {badge && (
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-harvest-500 text-white">
                    {badge}
                  </span>
                )}
              </NavLink>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="px-4 pb-5 pt-3 border-t border-forest-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-forest-600 flex items-center justify-center text-white text-xs font-bold">
              SF
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-forest-200 text-xs font-semibold truncate">Sample Farmer</div>
              <div className="text-forest-500 text-[10px]">English</div>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

function TopBar({ onMenuClick, dark, onToggleDark }) {
  return (
    <header className="sticky top-0 z-20 flex items-center gap-3 bg-white/90 backdrop-blur border-b border-forest-100 px-4 py-3 lg:px-6">
      <button
        className="lg:hidden p-2 rounded-lg text-forest-600 hover:bg-forest-100"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>

      {/* Breadcrumb demo */}
      <div className="hidden sm:flex items-center gap-1.5 text-sm text-forest-500 font-medium">
        <Leaf size={14} className="text-forest-600" />
        <span className="text-forest-700">Green Acres</span>
        <ChevronRight size={14} />
        <span>Overview</span>
      </div>

      {/* Weather demo badge */}
      <div className="hidden md:flex items-center gap-2 ml-4 px-3 py-1.5 rounded-lg bg-forest-50 border border-forest-200 text-xs text-forest-700 font-medium">
        <span>☀️</span>
        <span>28°C · Manual Input</span>
      </div>

      <div className="ml-auto flex items-center gap-2">
        {/* Notifications */}
        <button className="p-2 rounded-lg text-forest-600 hover:bg-forest-100 relative" aria-label="Notifications">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-harvest-500 rounded-full" />
        </button>

        {/* Theme toggle */}
        <button
          onClick={onToggleDark}
          className="p-2 rounded-lg text-forest-600 hover:bg-forest-100"
          aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Avatar */}
        <div className="w-8 h-8 rounded-full bg-forest-700 flex items-center justify-center text-white text-xs font-bold cursor-pointer">
          SF
        </div>
      </div>
    </header>
  )
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [dark, setDark] = useState(false)

  const handleToggleDark = () => {
    setDark(d => !d)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <Router>
      <div className="flex min-h-screen bg-forest-50">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        {/* Main content area */}
        <div className="flex-1 flex flex-col min-w-0 lg:ml-64">
          <TopBar
            onMenuClick={() => setSidebarOpen(true)}
            dark={dark}
            onToggleDark={handleToggleDark}
          />

          <main className="flex-1 p-4 lg:p-6 overflow-auto">
            <Routes>
              <Route path="/"               element={<Dashboard />} />
              <Route path="/disease"        element={<DiseaseDetection />} />
              <Route path="/crops"          element={<CropRecommendation />} />
              <Route path="/irrigation"     element={<SmartIrrigation />} />
              <Route path="/weather"        element={<SmartIrrigation />} />
              <Route path="/fieldguard"     element={<FieldGuard />} />
              <Route path="/sustainability" element={<SustainabilityScore />} />
              <Route path="/assistant"      element={<FarmerAssistant />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App
