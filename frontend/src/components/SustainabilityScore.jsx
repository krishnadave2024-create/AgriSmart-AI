import { useState } from 'react'
import axios from 'axios'
import { Loader2, AlertTriangle, Globe, RefreshCw, CheckCircle2 } from 'lucide-react'

const PRACTICES = [
  { name: 'crop_rotation',          label: 'I practice crop rotation',                               desc: '+20 pts' },
  { name: 'organic_fertilizer',     label: 'I use organic fertilizers',                              desc: '+20 pts' },
  { name: 'rainwater_harvesting',   label: 'I harvest rainwater',                                    desc: '+20 pts' },
  { name: 'soil_conservation',      label: 'I use soil conservation techniques (e.g. min. tillage)', desc: '+20 pts' },
  { name: 'crop_residue_management',label: 'I compost or incorporate crop residue (no burning)',     desc: '+20 pts' },
]

const SCORE_RING_COLOR = (s) =>
  s >= 80 ? { ring: 'border-forest-500', text: 'text-forest-700', bg: 'bg-forest-50' }
: s >= 60 ? { ring: 'border-blue-400',   text: 'text-blue-700',   bg: 'bg-blue-50' }
: s >= 40 ? { ring: 'border-harvest-500',text: 'text-harvest-600',bg: 'bg-harvest-50' }
:           { ring: 'border-red-400',     text: 'text-red-700',    bg: 'bg-red-50' }

function SustainabilityScore() {
  const [form, setForm] = useState({
    crop_rotation: false, organic_fertilizer: false, rainwater_harvesting: false,
    soil_conservation: false, crop_residue_management: false,
    chemical_fertilizer_level: 'medium', pesticide_level: 'medium',
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)

  const handle = (e) => {
    const { name, type, checked, value } = e.target
    setForm(p => ({ ...p, [name]: type === 'checkbox' ? checked : value }))
  }

  const reset  = () => {
    setForm({ crop_rotation: false, organic_fertilizer: false, rainwater_harvesting: false, soil_conservation: false, crop_residue_management: false, chemical_fertilizer_level: 'medium', pesticide_level: 'medium' })
    setResult(null); setError(null)
  }

  const submit = async (e) => {
    e.preventDefault(); setLoading(true); setError(null); setResult(null)
    try {
      const r = await axios.post('http://localhost:8000/api/sustainability/score/', form)
      setResult(r.data)
    } catch (err) {
      setError(err.response?.data?.error ?? 'Failed to connect to backend. Please ensure the Django API is running.')
    } finally { setLoading(false) }
  }

  const scoreColors = result ? SCORE_RING_COLOR(result.score) : null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Globe size={26} className="text-emerald-600" /> Sustainability Score
          </h1>
          <p className="page-subtitle">Explainable rule-based farming sustainability assessment</p>
        </div>
        <span className="badge-proto">Prototype Assessment</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Form */}
        <div className="lg:col-span-3 agri-card">
          <h2 className="font-semibold text-forest-900 mb-4">Farming Practices Assessment</h2>
          <form onSubmit={submit} className="space-y-5">

            <div className="space-y-3">
              <p className="text-xs font-semibold text-forest-500 uppercase tracking-wide">Sustainable Practices (each +20 pts)</p>
              {PRACTICES.map(p => (
                <label
                  key={p.name}
                  className="flex items-center gap-3 p-3 rounded-xl border border-forest-100 hover:bg-forest-50 cursor-pointer transition-colors"
                >
                  <input
                    type="checkbox" name={p.name} checked={form[p.name]} onChange={handle}
                    className="w-4 h-4 accent-forest-600 flex-shrink-0"
                  />
                  <span className="flex-1 text-sm text-forest-800">{p.label}</span>
                  <span className="text-xs text-forest-400 font-medium">{p.desc}</span>
                </label>
              ))}
            </div>

            <div className="border-t border-forest-100 pt-4">
              <p className="text-xs font-semibold text-forest-500 uppercase tracking-wide mb-3">Chemical Usage (penalties apply)</p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="agri-label">Chemical Fertilizer Level</label>
                  <select className="agri-select" name="chemical_fertilizer_level" value={form.chemical_fertilizer_level} onChange={handle}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High (−10 pts)</option>
                  </select>
                </div>
                <div>
                  <label className="agri-label">Pesticide Level</label>
                  <select className="agri-select" name="pesticide_level" value={form.pesticide_level} onChange={handle}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High (−10 pts)</option>
                  </select>
                </div>
              </div>
            </div>

            <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
              {loading ? <><Loader2 size={16} className="spin" /> Calculating…</> : 'Calculate Sustainability Score'}
            </button>

            {error && (
              <div className="error-banner">
                <AlertTriangle size={16} className="flex-shrink-0" /> {error}
              </div>
            )}
          </form>
        </div>

        {/* Results */}
        <div className="lg:col-span-2 agri-card flex flex-col">
          <h2 className="font-semibold text-forest-900 mb-4">Your Score</h2>

          {!result && !loading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400">
              <Globe size={36} className="mb-3 opacity-40" />
              <p className="text-sm">Select your practices to calculate a sustainability score.</p>
            </div>
          )}

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 py-12 text-forest-600">
              <Loader2 size={32} className="spin" /><span className="text-sm font-medium">Calculating…</span>
            </div>
          )}

          {result && scoreColors && (
            <div className="slide-up space-y-4 flex-1 flex flex-col">
              {/* Score ring */}
              <div className={`flex flex-col items-center justify-center py-6 rounded-2xl ${scoreColors.bg}`}>
                <div className={`w-28 h-28 rounded-full border-[6px] ${scoreColors.ring} flex items-center justify-center mb-3`}>
                  <span className={`text-4xl font-extrabold ${scoreColors.text}`}>{result.score}</span>
                </div>
                <span className={`text-lg font-bold ${scoreColors.text}`}>{result.category}</span>
                <span className="text-xs text-forest-500 mt-1">out of 100</span>
              </div>

              {/* Positive factors */}
              {result.positive_factors.length > 0 && (
                <div className="bg-forest-50 rounded-xl p-4">
                  <h3 className="text-xs font-bold uppercase tracking-wide text-forest-600 mb-2 flex items-center gap-1">
                    <CheckCircle2 size={14} /> Positive Factors
                  </h3>
                  <ul className="space-y-1.5">
                    {result.positive_factors.map((f, i) => (
                      <li key={i} className="text-xs text-forest-700 flex items-start gap-1.5">
                        <span className="text-forest-500 mt-0.5">✓</span> {f}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Improvements */}
              {result.improvement_suggestions.length > 0 && (
                <div className="bg-harvest-100 rounded-xl p-4">
                  <h3 className="text-xs font-bold uppercase tracking-wide text-harvest-600 mb-2 flex items-center gap-1">
                    <AlertTriangle size={14} /> Areas to Improve
                  </h3>
                  <ul className="space-y-1.5">
                    {result.improvement_suggestions.map((s, i) => (
                      <li key={i} className="text-xs text-harvest-700 flex items-start gap-1.5">
                        <span className="mt-0.5">→</span> {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="proto-banner">
                <AlertTriangle size={14} className="flex-shrink-0 mt-0.5" />
                <div>
                  <strong>Prototype Score</strong>
                  <p className="mt-0.5">{result.warning}</p>
                </div>
              </div>

              <button className="btn-secondary w-full justify-center mt-auto" onClick={reset}>
                <RefreshCw size={14} /> Re-Calculate
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SustainabilityScore
