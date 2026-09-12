import { useState } from 'react'
import axios from 'axios'
import { Loader2, AlertTriangle, Leaf, RefreshCw } from 'lucide-react'

const FIELDS = [
  { name: 'nitrogen',    label: 'Nitrogen (N)',    unit: 'mg/kg', type: 'number', min: 0 },
  { name: 'phosphorus',  label: 'Phosphorus (P)',  unit: 'mg/kg', type: 'number', min: 0 },
  { name: 'potassium',   label: 'Potassium (K)',   unit: 'mg/kg', type: 'number', min: 0 },
  { name: 'ph',          label: 'Soil pH',         unit: '0–14',  type: 'number', min: 0, max: 14, step: 0.1 },
  { name: 'temperature', label: 'Temperature',     unit: '°C',    type: 'number', step: 0.1 },
  { name: 'humidity',    label: 'Humidity',        unit: '%',     type: 'number', min: 0, max: 100, step: 0.1 },
  { name: 'rainfall',    label: 'Rainfall',        unit: 'mm',    type: 'number', min: 0, step: 0.1 },
]

const INITIAL = { nitrogen: '', phosphorus: '', potassium: '', ph: '', temperature: '', humidity: '', rainfall: '' }

const SCORE_COLOR = (s) => s >= 80 ? 'bg-forest-500' : s >= 60 ? 'bg-blue-500' : s >= 40 ? 'bg-harvest-500' : 'bg-red-500'

function CropRecommendation() {
  const [form, setForm]     = useState(INITIAL)
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)

  const handle = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }))
  const reset  = () => { setForm(INITIAL); setResult(null); setError(null) }

  const submit = async (e) => {
    e.preventDefault(); setLoading(true); setError(null); setResult(null)
    try {
      const r = await axios.post('http://localhost:8000/api/crops/recommend/', form)
      setResult(r.data)
    } catch (err) {
      setError(err.response?.data?.error ?? 'Failed to connect to the backend. Please ensure the Django API is running.')
    } finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Leaf size={26} className="text-forest-600" /> Crop Recommendation
          </h1>
          <p className="page-subtitle">Enter soil and climate conditions · Rule-based development prototype</p>
        </div>
        <span className="badge-proto">Rule-based Prototype</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Input form */}
        <div className="lg:col-span-2 agri-card">
          <h2 className="font-semibold text-forest-900 mb-4">Soil & Climate Inputs</h2>
          <form onSubmit={submit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              {FIELDS.slice(0, 4).map(f => (
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

            <div className="pt-1 border-t border-forest-100">
              <p className="text-xs font-semibold text-forest-500 mb-3 uppercase tracking-wide">Climate (Manual Input)</p>
              <div className="grid grid-cols-1 gap-3">
                {FIELDS.slice(4).map(f => (
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
              {loading ? <><Loader2 size={16} className="spin" /> Calculating…</> : 'Recommend Crops'}
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
          <h2 className="font-semibold text-forest-900 mb-4">Recommendations</h2>

          {!result && !loading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400">
              <Leaf size={36} className="mb-3 opacity-40" />
              <p className="text-sm">Fill in soil and climate data to receive crop recommendations.</p>
            </div>
          )}

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 py-12 text-forest-600">
              <Loader2 size={32} className="spin" />
              <span className="text-sm font-medium">Evaluating conditions…</span>
            </div>
          )}

          {result && (
            <div className="slide-up space-y-3 flex-1 flex flex-col">
              <p className="text-xs text-forest-500 mb-1">
                Showing {result.recommendations.length} recommendation(s) ranked by suitability score.
              </p>
              <div className="space-y-3 flex-1">
                {result.recommendations.map((rec, i) => (
                  <div key={i} className="rec-card">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm ${SCORE_COLOR(rec.suitability_score)}`}>
                          {i + 1}
                        </div>
                        <span className="font-bold text-forest-900 text-base">{rec.crop}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="text-xs text-forest-500">Score</div>
                        <div className="font-bold text-forest-700">{rec.suitability_score}</div>
                      </div>
                    </div>
                    {/* Score bar */}
                    <div className="h-1.5 bg-forest-100 rounded-full mb-2 overflow-hidden">
                      <div className={`h-full rounded-full ${SCORE_COLOR(rec.suitability_score)}`} style={{ width: `${rec.suitability_score}%` }} />
                    </div>
                    <p className="text-xs text-forest-600">{rec.reason}</p>
                  </div>
                ))}
              </div>

              <div className="proto-banner mt-2">
                <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                <div>
                  <strong>Rule-based Development Prototype</strong>
                  <p className="mt-0.5">{result.warning}</p>
                </div>
              </div>

              <button className="btn-secondary w-full justify-center mt-2" onClick={reset}>
                <RefreshCw size={14} /> New Recommendation
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CropRecommendation
