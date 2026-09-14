import React, { useState, useEffect } from 'react'
import { Globe, Shield, RefreshCw, AlertTriangle, Loader2, CheckCircle, Leaf, History, Droplets, Zap, DollarSign, Sprout } from 'lucide-react'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'

const PRACTICES = [
  { name: 'crop_rotation',          label: 'Crop Rotation' },
  { name: 'organic_fertilizer',     label: 'Organic Fertilizers' },
  { name: 'rainwater_harvesting',   label: 'Rainwater Harvesting' },
  { name: 'soil_conservation',      label: 'Soil Conservation (e.g. min. tillage)' },
  { name: 'crop_residue_management',label: 'Crop Residue Management (no burning)' },
]

function SustainabilityScore() {
  const { user } = useAuth()
  
  const [form, setForm] = useState({
    crop_rotation: 'unknown', 
    organic_fertilizer: 'unknown', 
    rainwater_harvesting: 'unknown',
    soil_conservation: 'unknown', 
    crop_residue_management: 'unknown',
    chemical_fertilizer_level: 'unknown', 
    pesticide_level: 'unknown',
  })
  
  const [loading, setLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [activityCounts, setActivityCounts] = useState({})

  useEffect(() => {
    fetchHistory()
    fetchDashboardCounts()
  }, [])

  const fetchHistory = async () => {
    setHistoryLoading(true)
    try {
      const res = await api.get('/sustainability/history/')
      setHistory(res.data.history || [])
      // If we have history, pre-fill form with the latest known inputs
      if (res.data.history && res.data.history.length > 0) {
          // Since history from backend doesn't contain full inputs, we might just load it from a summary
          // Wait, the API GET doesn't return full input_values in the current implementation, it only returns a summary
      }
    } catch (err) {
      console.error('Failed to fetch sustainability history')
    } finally {
      setHistoryLoading(false)
    }
  }
  
  const fetchDashboardCounts = async () => {
      try {
          const res = await api.get('/dashboard/summary/')
          if (res.data) {
              setActivityCounts({
                  'IrrigationAssessment': res.data.total_irrigation_assessments || 0,
                  'FieldGuardAssessment': res.data.total_fieldguard_assessments || 0,
                  'CropRecommendation': res.data.total_crop_recommendations || 0
              })
          }
      } catch (err) {
          console.error(err)
      }
  }

  const handle = (e) => {
    const { name, value } = e.target
    setForm(p => ({ ...p, [name]: value }))
  }

  const reset  = () => {
    setForm({ crop_rotation: 'unknown', organic_fertilizer: 'unknown', rainwater_harvesting: 'unknown', soil_conservation: 'unknown', crop_residue_management: 'unknown', chemical_fertilizer_level: 'unknown', pesticide_level: 'unknown' })
    setResult(null); setError(null)
  }

  const submit = async (e) => {
    e.preventDefault(); setLoading(true); setError(null); setResult(null)
    try {
      const r = await api.post('/sustainability/score/', form)
      if (r.data.success) {
          setResult(r.data)
          fetchHistory()
      } else {
          setError(r.data.error || 'Failed to calculate.')
      }
    } catch (err) {
      setError(err.response?.data?.error ?? 'Failed to connect to backend.')
    } finally { setLoading(false) }
  }

  const getCategoryColor = (category) => {
    if (category === 'Excellent') return 'text-green-600 bg-green-100 border-green-200 dark:bg-green-900/30 dark:border-green-800'
    if (category === 'Good') return 'text-emerald-600 bg-emerald-100 border-emerald-200 dark:bg-emerald-900/30 dark:border-emerald-800'
    if (category === 'Developing') return 'text-yellow-600 bg-yellow-100 border-yellow-200 dark:bg-yellow-900/30 dark:border-yellow-800'
    return 'text-red-600 bg-red-100 border-red-200 dark:bg-red-900/30 dark:border-red-800'
  }
  
  const getCategoryRing = (category) => {
    if (category === 'Excellent') return 'border-green-500 text-green-600'
    if (category === 'Good') return 'border-emerald-500 text-emerald-600'
    if (category === 'Developing') return 'border-yellow-500 text-yellow-600'
    return 'border-red-500 text-red-600'
  }

  const formatDate = (timestamp) => {
    if (!timestamp) return '--'
    return new Date(timestamp).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Globe size={28} className="text-emerald-600" /> Sustainability Profile
          </h1>
          <p className="page-subtitle">Database-backed environmental impact assessment</p>
        </div>
        <div className="flex flex-col items-end gap-1 text-xs text-forest-500 dark:text-forest-400">
            {result && (
                <>
                    <span className="flex items-center gap-1"><Shield size={12}/> {result.calculation_method}</span>
                    <span>Updated: {formatDate(result.timestamp)}</span>
                </>
            )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form and Evidence */}
        <div className="lg:col-span-7 space-y-6">
        
          <div className="agri-card dark:bg-forest-900 dark:border-forest-800 flex justify-around p-4 text-center">
             <div>
                <p className="text-xl font-bold text-forest-900 dark:text-white">{activityCounts['IrrigationAssessment'] || 0}</p>
                <p className="text-xs text-forest-500 uppercase tracking-wide">Irrigation Records</p>
             </div>
             <div>
                <p className="text-xl font-bold text-forest-900 dark:text-white">{activityCounts['FieldGuardAssessment'] || 0}</p>
                <p className="text-xs text-forest-500 uppercase tracking-wide">FieldGuard Scans</p>
             </div>
             <div>
                <p className="text-xl font-bold text-forest-900 dark:text-white">{activityCounts['CropRecommendation'] || 0}</p>
                <p className="text-xs text-forest-500 uppercase tracking-wide">Crop Recs</p>
             </div>
          </div>
          
          <div className="agri-card dark:bg-forest-900 dark:border-forest-800">
            <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <Sprout size={18} className="text-emerald-500" /> Farming Practices Validation
            </h2>
            <p className="text-sm text-forest-600 dark:text-forest-400 mb-6">
              Your sustainability score aggregates available authenticated data (like your Farm Profile area and smart irrigation recommendations) with manual practice inputs below.
            </p>
            
            <form onSubmit={submit} className="space-y-5">

              <div className="space-y-4">
                <p className="text-xs font-semibold text-forest-500 uppercase tracking-wide border-b border-forest-100 dark:border-forest-800 pb-2">Sustainable Practices</p>
                
                {PRACTICES.map(p => (
                  <div key={p.name} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <span className="text-sm text-forest-800 dark:text-forest-200 font-medium">{p.label}</span>
                    <select 
                        name={p.name} 
                        value={form[p.name]} 
                        onChange={handle}
                        className="agri-select w-full sm:w-48 dark:bg-forest-950 dark:border-forest-700 dark:text-white"
                    >
                        <option value="unknown">Unknown / Not provided</option>
                        <option value="yes">Yes</option>
                        <option value="no">No</option>
                    </select>
                  </div>
                ))}
              </div>

              <div className="space-y-4 mt-6">
                <p className="text-xs font-semibold text-forest-500 uppercase tracking-wide border-b border-forest-100 dark:border-forest-800 pb-2">Chemical Usage</p>
                
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <span className="text-sm text-forest-800 dark:text-forest-200 font-medium">Chemical Fertilizer Level</span>
                  <select className="agri-select w-full sm:w-48 dark:bg-forest-950 dark:border-forest-700 dark:text-white" name="chemical_fertilizer_level" value={form.chemical_fertilizer_level} onChange={handle}>
                    <option value="unknown">Unknown / Not provided</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <span className="text-sm text-forest-800 dark:text-forest-200 font-medium">Pesticide Level</span>
                  <select className="agri-select w-full sm:w-48 dark:bg-forest-950 dark:border-forest-700 dark:text-white" name="pesticide_level" value={form.pesticide_level} onChange={handle}>
                    <option value="unknown">Unknown / Not provided</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3 pt-6">
                <button type="button" className="btn-secondary" onClick={reset}>Reset</button>
                <button type="submit" className="btn-primary flex-1 justify-center" disabled={loading}>
                  {loading ? <Loader2 size={16} className="spin" /> : <RefreshCw size={16} />}
                  <span className="ml-2">{loading ? 'Calculating...' : 'Evaluate Sustainability'}</span>
                </button>
              </div>

              {error && (
                <div className="error-banner">
                  <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" /> <div>{error}</div>
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Results & History Panel */}
        <div className="lg:col-span-5 space-y-6 flex flex-col">
          <div className="agri-card dark:bg-forest-900 dark:border-forest-800 flex flex-col">
            <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4">Sustainability Overview</h2>

            {!result && !loading && (
              <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400 dark:text-forest-500">
                <Globe size={36} className="mb-3 opacity-40" />
                <p className="text-sm">Submit your practices to calculate an explainable sustainability score.</p>
              </div>
            )}

            {loading && (
              <div className="flex-1 flex flex-col items-center justify-center py-12 text-forest-600 dark:text-forest-400">
                <Loader2 size={36} className="spin mb-3" />
                <p className="text-sm font-medium">Aggregating database context...</p>
              </div>
            )}

            {result && !loading && (
              <div className="slide-up space-y-6 flex-1">
                {/* Score */}
                <div className="flex flex-col items-center justify-center py-4">
                  <div className={`w-28 h-28 rounded-full border-[6px] ${getCategoryRing(result.category)} flex items-center justify-center mb-3 bg-white dark:bg-forest-950 shadow-inner`}>
                    <span className="text-4xl font-extrabold">{result.score}</span>
                  </div>
                  <span className={`text-lg font-bold px-3 py-1 rounded-full text-white ${result.category === 'Excellent' ? 'bg-green-500' : result.category === 'Good' ? 'bg-emerald-500' : result.category === 'Developing' ? 'bg-yellow-500' : 'bg-red-500'}`}>{result.category}</span>
                </div>
                
                {/* Savings Estimates */}
                <div>
                   <h3 className="text-xs font-semibold text-forest-900 dark:text-forest-100 uppercase tracking-wide mb-3 border-b border-forest-100 dark:border-forest-800 pb-1">Estimated Savings Impact</h3>
                   <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="bg-blue-50 dark:bg-blue-900/20 p-2 rounded-lg border border-blue-100 dark:border-blue-800/50">
                          <Droplets size={16} className="mx-auto text-blue-500 mb-1" />
                          <p className="text-[10px] text-forest-500 dark:text-forest-400 uppercase">Water</p>
                          <p className="text-xs font-bold text-forest-800 dark:text-forest-200">{result.water_savings_estimate}</p>
                      </div>
                      <div className="bg-yellow-50 dark:bg-yellow-900/20 p-2 rounded-lg border border-yellow-100 dark:border-yellow-800/50">
                          <Zap size={16} className="mx-auto text-yellow-500 mb-1" />
                          <p className="text-[10px] text-forest-500 dark:text-forest-400 uppercase">Energy</p>
                          <p className="text-xs font-bold text-forest-800 dark:text-forest-200">{result.energy_savings_estimate}</p>
                      </div>
                      <div className="bg-emerald-50 dark:bg-emerald-900/20 p-2 rounded-lg border border-emerald-100 dark:border-emerald-800/50">
                          <DollarSign size={16} className="mx-auto text-emerald-500 mb-1" />
                          <p className="text-[10px] text-forest-500 dark:text-forest-400 uppercase">Cost</p>
                          <p className="text-xs font-bold text-forest-800 dark:text-forest-200">{result.cost_savings_estimate}</p>
                      </div>
                   </div>
                </div>

                {/* Factors */}
                <div>
                  <h3 className="text-xs font-semibold text-forest-900 dark:text-forest-100 uppercase tracking-wide mb-3 border-b border-forest-100 dark:border-forest-800 pb-1">Scoring Factors</h3>
                  <div className="space-y-4">
                      {result.positive_factors.length > 0 && (
                        <ul className="space-y-2">
                          {result.positive_factors.map((f, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <div className="mt-0.5 rounded-full p-0.5 text-green-500 bg-green-50 dark:bg-green-900/30">
                                <CheckCircle size={14} />
                              </div>
                              <span className="text-forest-800 dark:text-forest-300">{f}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                      
                      {result.improvement_suggestions.length > 0 && (
                        <ul className="space-y-2">
                          {result.improvement_suggestions.map((s, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <div className="mt-0.5 rounded-full p-0.5 text-yellow-500 bg-yellow-50 dark:bg-yellow-900/30">
                                <AlertTriangle size={14} />
                              </div>
                              <span className="text-forest-800 dark:text-forest-300">{s}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                  </div>
                </div>

                <div className="pt-4 border-t border-forest-100 dark:border-forest-800 text-xs text-forest-500 dark:text-forest-400 space-y-1">
                   <p><strong>Missing Data:</strong> {Object.entries(result.source_labels).filter(([_, v]) => v === 'unavailable').map(([k]) => k.replace(/_/g, ' ')).join(', ') || 'None'}</p>
                   <p className="italic text-[10px] mt-2">{result.warning}</p>
                </div>
              </div>
            )}
          </div>
          
          {/* History */}
          <div className="agri-card dark:bg-forest-900 dark:border-forest-800">
             <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
                <History size={18} className="text-emerald-500" /> Assessment History
             </h2>
             {historyLoading ? (
                 <div className="flex justify-center p-4"><Loader2 className="spin text-forest-400" size={20}/></div>
             ) : history.length > 0 ? (
                 <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                     {history.slice(0, 10).map(h => (
                         <div key={h.id} className="p-3 bg-forest-50 dark:bg-forest-950 rounded-lg border border-forest-100 dark:border-forest-800 flex justify-between items-center text-sm">
                             <div>
                                 <p className="font-medium text-forest-900 dark:text-white flex items-center gap-1">
                                    {h.score} pts <span className="text-[10px] text-forest-400 font-normal ml-1">({formatDate(h.created_at)})</span>
                                 </p>
                                 <p className="text-[10px] text-forest-500 dark:text-forest-400 mt-1 truncate max-w-[150px]" title={h.improvement}>→ {h.improvement}</p>
                             </div>
                             <div className={`px-2 py-1 rounded text-[10px] font-semibold uppercase ${getCategoryColor(h.category)}`}>
                                 {h.category}
                             </div>
                         </div>
                     ))}
                 </div>
             ) : (
                 <p className="text-sm text-forest-500 dark:text-forest-400 text-center py-4">No past sustainability records found.</p>
             )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SustainabilityScore
