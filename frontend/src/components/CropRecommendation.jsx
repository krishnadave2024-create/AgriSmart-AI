import React, { useState, useEffect } from 'react'
import { Loader2, AlertTriangle, Leaf, RefreshCw, MapPin, Cloud, Info, Clock, Droplets, Droplet, History } from 'lucide-react'
import api from '../utils/api'

const FIELDS = [
  { name: 'nitrogen',    label: 'Nitrogen (N)',    unit: 'mg/kg', type: 'number', min: 0 },
  { name: 'phosphorus',  label: 'Phosphorus (P)',  unit: 'mg/kg', type: 'number', min: 0 },
  { name: 'potassium',   label: 'Potassium (K)',   unit: 'mg/kg', type: 'number', min: 0 },
  { name: 'ph',          label: 'Soil pH',         unit: '0–14',  type: 'number', min: 0, max: 14, step: 0.1 },
]

const CLIMATE_FIELDS = [
  { name: 'temperature', label: 'Temperature',     unit: '°C',    type: 'number', step: 0.1 },
  { name: 'humidity',    label: 'Humidity',        unit: '%',     type: 'number', min: 0, max: 100, step: 0.1 },
  { name: 'rainfall',    label: 'Rainfall',        unit: 'mm',    type: 'number', min: 0, step: 0.1 },
]

const INITIAL = { nitrogen: '', phosphorus: '', potassium: '', ph: '', temperature: '', humidity: '', rainfall: '' }

const SCORE_COLOR = (s) => s >= 80 ? 'bg-forest-500' : s >= 60 ? 'bg-blue-500' : s >= 40 ? 'bg-harvest-500' : 'bg-red-500'
const SCORE_TEXT = (s) => s >= 80 ? 'text-forest-600' : s >= 60 ? 'text-blue-600' : s >= 40 ? 'text-harvest-600' : 'text-red-600'

function CropRecommendation() {
  const [form, setForm] = useState(INITIAL)
  const [weatherSource, setWeatherSource] = useState('manual')
  
  const [locationStr, setLocationStr] = useState('')
  const [fetchingWeather, setFetchingWeather] = useState(false)
  const [weatherError, setWeatherError] = useState(null)
  
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(true)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const res = await api.get('/crops/history/')
      setHistory(res.data.history)
    } catch (err) {
      console.error('Failed to fetch crop history')
    } finally {
      setHistoryLoading(false)
    }
  }

  const handle = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }))
  
  const reset = () => { 
    setForm(INITIAL)
    setResult(null)
    setError(null)
    setWeatherSource('manual')
    setWeatherError(null)
  }

  const fetchWeather = async () => {
    if (!locationStr.trim()) {
      setWeatherError('Please enter a location (city) to fetch weather.')
      return
    }
    setFetchingWeather(true)
    setWeatherError(null)
    try {
      const res = await api.get(`/weather/current/?city=${encodeURIComponent(locationStr)}`)
      if (res.data.success) {
        setForm(p => ({
          ...p,
          temperature: res.data.temperature,
          humidity: res.data.humidity,
          rainfall: res.data.rainfall > 0 ? res.data.rainfall : p.rainfall || 50 // simplistic fallback if 0 rain rn
        }))
        setWeatherSource('openweather')
      }
    } catch (err) {
      if (err.response?.status === 503) {
        setWeatherError('OpenWeather API key not configured. Please use manual input.')
      } else {
        setWeatherError(err.response?.data?.error || 'Failed to fetch weather.')
      }
      setWeatherSource('manual')
    } finally {
      setFetchingWeather(false)
    }
  }

  const submit = async (e) => {
    e.preventDefault(); 
    setLoading(true); 
    setError(null); 
    setResult(null);
    try {
      const payload = { ...form, weather_source: weatherSource }
      const r = await api.post('/crops/recommend/', payload)
      setResult(r.data)
      fetchHistory() // refresh history
    } catch (err) {
      setError(err.response?.data?.error ?? 'Failed to connect to the backend.')
    } finally { 
      setLoading(false) 
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Leaf size={26} className="text-forest-600" /> Crop Recommendation
          </h1>
          <p className="page-subtitle">Enter soil and climate conditions for data-driven agronomic suggestions</p>
        </div>
        <span className="badge-proto">Rule-based Engine</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Input form */}
        <div className="lg:col-span-2 space-y-6">
          <div className="agri-card">
            <h2 className="font-semibold text-forest-900 mb-4">Inputs</h2>
            <form onSubmit={submit} className="space-y-4">
              
              <div className="pt-1 border-t border-forest-100">
                <p className="text-xs font-semibold text-forest-500 mb-3 uppercase tracking-wide">Soil Nutrients (NPK & pH)</p>
                <div className="grid grid-cols-2 gap-3">
                  {FIELDS.map(f => (
                    <div key={f.name}>
                      <label className="agri-label">{f.label} <span className="normal-case font-normal text-forest-400">({f.unit})</span></label>
                      <input
                        className="agri-input" type={f.type} name={f.name}
                        value={form[f.name]} onChange={handle}
                        required min={f.min} max={f.max} step={f.step ?? 1}
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 border-t border-forest-100">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs font-semibold text-forest-500 uppercase tracking-wide">Climate Data</p>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${weatherSource === 'openweather' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>
                    {weatherSource === 'openweather' ? 'Auto (OpenWeather)' : 'Manual Entry'}
                  </span>
                </div>
                
                <div className="flex gap-2 mb-3">
                  <input 
                    type="text" 
                    placeholder="e.g. Pune, IN" 
                    className="agri-input flex-1"
                    value={locationStr}
                    onChange={e => setLocationStr(e.target.value)}
                  />
                  <button 
                    type="button" 
                    onClick={fetchWeather}
                    disabled={fetchingWeather}
                    className="btn-secondary whitespace-nowrap"
                  >
                    {fetchingWeather ? <Loader2 size={16} className="spin" /> : <><Cloud size={16}/> Fetch</>}
                  </button>
                </div>
                {weatherError && <div className="text-xs text-red-500 mb-3 flex items-start gap-1"><AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />{weatherError}</div>}

                <div className="grid grid-cols-2 gap-3">
                  {CLIMATE_FIELDS.map(f => (
                    <div key={f.name}>
                      <label className="agri-label">{f.label} <span className="normal-case font-normal text-forest-400">({f.unit})</span></label>
                      <input
                        className="agri-input" type={f.type} name={f.name}
                        value={form[f.name]} onChange={handle}
                        required min={f.min} max={f.max} step={f.step ?? 1}
                      />
                    </div>
                  ))}
                </div>
              </div>

              <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
                {loading ? <><Loader2 size={16} className="spin" /> Evaluating…</> : 'Generate Recommendations'}
              </button>

              {error && (
                <div className="error-banner">
                  <AlertTriangle size={16} className="flex-shrink-0" /> {error}
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Results */}
        <div className="lg:col-span-3 space-y-6">
          <div className="agri-card min-h-[400px] flex flex-col">
            <h2 className="font-semibold text-forest-900 mb-4">Recommendation Report</h2>

            {!result && !loading && (
              <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400">
                <Leaf size={36} className="mb-3 opacity-40" />
                <p className="text-sm">Submit your soil and climate data to generate an agronomic recommendation.</p>
              </div>
            )}

            {loading && (
              <div className="flex-1 flex flex-col items-center justify-center gap-3 py-12 text-forest-600">
                <Loader2 size={32} className="spin" />
                <span className="text-sm font-medium">Analyzing agronomic data against knowledge base…</span>
              </div>
            )}

            {result && (
              <div className="slide-up space-y-4 flex-1">
                {result.deficiencies && result.deficiencies.length > 0 && (
                  <div className="bg-harvest-50 text-harvest-800 p-3 rounded-lg border border-harvest-200 text-sm">
                    <div className="font-bold mb-1 flex items-center gap-1"><AlertTriangle size={16}/> Soil Analysis Warnings</div>
                    <ul className="list-disc pl-5 space-y-1">
                      {result.deficiencies.map((d, i) => <li key={i}>{d}</li>)}
                    </ul>
                  </div>
                )}
                
                {result.recommendations.length === 0 ? (
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg text-center text-gray-500">
                    <p>No highly suitable crops found for these conditions in our database.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {result.recommendations.map((rec, i) => (
                      <div key={i} className="border border-forest-100 rounded-xl overflow-hidden shadow-sm bg-white">
                        <div className="flex items-center justify-between bg-forest-50 p-3 border-b border-forest-100">
                          <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-lg ${SCORE_COLOR(rec.suitability_score)}`}>
                              #{i + 1}
                            </div>
                            <div>
                              <h3 className="font-bold text-forest-900 text-lg">{rec.crop}</h3>
                              <span className="text-xs text-forest-500 italic">{rec.details.scientific_name}</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xs text-forest-500 uppercase tracking-wide font-semibold">Suitability</div>
                            <div className={`font-black text-xl ${SCORE_TEXT(rec.suitability_score)}`}>{rec.suitability_score}%</div>
                          </div>
                        </div>
                        
                        <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* Image and Info */}
                          <div>
                            {rec.details.image_url ? (
                              <img src={rec.details.image_url} alt={rec.crop} className="w-full h-32 object-cover rounded-lg mb-3 shadow-inner" />
                            ) : (
                              <div className="w-full h-32 bg-gray-100 rounded-lg mb-3 flex items-center justify-center text-gray-400">No image available</div>
                            )}
                            <div className="space-y-1.5 text-sm">
                              <div className="flex items-center gap-2"><Clock size={14} className="text-forest-400"/> <span className="text-forest-700 font-medium">Duration:</span> {rec.details.duration}</div>
                              <div className="flex items-center gap-2"><MapPin size={14} className="text-forest-400"/> <span className="text-forest-700 font-medium">Season:</span> {rec.details.season}</div>
                              <div className="flex items-center gap-2"><Droplet size={14} className="text-forest-400"/> <span className="text-forest-700 font-medium">Water Req:</span> {rec.details.water_req}</div>
                            </div>
                          </div>
                          
                          {/* Reasoning */}
                          <div className="space-y-3 text-sm">
                            <div>
                              <h4 className="font-bold text-forest-800 text-xs uppercase mb-1">Advantages</h4>
                              <p className="text-gray-600 leading-tight">{rec.details.advantages}</p>
                            </div>
                            <div>
                              <h4 className="font-bold text-forest-800 text-xs uppercase mb-1">Nutrient Needs</h4>
                              <p className="text-gray-600 leading-tight">{rec.details.nutrient_req}</p>
                            </div>
                            {rec.non_matching_conditions.length > 0 && (
                              <div className="bg-red-50 p-2 rounded border border-red-100">
                                <h4 className="font-bold text-red-800 text-[11px] uppercase mb-1">Suboptimal Conditions</h4>
                                <ul className="list-disc pl-4 text-xs text-red-700 space-y-0.5">
                                  {rec.non_matching_conditions.map((c, j) => <li key={j}>{c}</li>)}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div className="proto-banner mt-4">
                  <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                  <div>
                    <strong>{result.warning}</strong>
                    <p className="mt-0.5 text-xs opacity-90">Method: Rule-based. Model Status: {result.model_status}</p>
                  </div>
                </div>

                <button className="btn-secondary w-full justify-center mt-2" onClick={reset}>
                  <RefreshCw size={14} /> Run Another Analysis
                </button>
              </div>
            )}
          </div>

          {/* History Panel */}
          <div className="agri-card">
            <h2 className="font-semibold text-forest-900 flex items-center gap-2 mb-4">
              <History size={18} className="text-forest-500" /> Recent Recommendations
            </h2>
            {historyLoading ? (
               <div className="flex items-center justify-center py-6 text-forest-400"><Loader2 size={24} className="spin" /></div>
            ) : history.length === 0 ? (
               <p className="text-sm text-gray-500 text-center py-4">No previous recommendations found.</p>
            ) : (
               <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                 {history.map(item => (
                   <div key={item.id} className="p-3 border border-forest-100 rounded-lg bg-forest-50/30 flex justify-between items-center">
                     <div>
                       <div className="font-bold text-forest-800">{item.top_recommendation || 'None'}</div>
                       <div className="text-[11px] text-forest-500 flex items-center gap-1">
                         <MapPin size={10}/> N:{item.nitrogen} P:{item.phosphorus} K:{item.potassium}
                       </div>
                       <div className="text-[11px] text-forest-500 flex items-center gap-1">
                         <Cloud size={10}/> {item.temperature}°C ({item.weather_source})
                       </div>
                     </div>
                     <div className="text-[10px] text-forest-400 bg-white px-2 py-1 rounded border border-forest-100">
                       {new Date(item.created_at).toLocaleDateString()}
                     </div>
                   </div>
                 ))}
               </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CropRecommendation
