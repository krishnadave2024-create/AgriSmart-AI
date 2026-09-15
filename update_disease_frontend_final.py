disease_jsx = """
import React, { useState, useEffect, useRef } from 'react'
import { UploadCloud, Image as ImageIcon, CheckCircle, AlertTriangle, XCircle, Info, RefreshCw, Activity, Search, Leaf } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { ScanLine } from 'lucide-react'

function DiseaseDetection() {
  const { user } = useAuth()
  const [selectedCrop, setSelectedCrop] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  
  const [history, setHistory] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [loadingHistory, setLoadingHistory] = useState(true)
  
  const fileInputRef = useRef(null)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await api.get('disease/history/')
      setHistory(response.data.history || [])
      setAnalytics(response.data.analytics || null)
    } catch (err) {
      console.error('Failed to fetch disease history:', err)
    } finally {
      setLoadingHistory(false)
    }
  }

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    handleFile(file)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    handleFile(file)
  }

  const handleFile = (file) => {
    setError('')
    setResult(null)
    
    if (!file) return
    
    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit.')
      return
    }
    
    if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
      setError('Unsupported file format. Please upload JPG or PNG.')
      return
    }

    setSelectedFile(file)
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
  }

  const handleDragOver = (event) => {
    event.preventDefault()
  }

  const resetUpload = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setResult(null)
    setError('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return
    if (!selectedCrop) {
      setError('Please select a crop type before analyzing.')
      return
    }

    setIsAnalyzing(true)
    setError('')

    const formData = new FormData()
    formData.append('image', selectedFile)
    formData.append('crop_type', selectedCrop)

    try {
      const response = await api.post('disease/predict/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (response.data.success) {
        setResult(response.data)
        fetchHistory()
      } else {
        setError(response.data.error || 'Failed to analyze image.')
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An unexpected error occurred.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getStatusColor = (status) => {
    if (status === 'healthy') return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800'
    if (status === 'diseased') return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800'
    return 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800'
  }
  
  const getStatusIcon = (status) => {
    if (status === 'healthy') return <CheckCircle size={24} className="text-green-500" />
    if (status === 'diseased') return <AlertTriangle size={24} className="text-red-500" />
    return <Search size={24} className="text-amber-500" />
  }
  
  const chartData = analytics ? [
    { name: 'Healthy', value: analytics.healthy_scans, color: '#22c55e' },
    { name: 'Diseased', value: analytics.diseased_scans, color: '#ef4444' },
    { name: 'Uncertain', value: analytics.uncertain_scans, color: '#f59e0b' }
  ].filter(d => d.value > 0) : []

  return (
    <div className="space-y-6 w-full max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-forest-900 dark:text-forest-100 flex items-center gap-2">
            <ScanLine className="text-forest-600" /> Disease Detection
          </h1>
          <p className="text-forest-600 dark:text-forest-400 text-sm mt-1">Upload a crop leaf image for AI diagnosis.</p>
        </div>
        <div className="text-xs bg-forest-100 dark:bg-forest-900/40 text-forest-600 dark:text-forest-300 px-3 py-1.5 rounded-full font-medium flex items-center gap-2 border border-forest-200 dark:border-forest-700 shadow-sm">
          <Info size={14} /> Only Tomato leaves are fully supported
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Upload & Preview Area */}
        <div className="lg:col-span-2 space-y-6">
          <div className="agri-card border-dashed border-2 border-forest-200 dark:border-forest-800 hover:border-forest-400 dark:hover:border-forest-600 transition-colors">
            {!previewUrl ? (
              <div 
                className="flex flex-col items-center justify-center py-16 px-4 text-center cursor-pointer"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="w-16 h-16 bg-forest-50 dark:bg-forest-900/40 rounded-full flex items-center justify-center mb-4">
                  <UploadCloud size={32} className="text-forest-500" />
                </div>
                <h3 className="text-lg font-semibold text-forest-900 dark:text-forest-100">Click or drag image to upload</h3>
                <p className="text-forest-500 dark:text-forest-400 text-sm mt-2 max-w-sm">
                  Upload a clear, well-lit image of a single leaf. Supported formats: JPG, PNG (Max 10MB).
                </p>
              </div>
            ) : (
              <div className="relative">
                <img src={previewUrl} alt="Leaf preview" className="w-full h-80 object-cover rounded-xl" />
                <button 
                  onClick={resetUpload}
                  className="absolute top-4 right-4 bg-white/90 dark:bg-black/90 p-2 rounded-full shadow-lg hover:scale-110 transition-transform"
                  title="Remove image"
                >
                  <XCircle className="text-red-500" size={24} />
                </button>
              </div>
            )}
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              accept=".jpg,.jpeg,.png"
              onChange={handleFileSelect} 
            />
          </div>

          {previewUrl && !result && (
            <div className="agri-card bg-forest-50 dark:bg-forest-900/20 border border-forest-200 dark:border-forest-800">
              <label className="block text-sm font-semibold text-forest-900 dark:text-forest-100 mb-2">
                Which crop is pictured in the image?
              </label>
              <select 
                value={selectedCrop}
                onChange={(e) => { setSelectedCrop(e.target.value); setError(''); }}
                className="w-full p-3 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 focus:ring-2 focus:ring-forest-500 outline-none transition-shadow"
              >
                <option value="" disabled>Select Crop...</option>
                <option value="tomato">Tomato</option>
                <option value="other">Other / Unsupported</option>
              </select>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl flex items-center gap-2 border border-red-200 dark:border-red-800 text-sm font-medium">
              <AlertTriangle size={18} /> {error}
            </div>
          )}

          {previewUrl && !result && !error && selectedCrop && (
            <button 
              onClick={handleAnalyze} 
              disabled={isAnalyzing}
              className="w-full py-3.5 bg-forest-600 hover:bg-forest-700 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-70"
            >
              {isAnalyzing ? (
                <><RefreshCw size={20} className="animate-spin" /> Analyzing...</>
              ) : (
                <><Search size={20} /> Analyze Image</>
              )}
            </button>
          )}

          {/* Analysis Result */}
          {result && result.prediction && (
            <div className={`agri-card border-2 ${getStatusColor(result.prediction.status)}`}>
              <div className="flex items-start gap-4">
                <div className="mt-1 p-2 bg-white dark:bg-black/20 rounded-full shadow-sm">
                  {getStatusIcon(result.prediction.status)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h2 className="text-xl font-bold uppercase tracking-wide">
                      {result.prediction.status === 'healthy' ? 'Healthy Leaf' : 
                       result.prediction.status === 'unsupported_crop' ? 'Unsupported Crop' :
                       result.prediction.status === 'uncertain' ? 'Uncertain / Low Confidence' : 
                       'Disease Detected'}
                    </h2>
                    {result.prediction.confidence !== null && (
                      <span className="text-sm font-bold bg-white/50 dark:bg-black/30 px-2 py-1 rounded">
                        Model Score: {(result.prediction.confidence * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  
                  {result.prediction.confidence !== null && (
                    <div className="text-xs opacity-75 mb-3 italic">
                      This score is not a guarantee of diagnostic accuracy.
                    </div>
                  )}
                  
                  <p className="text-sm font-medium mb-4">{result.message}</p>
                  
                  {result.prediction.status !== 'unsupported_crop' && result.prediction.status !== 'uncertain' && (
                    <div className="grid grid-cols-2 gap-4 text-sm mb-6">
                      <div className="bg-white/50 dark:bg-black/20 p-3 rounded-lg">
                        <div className="text-xs opacity-70 mb-1">Crop</div>
                        <div className="font-semibold">{result.prediction.crop || 'Unknown'}</div>
                      </div>
                      {result.prediction.disease && (
                        <div className="bg-white/50 dark:bg-black/20 p-3 rounded-lg">
                          <div className="text-xs opacity-70 mb-1">Disease</div>
                          <div className="font-semibold">{result.prediction.disease}</div>
                        </div>
                      )}
                    </div>
                  )}

                  {result.knowledge && (
                    <div className="space-y-4 bg-white/60 dark:bg-black/20 p-4 rounded-xl text-sm">
                      {result.knowledge.symptoms && result.knowledge.symptoms.length > 0 && (
                        <div>
                          <strong className="block mb-1 opacity-80">Symptoms:</strong>
                          <ul className="list-disc pl-5 space-y-1">
                            {result.knowledge.symptoms.map((s, i) => <li key={i}>{s}</li>)}
                          </ul>
                        </div>
                      )}
                      
                      {result.knowledge.treatment && result.knowledge.treatment.length > 0 && result.prediction.status === 'diseased' && (
                        <div>
                          <strong className="block mb-1 opacity-80">Treatment:</strong>
                          <ul className="list-disc pl-5 space-y-1">
                            {result.knowledge.treatment.map((t, i) => <li key={i}>{t}</li>)}
                          </ul>
                        </div>
                      )}
                      
                      {result.knowledge.prevention && result.knowledge.prevention.length > 0 && (
                        <div>
                          <strong className="block mb-1 opacity-80">Prevention:</strong>
                          <ul className="list-disc pl-5 space-y-1">
                            {result.knowledge.prevention.map((p, i) => <li key={i}>{p}</li>)}
                          </ul>
                        </div>
                      )}

                      {result.knowledge.safe_next_steps && result.knowledge.safe_next_steps.length > 0 && (
                        <div>
                          <strong className="block mb-1 opacity-80">Safe Next Steps:</strong>
                          <ul className="list-disc pl-5 space-y-1">
                            {result.knowledge.safe_next_steps.map((p, i) => <li key={i}>{p}</li>)}
                          </ul>
                        </div>
                      )}

                      {result.knowledge.expert_consult && (
                        <div className="mt-4 p-3 bg-white dark:bg-forest-950 border border-forest-100 dark:border-forest-800 rounded-lg flex gap-2">
                          <Info size={18} className="text-blue-500 shrink-0 mt-0.5" />
                          <span className="opacity-90">{result.knowledge.expert_consult}</span>
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className="mt-6 flex gap-3">
                    <button onClick={resetUpload} className="px-4 py-2 bg-white dark:bg-forest-950 border border-current rounded-lg font-semibold hover:opacity-80 transition-opacity">
                      Scan Another
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar: Analytics & History */}
        <div className="space-y-6">
          
          <div className="agri-card">
            <h3 className="font-bold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <Activity size={18} className="text-forest-500" /> Disease Analytics
            </h3>
            {loadingHistory ? (
               <div className="text-center py-4 opacity-50"><RefreshCw className="animate-spin inline mr-2" size={16}/>Loading...</div>
            ) : analytics && analytics.total_scans > 0 ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3 text-center">
                  <div className="bg-forest-50 dark:bg-forest-900/30 p-3 rounded-lg border border-forest-100 dark:border-forest-800">
                    <div className="text-2xl font-bold text-forest-900 dark:text-forest-100">{analytics.total_scans}</div>
                    <div className="text-xs text-forest-500">Total Scans</div>
                  </div>
                  <div className="bg-forest-50 dark:bg-forest-900/30 p-3 rounded-lg border border-forest-100 dark:border-forest-800">
                    <div className="text-2xl font-bold text-red-500">{analytics.diseased_scans}</div>
                    <div className="text-xs text-forest-500">Diseased</div>
                  </div>
                </div>
                
                {chartData.length > 0 && (
                  <div className="h-40 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={chartData} cx="50%" cy="50%" innerRadius={35} outerRadius={55} paddingAngle={2} dataKey="value">
                          {chartData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                        </Pie>
                        <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                )}
                
                {analytics.most_frequent_disease && analytics.most_frequent_disease !== 'None' && (
                  <div className="text-sm bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200 p-3 rounded-lg text-center">
                    Most Frequent: <strong>{analytics.most_frequent_disease}</strong>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-forest-500 text-center py-4 bg-forest-50 dark:bg-forest-900/30 rounded-xl">
                Not enough scan history for analytics.
              </div>
            )}
          </div>

          <div className="agri-card">
            <h3 className="font-bold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <ImageIcon size={18} className="text-forest-500" /> Recent Scans
            </h3>
            <div className="space-y-3">
              {history.length > 0 ? (
                history.slice(0, 5).map((scan) => (
                  <div key={scan.id} className="flex gap-3 items-center p-2 rounded-lg hover:bg-forest-50 dark:hover:bg-forest-900/40 transition-colors border border-transparent hover:border-forest-100 dark:hover:border-forest-800">
                    {scan.image_url ? (
                      <img src={scan.image_url} alt="scan" className="w-12 h-12 rounded object-cover border border-forest-200 dark:border-forest-800" />
                    ) : (
                      <div className="w-12 h-12 rounded bg-forest-100 flex items-center justify-center"><Leaf size={16} className="opacity-30" /></div>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className={`text-sm font-semibold truncate ${
                        scan.prediction_status === 'healthy' ? 'text-green-600 dark:text-green-400' :
                        scan.prediction_status === 'diseased' ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'
                      }`}>
                        {scan.prediction_status === 'diseased' ? scan.disease_name : scan.prediction_status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </div>
                      <div className="text-[10px] text-forest-400 uppercase tracking-wider">{new Date(scan.created_at).toLocaleDateString()}</div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-sm text-forest-500 text-center py-4">No scan history available.</div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default DiseaseDetection
"""

with open('frontend/src/components/DiseaseDetection.jsx', 'w', encoding='utf-8') as f:
    f.write(disease_jsx)
print("DiseaseDetection.jsx updated with crop selector and confidence disclaimer.")
