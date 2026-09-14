import { useState } from 'react'
import axios from 'axios'
import { Shield, AlertTriangle, Loader2, CheckCircle, Info, Droplets, Cloud, Thermometer, Wind } from 'lucide-react'

function FieldGuard() {
  const [formData, setFormData] = useState({
    crop: '',
    growth_stage: '',
    disease_label: '',
    disease_confidence: '',
    soil_moisture: '',
    rainfall: '',
    temperature: '',
    humidity: '',
    sustainability_score: ''
  })

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleReset = () => {
    setFormData({
      crop: '', growth_stage: '', disease_label: '', disease_confidence: '',
      soil_moisture: '', rainfall: '', temperature: '', humidity: '', sustainability_score: ''
    })
    setResult(null)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post('http://localhost:8000/api/fieldguard/assess/', formData)
      if (response.data.success) {
        setResult(response.data)
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
    if (category === 'Low Risk') return 'text-green-600 bg-green-100 border-green-200'
    if (category === 'Moderate Risk') return 'text-yellow-600 bg-yellow-100 border-yellow-200'
    if (category === 'High Risk') return 'text-orange-600 bg-orange-100 border-orange-200'
    return 'text-red-600 bg-red-100 border-red-200'
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

      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Form */}
        <div className="lg:col-span-7 agri-card">
          <h2 className="font-semibold text-forest-900 mb-4 flex items-center gap-2">
            <AlertTriangle size={18} /> Manual Assessment Inputs
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

              <div className="input-group">
                <label className="input-label">Crop Type</label>
                <input type="text" name="crop" value={formData.crop} onChange={handleChange} className="input-field" placeholder="e.g. Wheat" />
              </div>

              <div className="input-group">
                <label className="input-label">Growth Stage</label>
                <input type="text" name="growth_stage" value={formData.growth_stage} onChange={handleChange} className="input-field" placeholder="e.g. Vegetative" />
              </div>

              <div className="input-group">
                <label className="input-label flex justify-between">
                  <span>Temperature (°C)</span>
                  <span className="badge-proto text-[10px] py-0">Manual</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-forest-400">
                    <Thermometer size={16} />
                  </div>
                  <input type="number" step="0.1" name="temperature" value={formData.temperature} onChange={handleChange} className="input-field pl-9" placeholder="25.0" />
                </div>
              </div>

              <div className="input-group">
                <label className="input-label flex justify-between">
                  <span>Humidity (%)</span>
                  <span className="badge-proto text-[10px] py-0">Manual</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-forest-400">
                    <Wind size={16} />
                  </div>
                  <input type="number" step="0.1" name="humidity" value={formData.humidity} onChange={handleChange} className="input-field pl-9" placeholder="60" />
                </div>
              </div>

              <div className="input-group">
                <label className="input-label flex justify-between">
                  <span>Rainfall (mm)</span>
                  <span className="badge-proto text-[10px] py-0">Manual</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-forest-400">
                    <Cloud size={16} />
                  </div>
                  <input type="number" step="0.1" name="rainfall" value={formData.rainfall} onChange={handleChange} className="input-field pl-9" placeholder="10" />
                </div>
              </div>

              <div className="input-group">
                <label className="input-label flex justify-between">
                  <span>Soil Moisture (%)</span>
                  <span className="badge-proto text-[10px] py-0">Manual</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-forest-400">
                    <Droplets size={16} />
                  </div>
                  <input type="number" step="0.1" name="soil_moisture" value={formData.soil_moisture} onChange={handleChange} className="input-field pl-9" placeholder="45" />
                </div>
              </div>

              <div className="input-group">
                <label className="input-label">Disease Label (if any)</label>
                <input type="text" name="disease_label" value={formData.disease_label} onChange={handleChange} className="input-field" placeholder="e.g. Rust" />
              </div>

              <div className="input-group">
                <label className="input-label flex justify-between">
                  <span>Disease Confidence (0-1)</span>
                  <span className="badge-proto text-[10px] py-0">Manual</span>
                </label>
                <input type="number" step="0.01" max="1" min="0" name="disease_confidence" value={formData.disease_confidence} onChange={handleChange} className="input-field" placeholder="0.85" />
              </div>

            </div>

            {error && (
              <div className="error-banner mt-4">
                <AlertTriangle size={16} className="flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="flex gap-3 pt-4 border-t border-forest-100">
              <button type="button" className="btn-secondary" onClick={handleReset}>Reset</button>
              <button type="submit" className="btn-primary flex-1 justify-center" disabled={loading}>
                {loading ? <Loader2 size={16} className="spin" /> : <Shield size={16} />}
                {loading ? 'Evaluating Risk...' : 'Evaluate Risk Score'}
              </button>
            </div>
          </form>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-5 agri-card flex flex-col h-full">
          <h2 className="font-semibold text-forest-900 mb-4">Risk Assessment Report</h2>

          {!result && !loading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400">
              <Shield size={36} className="mb-3 opacity-40" />
              <p className="text-sm">Submit the parameters to generate a risk assessment.</p>
            </div>
          )}

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center py-12 text-forest-600">
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
                <h3 className="text-sm font-semibold text-forest-900 mb-3 border-b border-forest-100 pb-2">Contributing Factors</h3>
                {result.factors && result.factors.length > 0 ? (
                  <ul className="space-y-3">
                    {result.factors.map((f, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <div className={`mt-0.5 rounded-full p-0.5 ${f.impact === 'positive' ? 'text-green-500 bg-green-50' : 'text-red-500 bg-red-50'}`}>
                          {f.impact === 'positive' ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
                        </div>
                        <div>
                          <span className="font-medium text-forest-900 block">{f.factor}</span>
                          <span className="text-forest-600 text-xs">{f.description}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-forest-500">No major contributing factors identified.</p>
                )}
              </div>

              {result.preventive_actions && result.preventive_actions.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-forest-900 mb-2">Preventive Actions</h3>
                  <ul className="list-disc pl-5 text-sm text-forest-700 space-y-1">
                    {result.preventive_actions.map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FieldGuard
