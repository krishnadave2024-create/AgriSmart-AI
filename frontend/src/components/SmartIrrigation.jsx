import { useState, useEffect } from 'react'
import { Loader2, AlertTriangle, Droplets, RefreshCw, CloudRain, ThermometerSun, CheckCircle, MapPin, Cloud, Info, History } from 'lucide-react'
import api from '../utils/api'

const PRIORITY_STYLE = {
  'No irrigation required':      'border-forest-400 bg-forest-50',
  'Monitor soil moisture':        'border-blue-300 bg-blue-50',
  'Irrigation recommended':       'border-harvest-400 bg-harvest-100',
  'Urgent irrigation recommended':'border-red-400 bg-red-50',
}

const SEVERITY_COLOR = { high: 'border-red-400', medium: 'border-harvest-400', low: 'border-blue-400' }

function SmartIrrigation() {
  const [form, setForm] = useState({ 
    crop: '', 
    growth_stage: '',
    field_area: '',
    irrigation_method: '',
    soil_moisture: '', 
    temperature: '', 
    humidity: '', 
    rainfall: '',
    location: ''
  })
  
  const [weatherSource, setWeatherSource] = useState('manual')
  const [loading, setLoading] = useState(false)
  const [weatherLoading, setWeatherLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [weatherError, setWeatherError] = useState(null)
  const [history, setHistory] = useState([])
  
  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const res = await api.get('/irrigation/history/')
      setHistory(res.data.history)
    } catch (err) {
      console.error('Failed to fetch irrigation history')
    }
  }

  const handle = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }))
  
  const reset = () => { 
    setForm({ crop: '', growth_stage: '', field_area: '', irrigation_method: '', soil_moisture: '', temperature: '', humidity: '', rainfall: '', location: '' })
    setWeatherSource('manual')
    setResult(null)
    setError(null) 
    setWeatherError(null)
  }

  const fetchWeather = async () => {
    if (!form.location) {
      setWeatherError('Please enter a location first.')
      return
    }
    setWeatherLoading(true)
    setWeatherError(null)
    try {
      const res = await api.get(`/weather/current/?city=${encodeURIComponent(form.location)}`)
      setForm(p => ({
        ...p,
        temperature: res.data.temperature,
        humidity: res.data.humidity,
        rainfall: res.data.rainfall
      }))
      setWeatherSource('OpenWeather API')
    } catch (err) {
      setWeatherError(err.response?.data?.error || 'Failed to fetch weather.')
      setWeatherSource('manual')
    } finally {
      setWeatherLoading(false)
    }
  }

  const submit = async (e) => {
    e.preventDefault(); 
    setLoading(true); setError(null); setResult(null)
    try {
      const payload = { ...form, weather_source: weatherSource }
      const r = await api.post('/irrigation/recommend/', payload)
      setResult(r.data)
      fetchHistory() // refresh history
    } catch (err) {
      setError(err.response?.data?.error ?? 'Failed to connect to backend.')
    } finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Droplets size={26} className="text-blue-600" /> Smart Irrigation
          </h1>
          <p className="page-subtitle">Professional rule-based agronomic advisory</p>
        </div>
        <div className="flex gap-2">
            {weatherSource === 'manual' ? (
                <span className="badge-proto border-orange-200 bg-orange-50 text-orange-700">Manual Weather</span>
            ) : (
                <span className="badge-proto border-blue-200 bg-blue-50 text-blue-700">Live Weather Active</span>
            )}
            <span className="badge-proto">No IoT Sensors</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-2 space-y-6">
            <div className="agri-card">
              <h2 className="font-semibold text-forest-900 mb-4 flex items-center gap-2">
                  <Cloud size={18} className="text-blue-500" /> Weather Data
              </h2>
              <div className="space-y-4">
                  <div>
                    <label className="agri-label">Location (City)</label>
                    <div className="flex gap-2">
                      <input className="agri-input flex-1" type="text" name="location" value={form.location} onChange={handle} placeholder="e.g. Pune" />
                      <button type="button" onClick={fetchWeather} disabled={weatherLoading} className="btn-secondary whitespace-nowrap">
                        {weatherLoading ? <Loader2 size={16} className="spin" /> : <MapPin size={16} />} Fetch
                      </button>
                    </div>
                    {weatherError && <p className="text-xs text-red-600 mt-1">{weatherError}</p>}
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="agri-label">Temp (°C)</label>
                      <input className="agri-input" type="number" name="temperature" value={form.temperature} onChange={handle} required step="0.1" />
                    </div>
                    <div>
                      <label className="agri-label">Rain (mm)</label>
                      <input className="agri-input" type="number" name="rainfall" value={form.rainfall} onChange={handle} required min="0" step="0.1" />
                    </div>
                    <div className="col-span-2">
                      <label className="agri-label">Humidity (%) <span className="normal-case font-normal text-forest-400">Optional</span></label>
                      <input className="agri-input" type="number" name="humidity" value={form.humidity} onChange={handle} min="0" max="100" step="0.1" />
                    </div>
                  </div>
              </div>
            </div>

            <div className="agri-card">
              <h2 className="font-semibold text-forest-900 mb-4 flex items-center gap-2">
                  <Droplets size={18} className="text-blue-600" /> Field & Crop
              </h2>
              <form onSubmit={submit} className="space-y-4">
                <div>
                  <label className="agri-label">Crop Name</label>
                  <select className="agri-select" name="crop" value={form.crop} onChange={handle} required>
                    <option value="">Select crop…</option>
                    <option value="wheat">Wheat</option>
                    <option value="rice">Rice</option>
                    <option value="cotton">Cotton</option>
                    <option value="maize">Maize</option>
                    <option value="millets">Millets</option>
                  </select>
                </div>
                <div>
                  <label className="agri-label">Growth Stage</label>
                  <input className="agri-input" type="text" name="growth_stage" value={form.growth_stage} onChange={handle} placeholder="e.g. Flowering" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="agri-label">Area (Acres) <span className="normal-case font-normal text-forest-400">Opt</span></label>
                        <input className="agri-input" type="number" name="field_area" value={form.field_area} onChange={handle} min="0" step="0.1" />
                    </div>
                    <div>
                        <label className="agri-label">Method <span className="normal-case font-normal text-forest-400">Opt</span></label>
                        <input className="agri-input" type="text" name="irrigation_method" value={form.irrigation_method} onChange={handle} placeholder="e.g. Drip" />
                    </div>
                </div>
                <div>
                  <label className="agri-label">Soil Moisture (%) <span className="normal-case font-normal text-forest-400">Manual Input (No Sensor)</span></label>
                  <input className="agri-input" type="number" name="soil_moisture" value={form.soil_moisture} onChange={handle} min="0" max="100" step="0.1" placeholder="Enter if known" />
                </div>

                <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
                  {loading ? <><Loader2 size={16} className="spin" /> Analysing…</> : 'Get Irrigation Insights'}
                </button>

                {error && (
                  <div className="error-banner">
                    <AlertTriangle size={16} className="flex-shrink-0" /> {error}
                  </div>
                )}
              </form>
            </div>
        </div>

        <div className="lg:col-span-3 space-y-6">
            <div className="agri-card min-h-[400px] flex flex-col">
              <h2 className="font-semibold text-forest-900 mb-4">Irrigation Advisory</h2>

              {!result && !loading && (
                <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400">
                  <Droplets size={36} className="mb-3 opacity-40" />
                  <p className="text-sm">Submit your field data to receive a rule-based irrigation recommendation.</p>
                </div>
              )}

              {loading && (
                <div className="flex-1 flex flex-col items-center justify-center gap-3 py-12 text-forest-600">
                  <Loader2 size={32} className="spin" /><span className="text-sm font-medium">Processing conditions…</span>
                </div>
              )}

              {result && (
                <div className="slide-up space-y-4 flex-1 flex flex-col">
                  <div className={`p-4 rounded-xl border-l-4 ${PRIORITY_STYLE[result.irrigation_priority] ?? 'border-forest-300 bg-forest-50'}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle size={18} className="text-forest-600" />
                      <span className="font-bold text-forest-900">{result.irrigation_priority}</span>
                    </div>
                    <p className="text-sm text-forest-800 mb-1"><strong>Action:</strong> {result.recommended_action}</p>
                    <p className="text-xs text-forest-600"><strong>Reason:</strong> {result.reason}</p>
                  </div>
                  
                  {result.crop_info && !result.crop_info.message && (
                      <div className="p-4 bg-forest-50 rounded-xl border border-forest-100">
                          <h3 className="text-sm font-bold text-forest-900 mb-2 flex items-center gap-1"><Info size={16} className="text-forest-600" /> Crop Knowledge Base</h3>
                          <ul className="text-xs text-forest-700 space-y-1">
                              <li><strong>Water Requirement:</strong> {result.crop_info.water_req}</li>
                              <li><strong>Common Method:</strong> {result.crop_info.method}</li>
                              <li><strong>Sensitive Stages:</strong> {result.crop_info.sensitive_stages.join(', ')}</li>
                          </ul>
                      </div>
                  )}
                  {result.crop_info?.message && (
                      <div className="p-4 bg-forest-50 rounded-xl border border-forest-100 text-xs text-forest-600">
                          {result.crop_info.message}
                      </div>
                  )}

                  {result.insights?.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-semibold text-forest-600 uppercase tracking-wide">Insights & Alerts</p>
                      {result.insights.map((ins, i) => (
                        <div key={i} className={`flex items-start gap-3 p-3 rounded-xl border-l-4 bg-white ${SEVERITY_COLOR[ins.severity] ?? 'border-forest-300'}`}>
                          {ins.type === 'weather' ? <CloudRain size={16} className="flex-shrink-0 mt-0.5" /> : <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />}
                          <div>
                            <span className="text-xs font-bold uppercase text-forest-700">{ins.severity} Alert</span>
                            <p className="text-xs text-forest-600 mt-0.5">{ins.message}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="proto-banner mt-auto">
                    <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                    <div>
                      <strong>Limitations</strong>
                      <p className="mt-0.5">{result.warning}</p>
                      <p className="mt-0.5">Data Sources: {weatherSource === 'manual' ? 'Manual Weather' : 'OpenWeather API'}, Manual Soil Moisture</p>
                    </div>
                  </div>

                  <button className="btn-secondary w-full justify-center mt-2" onClick={reset}>
                    <RefreshCw size={14} /> Reset Form
                  </button>
                </div>
              )}
            </div>
            
            {/* History Panel */}
            <div className="agri-card">
              <h2 className="font-semibold text-forest-900 mb-4 flex items-center gap-2">
                <History size={18} className="text-blue-500" /> Assessment History
              </h2>
              {history.length === 0 ? (
                <div className="text-center py-6 text-forest-400 text-sm">
                  No irrigation history yet.
                </div>
              ) : (
                <div className="space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                  {history.map(record => (
                    <div key={record.id} className="p-3 bg-forest-50 rounded-lg border border-forest-100 flex justify-between items-center">
                      <div>
                        <p className="text-sm font-semibold text-forest-900 capitalize">{record.crop}</p>
                        <p className="text-xs text-forest-600">{new Date(record.created_at).toLocaleDateString()} · {record.priority}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs font-medium text-forest-800">{record.temperature}°C</p>
                        <p className="text-xs text-forest-500">{record.rainfall}mm rain</p>
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

export default SmartIrrigation
