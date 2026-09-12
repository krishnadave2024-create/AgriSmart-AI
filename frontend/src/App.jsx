import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import { Moon, Sun, Home, Leaf, Droplets } from 'lucide-react'
import './App.css'

import DiseaseDetection from './components/DiseaseDetection'
import CropRecommendation from './components/CropRecommendation'
import SmartIrrigation from './components/SmartIrrigation'

function App() {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(t => t === 'light' ? 'dark' : 'light')
  }

  return (
    <Router>
      <div className="dashboard-container">
        <header>
          <div style={{display: 'flex', alignItems: 'center', gap: '2rem'}}>
            <h1>AgriSmart AI</h1>
            <nav className="main-nav">
              <NavLink to="/" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
                <Home size={18} /> Disease Detection
              </NavLink>
              <NavLink to="/crops" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
                <Leaf size={18} /> Crop Recommendation
              </NavLink>
              <NavLink to="/irrigation" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
                <Droplets size={18} /> Irrigation & Weather
              </NavLink>
            </nav>
          </div>
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
        </header>

        <Routes>
          <Route path="/" element={<DiseaseDetection />} />
          <Route path="/crops" element={<CropRecommendation />} />
          <Route path="/irrigation" element={<SmartIrrigation />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
