import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, ScanLine, Leaf, Droplets, Cloud, Shield,
  Globe, MessageSquare, Menu, X, Moon, Sun, Bell, ChevronRight, MapPin
} from 'lucide-react'
import Dashboard       from './components/Dashboard'
import DiseaseDetection from './components/DiseaseDetection'
import CropRecommendation from './components/CropRecommendation'
import SmartIrrigation  from './components/SmartIrrigation'
import WeatherIntelligence from './components/WeatherIntelligence'
import SustainabilityScore from './components/SustainabilityScore'
import FarmerAssistant  from './components/FarmerAssistant'
import FieldGuard       from './components/FieldGuard'
import Login            from './components/Login'
import Register         from './components/Register'
import Profile          from './components/Profile'
import FarmProfile      from './components/FarmProfile'
import { AuthProvider, useAuth } from './context/AuthContext'
import { Navigate } from 'react-router-dom'

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
        className={`sidebar ${open ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 dark:bg-forest-950 dark:border-r dark:border-forest-800`}
        aria-label="Main navigation"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-5 border-b border-forest-800 dark:border-forest-800">
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
          <span className="text-forest-200 text-xs font-medium truncate">My Farm</span>
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
        <div className="px-4 pb-5 pt-3 border-t border-forest-800 space-y-1">
          <NavLink to="/profile" onClick={onClose} className={({ isActive }) => `flex items-center gap-3 p-2 rounded-xl transition-colors cursor-pointer ${isActive ? 'bg-forest-800' : 'hover:bg-forest-800/50'}`}>
            <div className="w-8 h-8 rounded-full bg-forest-600 flex items-center justify-center text-white text-xs font-bold uppercase">
              U
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-forest-200 text-xs font-semibold truncate">My Profile</div>
            </div>
          </NavLink>
          <NavLink to="/farm-profile" onClick={onClose} className={({ isActive }) => `flex items-center gap-3 p-2 rounded-xl transition-colors cursor-pointer ${isActive ? 'bg-forest-800' : 'hover:bg-forest-800/50'}`}>
            <div className="w-8 h-8 rounded-full bg-harvest-600 flex items-center justify-center text-white text-xs font-bold">
              <MapPin size={14} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-forest-200 text-xs font-semibold truncate">Farm Details</div>
            </div>
          </NavLink>
        </div>
      </aside>
    </>
  )
}

function TopBar({ onMenuClick, dark, onToggleDark }) {
  const [showNotif, setShowNotif] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  return (
    <header className="sticky top-0 z-20 flex items-center gap-3 bg-white/90 dark:bg-forest-950/90 backdrop-blur border-b border-forest-100 dark:border-forest-800 px-4 py-3 lg:px-6">
      <button
        className="lg:hidden p-2 rounded-lg text-forest-600 dark:text-forest-400 hover:bg-forest-100 dark:hover:bg-forest-800"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>

      {/* Breadcrumb demo */}
      <div className="hidden sm:flex items-center gap-1.5 text-sm text-forest-500 dark:text-forest-400 font-medium">
        <Leaf size={14} className="text-forest-600 dark:text-forest-400" />
        <span className="text-forest-700 dark:text-forest-300">Green Acres</span>
        <ChevronRight size={14} />
        <span>Overview</span>
      </div>

      {/* Weather demo badge */}
      <div className="hidden md:flex items-center gap-2 ml-4 px-3 py-1.5 rounded-lg bg-forest-50 dark:bg-forest-900 border border-forest-200 dark:border-forest-700 text-xs text-forest-700 dark:text-forest-300 font-medium">
        <span>☀️</span>
        <span>28°C · Manual Input</span>
      </div>

      <div className="ml-auto flex items-center gap-2 relative">
        {/* Notifications */}
        <button 
          className="p-2 rounded-lg text-forest-600 dark:text-forest-400 hover:bg-forest-100 dark:hover:bg-forest-800 relative" 
          aria-label="Open notifications"
          onClick={() => setShowNotif(!showNotif)}
        >
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-harvest-500 rounded-full" />
        </button>

        {showNotif && (
          <div className="absolute top-12 right-10 w-72 bg-white dark:bg-forest-900 border border-forest-100 dark:border-forest-700 rounded-xl shadow-agri-md p-4 z-50">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold text-forest-900 dark:text-forest-100">Notifications</h3>
              <span className="text-xs px-2 py-0.5 bg-forest-100 dark:bg-forest-800 text-forest-700 dark:text-forest-300 rounded-full">Prototype</span>
            </div>
            <ul className="space-y-2 text-sm text-forest-700 dark:text-forest-300">
              <li className="p-2 bg-forest-50 dark:bg-forest-950 rounded-lg border-l-4 border-harvest-400">Review today's irrigation advisory</li>
              <li className="p-2 bg-forest-50 dark:bg-forest-950 rounded-lg border-l-4 border-red-400">Check FieldGuard risk assessment</li>
              <li className="p-2 bg-forest-50 dark:bg-forest-950 rounded-lg border-l-4 border-blue-400">Disease detection prototype ready</li>
            </ul>
          </div>
        )}

        {/* Theme toggle */}
        <button
          onClick={onToggleDark}
          className="p-2 rounded-lg text-forest-600 dark:text-forest-400 hover:bg-forest-100 dark:hover:bg-forest-800"
          aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Avatar */}
        <div 
          className="w-8 h-8 rounded-full bg-forest-700 dark:bg-forest-600 flex items-center justify-center text-white text-xs font-bold cursor-pointer uppercase"
          onClick={() => setShowMenu(!showMenu)}
          aria-label="Open account menu"
        >
          U
        </div>

        {showMenu && (
          <div className="absolute top-12 right-0 w-48 bg-white dark:bg-forest-900 border border-forest-100 dark:border-forest-700 rounded-xl shadow-agri-md p-2 z-50">
            <div className="p-2 border-b border-forest-100 dark:border-forest-800 mb-2">
              <div className="font-semibold text-forest-900 dark:text-forest-100">Farmer</div>
              <div className="text-xs text-forest-500 dark:text-forest-400">Settings</div>
            </div>
            <NavLink to="/profile" className="block w-full text-left px-2 py-1.5 text-sm text-forest-700 dark:text-forest-300 hover:bg-forest-50 dark:hover:bg-forest-800 rounded-lg" onClick={() => setShowMenu(false)}>Profile</NavLink>
            <NavLink to="/farm-profile" className="block w-full text-left px-2 py-1.5 text-sm text-forest-700 dark:text-forest-300 hover:bg-forest-50 dark:hover:bg-forest-800 rounded-lg" onClick={() => setShowMenu(false)}>Farm Profile</NavLink>
            <button className="w-full text-left px-2 py-1.5 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg mt-1" onClick={() => { setShowMenu(false); window.location.href='/login'; localStorage.clear(); }}>Logout</button>
          </div>
        )}
      </div>
    </header>
  )
}

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" />;
  }
  return children;
};

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [dark, setDark] = useState(false)

  const handleToggleDark = () => {
    setDark(d => !d)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <div className="flex min-h-screen bg-forest-50 dark:bg-forest-950 transition-colors duration-200">
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
            <Route path="/weather"        element={<WeatherIntelligence />} />
            <Route path="/fieldguard"     element={<FieldGuard />} />
            <Route path="/sustainability" element={<SustainabilityScore />} />
            <Route path="/assistant"      element={<FarmerAssistant />} />
            <Route path="/profile"        element={<Profile />} />
            <Route path="/farm-profile"   element={<FarmProfile />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/*" element={
            <ProtectedRoute>
              <AppContent />
            </ProtectedRoute>
          } />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
