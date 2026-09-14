import React, { useState, useEffect } from 'react'
import { Shield, AlertTriangle, Loader2, CheckCircle, Info, Droplets, Cloud, Thermometer, Wind, RefreshCw, History, Leaf, MapPin, Search } from 'lucide-react'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'

function FieldGuard() {
  const { user } = useAuth()
  
  const [formData, setFormData] = useState({
    crop: '',
    growth_stage: '',
    disease_scan_id: '',
    soil_moisture: '',
    weather_source: 'manual',
    temperature: '',
    humidity: '',
    rainfall: ''
  })

  const [loading, setLoading] = useState(false)
  const [weatherLoading, setWeatherLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [weatherError, setWeatherError] = useState(null)
  
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(true)
  const [diseaseScans, setDiseaseScans] = useState([])

  const defaultCity = user?.has_farm_profile ? user.farm_location : ''
  const [city, setCity] = useState(defaultCity)

  useEffect(() => {
    fetchHistory()
    fetchDiseaseScans()
  }, [])

  const fetchHistory = async () => {
    setHistoryLoading(true)
    try {
      const res = await api.get('/fieldguard/history/')
      setHistory(res.data.history || [])
    } catch (err) {
      console.error('Failed to fetch fieldguard history')
    } finally {
      setHistoryLoading(false)
    }
  }
  
  const fetchDiseaseScans = async () => {
    try {
      const res = await api.get('/disease/history/')
      setDiseaseScans(res.data.history || [])
    } catch (err) {
      console.error('Failed to fetch disease scans')
    }
  }

  const fetchWeather = async () => {
    if (!city) {
      setWeatherError('Please enter a location.')
      return
    }
    setWeatherLoading(true)
    setWeatherError(null)
    
    try {
      const res = await api.get(`/weather/current/?city=${encodeURIComponent(city)}`)
      const w = res.data
      setFormData(prev => ({
        ...prev,
        temperature: w.temperature,
        humidity: w.humidity,
        rainfall: w.rainfall || 0,
        weather_source: 'OpenWeather'
      }))
    } catch (err) {
      setWeatherError(err.response?.data?.error || 'Weather data unavailable.')
    } finally {
      setWeatherLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleReset = () => {
    setFormData({
      crop: '', growth_stage: '', disease_scan_id: '',
      soil_moisture: '', weather_source: 'manual', temperature: '', humidity: '', rainfall: ''
    })
    setResult(null)
    setError(null)
    setWeatherError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await api.post('/fieldguard/assess/', formData)
      if (response.data.success) {
        setResult(response.data)
        fetchHistory()
      } else {
        setError(response.data.error || 'Failed to calculate risk')
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to connect to backend.')
    } finally {
      setLoading(false)
    }
  }

  // Get color for category
  const getCategoryColor = (category) => {
    if (category === 'Low Risk') return 'text-green-600 bg-green-100 border-green-200 dark:bg-green-900/30 dark:border-green-800'
    if (category === 'Moderate Risk') return 'text-yellow-600 bg-yellow-100 border-yellow-200 dark:bg-yellow-900/30 dark:border-yellow-800'
    if (category === 'High Risk') return 'text-orange-600 bg-orange-100 border-orange-200 dark:bg-orange-900/30 dark:border-orange-800'
    return 'text-red-600 bg-red-100 border-red-200 dark:bg-red-900/30 dark:border-red-800'
  }

  const formatDate = (timestamp) => {
    if (!timestamp) return '--'
    return new Date(timestamp).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Shield size={28} className="text-forest-600" /> FieldGuard Risk Intelligence
          </h1>
          <p className="page-subtitle">Composite agricultural threat analysis</p>
        </div>
        <div className="flex flex-col items-end gap-1 text-xs text-forest-500 dark:text-forest-400">
            {result && (
                <>
                    <span className="flex items-center gap-1"><Info size={12}/> Rule-based Assessment</span>
                    <span>Updated: {formatDate(result.timestamp)}</span>
                </>
            )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Form */}
        <div className="lg:col-span-7 space-y-6">
          <div className="agri-card dark:bg-forest-900 dark:border-forest-800">
            <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <MapPin size={18} className="text-blue-500" /> Weather Data Source
            </h2>
            <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-end mb-4">
               <div className="flex-1 w-full">
                  <label className="agri-label dark:text-forest-400">City / Farm Location</label>
                  <div className="relative">
                    <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-forest-400" />
                    <input 
                      className="agri-input pl-9 dark:bg-forest-950 dark:border-forest-700 dark:text-white" 
                      type="text" 
                      value={city} 
                      onChange={e => setCity(e.target.value)} 
                      placeholder="e.g. Pune" 
                    />
                  </div>
                  {user?.has_farm_profile && city === user.farm_location && (
                      <p className="text-xs text-forest-500 mt-1 flex items-center gap-1">
                          <CheckCircle size={12} className="text-forest-500"/> Saved farm location
                      </p>
                  )}
               </div>
               <button type="button" onClick={fetchWeather} disabled={weatherLoading} className="btn-secondary w-full sm:w-auto h-11 flex justify-center items-center">
                  {weatherLoading ? <Loader2 size={16} className="spin" /> : <RefreshCw size={16} />}
                  <span className="ml-2">{weatherLoading ? 'Fetching...' : 'Fetch Live Weather'}</span>
               </button>
            </div>
            {weatherError && (
              <div className="error-banner mb-4">
                <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                <div className="text-sm">{weatherError}</div>
              </div>
            )}
          </div>
          
          <div className="agri-card dark:bg-forest-900 dark:border-forest-800">
            <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <AlertTriangle size={18} className="text-orange-500"/> Assessment Inputs
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="agri-label dark:text-forest-400">Crop Type</label>
                  <input type="text" name="crop" value={formData.crop} onChange={handleChange} className="agri-input dark:bg-forest-950 dark:border-forest-700 dark:text-white" placeholder="e.g. Wheat" required />
                </div>
                <div>
                  <label className="agri-label dark:text-forest-400">Growth Stage</label>
                  <select name="growth_stage" value={formData.growth_stage} onChange={handleChange} className="agri-input dark:bg-forest-950 dark:border-forest-700 dark:text-white" required>
                    <option value="">Select Stage</option>
                    <option value="seedling">Seedling</option>
                    <option value="vegetative">Vegetative</option>
                    <option value="flowering">Flowering</option>
                    <option value="fruiting">Fruiting/Grain Filling</option>
                    <option value="maturity">Maturity</option>
                  </select>
                </div>
                
                <div className="md:col-span-2">
                  <label className="agri-label dark:text-forest-400">Linked Disease Scan (Optional)</label>
                  <select name="disease_scan_id" value={formData.disease_scan_id} onChange={handleChange} className="agri-input dark:bg-forest-950 dark:border-forest-700 dark:text-white">
                    <option value="">-- No linked scan / Healthy --</option>
                    {diseaseScans.map(scan => (
                        <option key={scan.id} value={scan.id}>
                            {formatDate(scan.created_at)} - {scan.predicted_class} ({Math.round(scan.confidence * 100)}%)
                        </option>
                    ))}
                  </select>
                  {diseaseScans.length === 0 && <p className="text-xs text-forest-400 mt-1 italic">No verified disease scan available.</p>}
                </div>

                <div>
                  <label className="agri-label dark:text-forest-400 flex justify-between">
                    <span>Temperature (°C)</span>
                    {formData.weather_source === 'OpenWeather' ? <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded dark:bg-blue-900 dark:text-blue-200">OpenWeather</span> : <span className="text-[10px] bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded dark:bg-gray-800 dark:text-gray-300">Manual</span>}
                  </label>
                  <div className="relative">
                    <Thermometer size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-forest-400" />
                    <input type="number" step="0.1" name="temperature" value={formData.temperature} onChange={handleChange} className="agri-input pl-9 dark:bg-forest-950 dark:border-forest-700 dark:text-white" placeholder="25.0" required />
                  </div>
                </div>

                <div>
                  <label className="agri-label dark:text-forest-400 flex justify-between">
                    <span>Rainfall (mm)</span>
                    {formData.weather_source === 'OpenWeather' ? <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded dark:bg-blue-900 dark:text-blue-200">OpenWeather</span> : <span className="text-[10px] bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded dark:bg-gray-800 dark:text-gray-300">Manual</span>}
                  </label>
                  <div className="relative">
                    <Cloud size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-forest-400" />
                    <input type="number" step="0.1" name="rainfall" value={formData.rainfall} onChange={handleChange} className="agri-input pl-9 dark:bg-forest-950 dark:border-forest-700 dark:text-white" placeholder="10" required />
                  </div>
                </div>
                
                <div>
                  <label className="agri-label dark:text-forest-400 flex justify-between">
                    <span>Humidity (%)</span>
                    {formData.weather_source === 'OpenWeather' ? <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded dark:bg-blue-900 dark:text-blue-200">OpenWeather</span> : <span className="text-[10px] bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded dark:bg-gray-800 dark:text-gray-300">Manual</span>}
                  </label>
                  <div className="relative">
                    <Wind size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-forest-400" />
                    <input type="number" step="0.1" name="humidity" value={formData.humidity} onChange={handleChange} className="agri-input pl-9 dark:bg-forest-950 dark:border-forest-700 dark:text-white" placeholder="60" />
                  </div>
                </div>

                <div>
                  <label className="agri-label dark:text-forest-400 flex justify-between">
                    <span>Soil Moisture (%)</span>
                    <span className="text-[10px] bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded dark:bg-gray-800 dark:text-gray-300">Manual Input</span>
                  </label>
                  <div className="relative">
                    <Droplets size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-forest-400" />
                    <input type="number" step="0.1" name="soil_moisture" value={formData.soil_moisture} onChange={handleChange} className="agri-input pl-9 dark:bg-forest-950 dark:border-forest-700 dark:text-white" placeholder="45" />
                  </div>
                </div>
              </div>

              {error && (
                <div className="error-banner mt-4">
                  <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                  <div className="text-sm">{error}</div>
                </div>
              )}

              <div className="flex gap-3 pt-4 border-t border-forest-100 dark:border-forest-800">
                <button type="button" className="btn-secondary" onClick={handleReset}>Reset</button>
                <button type="submit" className="btn-primary flex-1 justify-center" disabled={loading}>
                  {loading ? <Loader2 size={16} className="spin" /> : <Shield size={16} />}
                  <span className="ml-2">{loading ? 'Evaluating Risk...' : 'Evaluate Risk Score'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Results & History Panel */}
        <div className="lg:col-span-5 space-y-6 flex flex-col">
          <div className="agri-card dark:bg-forest-900 dark:border-forest-800 flex flex-col">
            <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4">Risk Assessment Report</h2>

            {!result && !loading && (
              <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400 dark:text-forest-500">
                <Shield size={36} className="mb-3 opacity-40" />
                <p className="text-sm">Submit parameters to generate an explainable risk assessment.</p>
              </div>
            )}

            {loading && (
              <div className="flex-1 flex flex-col items-center justify-center py-12 text-forest-600 dark:text-forest-400">
                <Loader2 size={36} className="spin mb-3" />
                <p className="text-sm font-medium">Computing deterministic factors...</p>
              </div>
            )}

            {result && !loading && (
              <div className="slide-up space-y-6 flex-1">
                <div className={`p-4 rounded-xl border ${getCategoryColor(result.category)} flex flex-col items-center justify-center text-center`}>
                  <div className="text-4xl font-bold mb-1">{result.score}</div>
                  <div className="text-sm font-semibold uppercase tracking-wider">{result.category}</div>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-forest-900 dark:text-forest-100 mb-3 border-b border-forest-100 dark:border-forest-800 pb-2">Contributing Factors</h3>
                  {result.factors && result.factors.length > 0 ? (
                    <ul className="space-y-3">
                      {result.factors.map((f, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <div className={`mt-0.5 rounded-full p-0.5 ${f.impact === 'positive' ? 'text-green-500 bg-green-50 dark:bg-green-900/30' : 'text-red-500 bg-red-50 dark:bg-red-900/30'}`}>
                            {f.impact === 'positive' ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
                          </div>
                          <div>
                            <span className="font-medium text-forest-900 dark:text-forest-200 block">{f.factor}</span>
                            <span className="text-forest-600 dark:text-forest-400 text-xs">{f.description}</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-forest-500 dark:text-forest-400">No major contributing factors identified.</p>
                  )}
                </div>

                {result.preventive_actions && result.preventive_actions.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-forest-900 dark:text-forest-100 mb-2">Preventive Actions</h3>
                    <ul className="list-disc pl-5 text-sm text-forest-700 dark:text-forest-300 space-y-1">
                      {result.preventive_actions.map((action, i) => (
                        <li key={i}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="pt-4 border-t border-forest-100 dark:border-forest-800 text-xs text-forest-500 dark:text-forest-400 space-y-1">
                   <p><strong>Rule Version:</strong> {result.rule_version}</p>
                   <p><strong>Missing Data:</strong> {Object.entries(result.data_sources).filter(([_, v]) => v === 'unavailable').map(([k]) => k).join(', ') || 'None'}</p>
                   <p className="italic text-[10px] mt-2">{result.warning}</p>
                </div>
              </div>
            )}
          </div>
          
          {/* History */}
          <div className="agri-card dark:bg-forest-900 dark:border-forest-800">
             <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
                <History size={18} className="text-harvest-500" /> Assessment History
             </h2>
             {historyLoading ? (
                 <div className="flex justify-center p-4"><Loader2 className="spin text-forest-400" size={20}/></div>
             ) : history.length > 0 ? (
                 <div className="space-y-3">
                     {history.slice(0, 5).map(h => (
                         <div key={h.id} className="p-3 bg-forest-50 dark:bg-forest-950 rounded-lg border border-forest-100 dark:border-forest-800 flex justify-between items-center text-sm">
                             <div>
                                 <p className="font-medium text-forest-900 dark:text-white capitalize">{h.crop} <span className="text-xs text-forest-500 font-normal ml-1">({formatDate(h.created_at)})</span></p>
                                 <p className="text-xs text-forest-500 dark:text-forest-400">Score: {h.score}</p>
                             </div>
                             <div className={`px-2 py-1 rounded text-xs font-semibold ${
                                h.category === 'Low Risk' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
                                h.category === 'Moderate Risk' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300' :
                                h.category === 'High Risk' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300' :
                                'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                             }`}>
                                 {h.category}
                             </div>
                         </div>
                     ))}
                 </div>
             ) : (
                 <p className="text-sm text-forest-500 dark:text-forest-400 text-center py-4">No past assessments found.</p>
             )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default FieldGuard
