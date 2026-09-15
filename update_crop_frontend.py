import os

frontend_code = """
import React, { useState, useEffect } from 'react'
import { Loader2, AlertTriangle, Leaf, Cloud, MapPin, ExternalLink, Activity, Info, BarChart2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, Cell } from 'recharts'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'

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

export default function CropRecommendation() {
  const { user } = useAuth()
  const [form, setForm] = useState(INITIAL)
  const [weatherSource, setWeatherSource] = useState('manual')
  const [locationStr, setLocationStr] = useState('')
  const [fetchingWeather, setFetchingWeather] = useState(false)
  const [weatherError, setWeatherError] = useState(null)
  
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [farmProfile, setFarmProfile] = useState(null)

  useEffect(() => {
    fetchFarmProfile()
  }, [])

  const fetchFarmProfile = async () => {
    try {
      const res = await api.get('/farm/')
      if (res.data.success && res.data.farm_profile) {
        setFarmProfile(res.data.farm_profile)
      }
    } catch (err) {
      console.error('Failed to fetch farm profile')
    }
  }

  const useFarmLocation = () => {
    if (farmProfile && farmProfile.location) {
      setLocationStr(farmProfile.location)
    }
  }

  const handle = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }))
  
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
          rainfall: res.data.rainfall > 0 ? res.data.rainfall : p.rainfall || 50 
        }))
        setWeatherSource('openweather')
      }
    } catch (err) {
      setWeatherError(err.response?.data?.error || 'Failed to fetch weather.')
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
    } catch (err) {
      setError(err.response?.data?.error ?? 'Failed to connect to the backend.')
    } finally { 
      setLoading(false) 
    }
  }

  const SoilStatus = ({ status, message }) => {
    if (status === 'within') return <div className="text-green-600 dark:text-green-400 text-xs font-semibold flex gap-1"><CheckCircle size={14}/> {message}</div>
    if (status === 'below') return <div className="text-amber-600 dark:text-amber-400 text-xs font-semibold flex gap-1"><AlertTriangle size={14}/> {message}</div>
    if (status === 'above') return <div className="text-red-600 dark:text-red-400 text-xs font-semibold flex gap-1"><AlertTriangle size={14}/> {message}</div>
    return null
  }

  const ImageWithFallback = ({ src, alt }) => {
    const [error, setError] = useState(false)
    if (error || !src) return (
      <div className="w-full h-48 bg-forest-100 dark:bg-forest-900/30 flex flex-col items-center justify-center text-forest-500 rounded-t-xl">
        <Leaf size={32} className="opacity-50 mb-2" />
        <span className="text-xs font-medium">Crop image unavailable</span>
      </div>
    )
    return <img src={src} alt={alt} loading="lazy" onError={() => setError(true)} className="w-full h-48 object-cover rounded-t-xl" />
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-forest-900 dark:text-forest-100 flex items-center gap-2">
            <Leaf className="text-forest-600" /> Crop Recommendation
          </h1>
          <p className="text-forest-600 dark:text-forest-400 text-sm mt-1">Enter soil and climate conditions for data-driven agronomic suggestions</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="agri-card">
            <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <Activity size={18} className="text-forest-600"/> Agronomic Inputs
            </h2>
            <form onSubmit={submit} className="space-y-4">
              
              <div className="pt-2 border-t border-forest-100 dark:border-forest-800">
                <p className="text-xs font-semibold text-forest-500 mb-3 uppercase tracking-wide">Soil Nutrients</p>
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

              <div className="pt-4 border-t border-forest-100 dark:border-forest-800">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs font-semibold text-forest-500 uppercase tracking-wide">Climate Data</p>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${weatherSource === 'openweather' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>
                    {weatherSource === 'openweather' ? 'Live Weather' : 'Manual Entry'}
                  </span>
                </div>
                
                <div className="flex gap-2 mb-3">
                  <div className="flex-1 relative">
                    <input 
                      type="text" 
                      placeholder="e.g. Pune, IN" 
                      className="agri-input w-full pr-8"
                      value={locationStr}
                      onChange={e => setLocationStr(e.target.value)}
                    />
                    {farmProfile && farmProfile.location && (
                      <button type="button" onClick={useFarmLocation} className="absolute right-2 top-2 text-forest-400 hover:text-forest-600" title="Use my farm location">
                        <MapPin size={16} />
                      </button>
                    )}
                  </div>
                  <button 
                    type="button" 
                    onClick={fetchWeather}
                    disabled={fetchingWeather}
                    className="btn-secondary whitespace-nowrap"
                  >
                    {fetchingWeather ? <Loader2 size={16} className="animate-spin" /> : <><Cloud size={16}/> Fetch</>}
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

              <button type="submit" className="btn-primary w-full justify-center mt-6" disabled={loading}>
                {loading ? <><Loader2 size={16} className="animate-spin" /> Evaluating…</> : 'Generate Recommendations'}
              </button>

              {error && (
                <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm flex gap-2 border border-red-200 dark:border-red-800 mt-4">
                  <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" /> {error}
                </div>
              )}
            </form>
          </div>
        </div>

        <div className="lg:col-span-3 space-y-6">
          {result ? (
            <>
              {/* Analytics Panel */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="agri-card border border-forest-100 dark:border-forest-800">
                  <h3 className="text-sm font-bold text-forest-900 dark:text-forest-100 mb-3 flex items-center gap-1"><BarChart2 size={16}/> Relative Suitability Score</h3>
                  <div className="h-40 w-full">
                    {result.recommendations.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={result.recommendations}>
                          <XAxis dataKey="crop" tick={{fontSize: 12}} />
                          <RechartsTooltip cursor={{fill: 'transparent'}} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                          <Bar dataKey="suitability_score" radius={[4, 4, 0, 0]}>
                            {result.recommendations.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.suitability_score >= 80 ? '#22c55e' : entry.suitability_score >= 60 ? '#3b82f6' : '#f59e0b'} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-full text-forest-400 text-sm">No crops suitable</div>
                    )}
                  </div>
                </div>
                
                <div className="agri-card border border-forest-100 dark:border-forest-800 flex flex-col justify-center">
                  <h3 className="text-sm font-bold text-forest-900 dark:text-forest-100 mb-3 flex items-center gap-1"><Info size={16}/> Data Quality</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between border-b border-forest-50 dark:border-forest-800 pb-2">
                      <span className="text-forest-600 dark:text-forest-400">Weather Status</span>
                      <span className="font-semibold">{result.data_quality?.weather_status || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between border-b border-forest-50 dark:border-forest-800 pb-2">
                      <span className="text-forest-600 dark:text-forest-400">Soil Status</span>
                      <span className="font-semibold">{result.data_quality?.soil_status || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-forest-600 dark:text-forest-400">Engine Type</span>
                      <span className="font-semibold bg-forest-100 dark:bg-forest-900/40 text-forest-700 dark:text-forest-300 px-2 rounded-md">{result.model_status === 'rule-based' ? 'Agronomic Rule-Based' : 'AI'}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendation Cards */}
              <div className="space-y-6">
                {result.recommendations.length > 0 ? result.recommendations.map((rec, idx) => (
                  <div key={rec.crop} className="agri-card p-0 overflow-hidden border border-forest-100 dark:border-forest-800 shadow-sm relative">
                    {idx === 0 && <div className="absolute top-4 right-4 bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full shadow z-10 uppercase tracking-wide">Top Match</div>}
                    
                    <ImageWithFallback src={rec.details.image_url} alt={rec.crop} />
                    
                    <div className="p-6">
                      <div className="flex items-end justify-between mb-4 border-b border-forest-50 dark:border-forest-800 pb-4">
                        <div>
                          <h3 className="text-2xl font-bold text-forest-900 dark:text-forest-100">{rec.crop}</h3>
                          <div className="text-sm font-medium text-forest-500 italic">{rec.details.scientific_name}</div>
                        </div>
                        <div className="text-right">
                          <div className={`text-3xl font-black ${rec.suitability_score >= 80 ? 'text-green-600' : rec.suitability_score >= 60 ? 'text-blue-600' : 'text-amber-500'}`}>
                            {rec.suitability_score}%
                          </div>
                          <div className="text-xs text-forest-500 uppercase tracking-wider font-semibold">Suitability Score</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div>
                          <h4 className="text-sm font-bold text-forest-900 dark:text-forest-100 mb-2 border-b border-forest-100 dark:border-forest-800 pb-1">Agronomic Profile</h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between"><span className="text-forest-500">Duration:</span> <span className="font-semibold">{rec.details.duration}</span></div>
                            <div className="flex justify-between"><span className="text-forest-500">Season:</span> <span className="font-semibold">{rec.details.season}</span></div>
                            <div className="flex justify-between"><span className="text-forest-500">Water Req:</span> <span className="font-semibold">{rec.details.water_req}</span></div>
                          </div>
                        </div>

                        <div>
                          <h4 className="text-sm font-bold text-forest-900 dark:text-forest-100 mb-2 border-b border-forest-100 dark:border-forest-800 pb-1">Soil Analysis</h4>
                          <div className="space-y-2">
                            {rec.soil_analysis && Object.entries(rec.soil_analysis).map(([key, data]) => (
                              <SoilStatus key={key} status={data.status} message={data.message} />
                            ))}
                          </div>
                        </div>
                      </div>

                      {rec.non_matching_conditions?.length > 0 && (
                        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30 rounded-xl">
                          <h4 className="text-sm font-bold text-red-800 dark:text-red-400 mb-2 flex items-center gap-1"><AlertTriangle size={16}/> Limiting Factors</h4>
                          <ul className="list-disc pl-5 text-sm text-red-700 dark:text-red-300 space-y-1">
                            {rec.non_matching_conditions.map((c, i) => <li key={i}>{c}</li>)}
                          </ul>
                        </div>
                      )}

                      {rec.details.reference_url && (
                        <a href={rec.details.reference_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 bg-blue-50 dark:bg-blue-900/20 px-4 py-2 rounded-lg transition-colors">
                          <ExternalLink size={16} /> Read Agronomic Information
                        </a>
                      )}
                    </div>
                  </div>
                )) : (
                  <div className="agri-card text-center py-12">
                    <AlertTriangle size={48} className="mx-auto text-amber-500 mb-4" />
                    <h3 className="text-xl font-bold text-forest-900 dark:text-forest-100">No Suitable Crops Found</h3>
                    <p className="text-forest-500 mt-2 max-w-md mx-auto">Based on your inputs, none of the supported crops match the minimum growing conditions. Try adjusting your inputs or checking the weather data.</p>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="agri-card h-full flex flex-col items-center justify-center text-center py-20 bg-forest-50/50 dark:bg-forest-900/10 border-dashed border-2 border-forest-200 dark:border-forest-800">
              <Leaf size={64} className="text-forest-300 dark:text-forest-700 mb-4" />
              <h3 className="text-xl font-bold text-forest-900 dark:text-forest-100 mb-2">Ready for Recommendations</h3>
              <p className="text-forest-500 max-w-sm">Enter your soil test results and fetch live weather data to generate a rule-based agronomic crop recommendation.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

import { CheckCircle } from 'lucide-react'
"""
with open('frontend/src/components/CropRecommendation.jsx', 'w', encoding='utf-8') as f:
    f.write(frontend_code)
print("CropRecommendation.jsx updated successfully.")
