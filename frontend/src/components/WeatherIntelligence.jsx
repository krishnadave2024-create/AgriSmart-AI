import { useState } from 'react'
import { Cloud, ThermometerSun, AlertTriangle, RefreshCw } from 'lucide-react'

function WeatherIntelligence() {
  const [form, setForm] = useState({ temperature: '', humidity: '', rainfall: '', condition: 'sunny' })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handle = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }))
  const reset = () => { setForm({ temperature: '', humidity: '', rainfall: '', condition: 'sunny' }); setResult(null); }

  const submit = (e) => {
    e.preventDefault();
    setLoading(true);
    // Simulate processing
    setTimeout(() => {
      setResult({
        advisory: form.rainfall > 10 ? 'Heavy rainfall expected. Delay fertilizer application and check drainage.' : form.temperature > 30 ? 'High temperatures detected. Increase irrigation frequency.' : 'Optimal weather conditions for routine field operations.',
      })
      setLoading(false);
    }, 600);
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Cloud size={26} className="text-blue-500" /> Weather Intelligence
          </h1>
          <p className="page-subtitle">Manual weather input · Prototype advisory</p>
        </div>
        <span className="badge-proto">Manual Input</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-2 agri-card dark:bg-forest-900 dark:border-forest-800">
          <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4">Weather Inputs</h2>
          <form onSubmit={submit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="agri-label dark:text-forest-400">Temperature (°C)</label>
                <input className="agri-input dark:bg-forest-950 dark:border-forest-700 dark:text-white" type="number" name="temperature" value={form.temperature} onChange={handle} required step="0.1" />
              </div>
              <div>
                <label className="agri-label dark:text-forest-400">Humidity (%)</label>
                <input className="agri-input dark:bg-forest-950 dark:border-forest-700 dark:text-white" type="number" name="humidity" value={form.humidity} onChange={handle} required min="0" max="100" step="0.1" />
              </div>
              <div>
                <label className="agri-label dark:text-forest-400">Rainfall (mm)</label>
                <input className="agri-input dark:bg-forest-950 dark:border-forest-700 dark:text-white" type="number" name="rainfall" value={form.rainfall} onChange={handle} required min="0" step="0.1" />
              </div>
              <div>
                <label className="agri-label dark:text-forest-400">Condition</label>
                <select className="agri-select dark:bg-forest-950 dark:border-forest-700 dark:text-white" name="condition" value={form.condition} onChange={handle}>
                  <option value="sunny">Sunny</option>
                  <option value="cloudy">Cloudy</option>
                  <option value="rainy">Rainy</option>
                  <option value="stormy">Stormy</option>
                </select>
              </div>
            </div>

            <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
              {loading ? 'Analyzing...' : 'Get Weather Advisory'}
            </button>
            <div className="proto-banner mt-4">
              <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
              <div>
                <strong>No Live API Connected</strong>
                <p className="mt-0.5 text-xs">This page uses manual input. No real weather API is configured.</p>
              </div>
            </div>
          </form>
        </div>

        <div className="lg:col-span-3 agri-card flex flex-col dark:bg-forest-900 dark:border-forest-800">
          <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4">Weather-based Advisory</h2>

          {!result && !loading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400">
              <Cloud size={36} className="mb-3 opacity-40" />
              <p className="text-sm">Enter weather data to receive farming recommendations.</p>
            </div>
          )}

          {result && (
            <div className="slide-up space-y-4 flex-1 flex flex-col">
              <div className="p-4 rounded-xl border-l-4 border-blue-400 bg-blue-50 dark:bg-forest-950 dark:border-blue-500">
                <div className="flex items-center gap-2 mb-2">
                  <ThermometerSun size={18} className="text-blue-600 dark:text-blue-400" />
                  <span className="font-bold text-forest-900 dark:text-forest-100">Advisory</span>
                </div>
                <p className="text-sm text-forest-800 dark:text-forest-200">{result.advisory}</p>
              </div>

              <div className="proto-banner">
                <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                <div>
                  <strong>Prototype Advisory</strong>
                  <p className="mt-0.5">These recommendations are based on manual inputs for testing.</p>
                </div>
              </div>

              <button className="btn-secondary w-full justify-center mt-auto dark:bg-forest-800 dark:border-forest-700 dark:text-white dark:hover:bg-forest-700" onClick={reset}>
                <RefreshCw size={14} /> Reset Data
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default WeatherIntelligence
