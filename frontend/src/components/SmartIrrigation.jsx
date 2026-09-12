import { useState } from 'react'
import axios from 'axios'
import { Loader2, AlertTriangle, Droplets, RefreshCw, CloudRain, ThermometerSun, CheckCircle } from 'lucide-react'

const PRIORITY_STYLE = {
  'No irrigation required':      'border-forest-400 bg-forest-50',
  'Monitor soil moisture':        'border-blue-300 bg-blue-50',
  'Irrigation recommended':       'border-harvest-400 bg-harvest-100',
  'Urgent irrigation recommended':'border-red-400 bg-red-50',
}

const SEVERITY_COLOR = { high: 'border-red-400', medium: 'border-harvest-400', low: 'border-blue-400' }



function SmartIrrigation() {
  const [form, setForm] = useState({ crop: '', soil_moisture: '', temperature: '', humidity: '', rainfall: '', growth_stage: '' })
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)

  const handle = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }))
  const reset  = () => { setForm({ crop: '', soil_moisture: '', temperature: '', humidity: '', rainfall: '', growth_stage: '' }); setResult(null); setError(null) }

  const submit = async (e) => {
    e.preventDefault(); setLoading(true); setError(null); setResult(null)
    try {
      const r = await axios.post('http://localhost:8000/api/irrigation/recommend/', form)
      setResult(r.data)
    } catch (err) {
      setError(err.response?.data?.error ?? 'Failed to connect to backend. Please ensure the Django API is running.')
    } finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Droplets size={26} className="text-blue-600" /> Smart Irrigation & Weather
          </h1>
          <p className="page-subtitle">Manual weather input · Rule-based prototype advisory</p>
        </div>
        <span className="badge-proto">Manual Input</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Form */}
        <div className="lg:col-span-2 agri-card">
          <h2 className="font-semibold text-forest-900 mb-4">Crop & Field Inputs</h2>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="agri-label">Crop Name</label>
              <input className="agri-input" type="text" name="crop" value={form.crop} onChange={handle} required placeholder="e.g. Wheat" />
            </div>
            <div>
              <label className="agri-label">Growth Stage</label>
              <select className="agri-select" name="growth_stage" value={form.growth_stage} onChange={handle}>
                <option value="">Select stage…</option>
                <option value="seedling">Seedling</option>
                <option value="vegetative">Vegetative</option>
                <option value="flowering">Flowering</option>
                <option value="fruiting">Fruiting / Maturation</option>
              </select>
            </div>
            <div>
              <label className="agri-label">Soil Moisture (%) <span className="normal-case font-normal text-forest-400">Optional</span></label>
              <input className="agri-input" type="number" name="soil_moisture" value={form.soil_moisture} onChange={handle} min="0" max="100" step="0.1" />
            </div>

            <div className="pt-1 border-t border-forest-100">
              <p className="text-xs font-semibold text-forest-500 mb-3 uppercase tracking-wide">Weather (Manual Override)</p>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="agri-label">Temperature (°C)</label>
                  <input className="agri-input" type="number" name="temperature" value={form.temperature} onChange={handle} required step="0.1" />
                </div>
                <div>
                  <label className="agri-label">Humidity (%)</label>
                  <input className="agri-input" type="number" name="humidity" value={form.humidity} onChange={handle} min="0" max="100" step="0.1" />
                </div>
                <div className="col-span-2">
                  <label className="agri-label">Rainfall Forecast (mm)</label>
                  <input className="agri-input" type="number" name="rainfall" value={form.rainfall} onChange={handle} required min="0" step="0.1" />
                </div>
              </div>
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

        {/* Results */}
        <div className="lg:col-span-3 agri-card flex flex-col">
          <h2 className="font-semibold text-forest-900 mb-4">Irrigation Advisory</h2>

          {!result && !loading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400">
              <Droplets size={36} className="mb-3 opacity-40" />
              <p className="text-sm">Enter crop and weather data to receive an irrigation advisory.</p>
            </div>
          )}

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 py-12 text-forest-600">
              <Loader2 size={32} className="spin" /><span className="text-sm font-medium">Processing conditions…</span>
            </div>
          )}

          {result && (
            <div className="slide-up space-y-4 flex-1 flex flex-col">
              {/* Priority card */}
              <div className={`p-4 rounded-xl border-l-4 ${PRIORITY_STYLE[result.irrigation_priority] ?? 'border-forest-300 bg-forest-50'}`}>
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle size={18} className="text-forest-600" />
                  <span className="font-bold text-forest-900">{result.irrigation_priority}</span>
                </div>
                <p className="text-sm text-forest-800 mb-1"><strong>Action:</strong> {result.recommended_action}</p>
                <p className="text-xs text-forest-600"><strong>Reason:</strong> {result.reason}</p>
              </div>

              {/* Insights */}
              {result.insights?.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-forest-600 uppercase tracking-wide">Weather & Field Insights</p>
                  {result.insights.map((ins, i) => (
                    <div key={i} className={`flex items-start gap-3 p-3 rounded-xl border-l-4 bg-white ${SEVERITY_COLOR[ins.severity] ?? 'border-forest-300'}`}>
                      {ins.type === 'weather' ? <CloudRain size={16} className="flex-shrink-0 mt-0.5" /> : <ThermometerSun size={16} className="flex-shrink-0 mt-0.5" />}
                      <div>
                        <span className="text-xs font-bold uppercase text-forest-700">{ins.severity} Alert</span>
                        <p className="text-xs text-forest-600 mt-0.5">{ins.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="proto-banner">
                <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                <div>
                  <strong>Prototype Advisory · Manual Weather Input</strong>
                  <p className="mt-0.5">{result.warning}</p>
                </div>
              </div>

              <button className="btn-secondary w-full justify-center mt-auto" onClick={reset}>
                <RefreshCw size={14} /> New Analysis
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SmartIrrigation
