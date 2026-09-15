import React, { useState, useEffect, useRef, useMemo } from 'react'
import { UploadCloud, Image as ImageIcon, CheckCircle, AlertTriangle, XCircle, Info, RefreshCw, Activity, Search, Leaf, ScanLine } from 'lucide-react'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { diseaseMetadata } from '../data/diseaseMetadata'

function DiseaseDetection() {
  const { user } = useAuth()
  const [selectedCrop, setSelectedCrop] = useState('auto')
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  
  const [history, setHistory] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(true)
  
  const fileInputRef = useRef(null)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await api.get('disease/history/')
      setHistory(response.data.history || [])
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
    
    if (file.size > 15 * 1024 * 1024) {
      setError('File size exceeds 15MB limit.')
      return
    }
    
    if (!['image/jpeg', 'image/jpg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Unsupported file format. Please upload JPG, PNG, or WEBP.')
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

    setIsAnalyzing(true)
    setError('')

    const formData = new FormData()
    formData.append('image', selectedFile)
    if (selectedCrop !== 'auto') {
      formData.append('crop_type', selectedCrop)
    }

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
      setError(err.response?.data?.error || 'An unexpected error occurred connecting to the prediction service.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getStatusColor = (severity) => {
    if (severity === 'None') return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800'
    if (severity === 'High' || severity === 'Critical') return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800'
    return 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800'
  }
  
  const getStatusIcon = (severity) => {
    if (severity === 'None') return <CheckCircle size={24} className="text-green-500" />
    if (severity === 'High' || severity === 'Critical') return <AlertTriangle size={24} className="text-red-500" />
    return <Search size={24} className="text-amber-500" />
  }

  // Ensure robust result mapping
  const predictionMeta = result?.predicted_class ? diseaseMetadata[result.predicted_class] : null;

  const validScans = history.filter(scan => scan.predicted_class && diseaseMetadata[scan.predicted_class] && scan.confidence != null);
  
  const computedAnalytics = useMemo(() => {
    if (validScans.length === 0) return null;
    
    let healthyCount = 0;
    let diseasedCount = 0;
    
    const cropCounts = {};
    const diseaseCounts = {};
    
    validScans.forEach(scan => {
      const meta = diseaseMetadata[scan.predicted_class];
      const crop = meta.crop;
      cropCounts[crop] = (cropCounts[crop] || 0) + 1;
      
      if (meta.severity === 'None' || meta.disease.toLowerCase() === 'healthy') {
        healthyCount++;
      } else {
        diseasedCount++;
        const disease = meta.disease;
        diseaseCounts[disease] = (diseaseCounts[disease] || 0) + 1;
      }
    });
    
    let totalConfidence = validScans.reduce((acc, curr) => {
      const conf = curr.confidence <= 1 ? curr.confidence * 100 : curr.confidence;
      return acc + conf;
    }, 0);
    const avgConfidence = (totalConfidence / validScans.length).toFixed(2);

    const mostFrequentDisease = Object.entries(diseaseCounts).sort((a, b) => b[1] - a[1])[0];
    
    return {
      total: validScans.length,
      healthy: healthyCount,
      diseased: diseasedCount,
      avgConfidence: avgConfidence,
      mostFrequentDisease: mostFrequentDisease ? mostFrequentDisease[0] : null,
      cropDistribution: Object.entries(cropCounts).sort((a, b) => b[1] - a[1]),
      diseaseDistribution: Object.entries(diseaseCounts).sort((a, b) => b[1] - a[1])
    };
  }, [validScans]);

  return (
    <div className="space-y-6 w-full max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-forest-900 dark:text-forest-100 flex items-center gap-2">
            <ScanLine className="text-forest-600" /> Disease Detection
          </h1>
          <p className="text-forest-600 dark:text-forest-400 text-sm mt-1">Upload a crop leaf image for AI diagnosis.</p>
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
                  Upload a clear, well-lit image of a single leaf. Supported formats: JPG, PNG, WEBP (Max 15MB).
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
              accept=".jpg,.jpeg,.png,.webp"
              onChange={handleFileSelect} 
            />
          </div>

          {previewUrl && !result && (
            <div className="agri-card bg-forest-50 dark:bg-forest-900/20 border border-forest-200 dark:border-forest-800">
              <label className="block text-sm font-semibold text-forest-900 dark:text-forest-100 mb-2">
                Which crop is pictured in the image? (Optional)
              </label>
              <select 
                value={selectedCrop}
                onChange={(e) => { setSelectedCrop(e.target.value); setError(''); }}
                className="w-full p-3 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 focus:ring-2 focus:ring-forest-500 outline-none transition-shadow"
              >
                <option value="auto">Auto-detect crop</option>
                <option value="apple">Apple</option>
                <option value="blueberry">Blueberry</option>
                <option value="cherry">Cherry</option>
                <option value="corn">Corn (Maize)</option>
                <option value="grape">Grape</option>
                <option value="orange">Orange</option>
                <option value="peach">Peach</option>
                <option value="pepper">Pepper (Bell)</option>
                <option value="potato">Potato</option>
                <option value="raspberry">Raspberry</option>
                <option value="soybean">Soybean</option>
                <option value="squash">Squash</option>
                <option value="strawberry">Strawberry</option>
                <option value="tomato">Tomato</option>
                <option value="other">Other / Unknown</option>
              </select>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl flex items-center gap-2 border border-red-200 dark:border-red-800 text-sm font-medium">
              <AlertTriangle size={18} className="shrink-0" /> 
              <span>{error}</span>
            </div>
          )}

          {previewUrl && !result && !error && (
            <button 
              onClick={handleAnalyze} 
              disabled={isAnalyzing}
              className="w-full py-3.5 bg-forest-600 hover:bg-forest-700 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-70"
            >
              {isAnalyzing ? (
                <><RefreshCw size={20} className="animate-spin" /> Analyzing leaf image...</>
              ) : (
                <><Search size={20} /> Analyze Image</>
              )}
            </button>
          )}

          {/* Analysis Result */}
          {result && (
            <div className={`agri-card border-2 ${predictionMeta ? getStatusColor(predictionMeta.severity) : 'border-forest-200'}`}>
              {!predictionMeta ? (
                <div className="flex flex-col items-center justify-center p-6 text-center">
                  <AlertTriangle size={48} className="text-amber-500 mb-4" />
                  <h3 className="text-xl font-bold mb-2">Unable to confidently identify this image.</h3>
                  {result.confidence && (
                     <p className="text-sm opacity-80 mb-4">Confidence: {result.confidence}%</p>
                  )}
                  <p className="mb-4">Please upload a clear close-up image of a single crop leaf.</p>
                  <button onClick={resetUpload} className="px-6 py-2 bg-forest-600 text-white rounded-lg font-semibold hover:bg-forest-700 transition-colors">
                    Upload Again
                  </button>
                </div>
              ) : (
                <div className="flex items-start gap-4">
                  <div className="mt-1 p-2 bg-white dark:bg-black/20 rounded-full shadow-sm">
                    {getStatusIcon(predictionMeta.severity)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h2 className="text-xl font-bold uppercase tracking-wide">
                        {predictionMeta.displayName}
                      </h2>
                      {result.confidence !== null && (
                        <span className="text-sm font-bold bg-white/50 dark:bg-black/30 px-2 py-1 rounded">
                          Confidence: {result.confidence}%
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm font-medium mb-4">{predictionMeta.description}</p>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm mb-6">
                      <div className="bg-white/50 dark:bg-black/20 p-3 rounded-lg">
                        <div className="text-xs opacity-70 mb-1">Crop</div>
                        <div className="font-semibold">{predictionMeta.crop}</div>
                      </div>
                      <div className="bg-white/50 dark:bg-black/20 p-3 rounded-lg">
                        <div className="text-xs opacity-70 mb-1">Severity</div>
                        <div className="font-semibold">{predictionMeta.severity}</div>
                      </div>
                    </div>

                    <div className="space-y-4 bg-white/60 dark:bg-black/20 p-4 rounded-xl text-sm">
                      {predictionMeta.symptoms && predictionMeta.symptoms.length > 0 && predictionMeta.severity !== 'None' && (
                        <div>
                          <strong className="block mb-1 opacity-80">Visible Symptoms:</strong>
                          <ul className="list-disc pl-5 space-y-1">
                            {predictionMeta.symptoms.map((s, i) => <li key={i}>{s}</li>)}
                          </ul>
                        </div>
                      )}
                      
                      {predictionMeta.treatment && predictionMeta.treatment.length > 0 && predictionMeta.severity !== 'None' && (
                        <div>
                          <strong className="block mb-1 opacity-80">Treatment / Management:</strong>
                          <ul className="list-disc pl-5 space-y-1">
                            {predictionMeta.treatment.map((t, i) => <li key={i}>{t}</li>)}
                          </ul>
                        </div>
                      )}
                      
                      {predictionMeta.prevention && predictionMeta.prevention.length > 0 && (
                        <div>
                          <strong className="block mb-1 opacity-80">Prevention:</strong>
                          <ul className="list-disc pl-5 space-y-1">
                            {predictionMeta.prevention.map((p, i) => <li key={i}>{p}</li>)}
                          </ul>
                        </div>
                      )}

                      {predictionMeta.advisory && (
                        <div className="mt-4 p-3 bg-white dark:bg-forest-950 border border-forest-100 dark:border-forest-800 rounded-lg flex gap-2">
                          <Info size={18} className="text-blue-500 shrink-0 mt-0.5" />
                          <span className="opacity-90">{predictionMeta.advisory}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-6 flex gap-3">
                      <button onClick={resetUpload} className="px-4 py-2 bg-white dark:bg-forest-950 border border-current rounded-lg font-semibold hover:opacity-80 transition-opacity">
                        Scan Another
                      </button>
                    </div>
                  </div>
                </div>
              )}
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
            ) : computedAnalytics ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3 text-center">
                  <div className="bg-forest-50 dark:bg-forest-900/30 p-3 rounded-lg border border-forest-100 dark:border-forest-800">
                    <div className="text-2xl font-bold text-forest-900 dark:text-forest-100">{computedAnalytics.total}</div>
                    <div className="text-xs text-forest-500 mt-1">Total Scans</div>
                  </div>
                  <div className="bg-forest-50 dark:bg-forest-900/30 p-3 rounded-lg border border-forest-100 dark:border-forest-800">
                    <div className="text-2xl font-bold text-red-500">{computedAnalytics.diseased}</div>
                    <div className="text-xs text-forest-500 mt-1">Diseased Scans</div>
                  </div>
                  <div className="bg-forest-50 dark:bg-forest-900/30 p-3 rounded-lg border border-forest-100 dark:border-forest-800">
                    <div className="text-2xl font-bold text-green-500">{computedAnalytics.healthy}</div>
                    <div className="text-xs text-forest-500 mt-1">Healthy Scans</div>
                  </div>
                  <div className="bg-forest-50 dark:bg-forest-900/30 p-3 rounded-lg border border-forest-100 dark:border-forest-800">
                    <div className="text-2xl font-bold text-blue-500">{computedAnalytics.avgConfidence}%</div>
                    <div className="text-xs text-forest-500 mt-1">Avg Confidence</div>
                  </div>
                </div>
                
                {computedAnalytics.mostFrequentDisease && (
                  <div className="text-sm bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200 p-3 rounded-lg text-center mt-4">
                    Most Frequent Disease: <strong>{computedAnalytics.mostFrequentDisease}</strong>
                  </div>
                )}
                
                {computedAnalytics.cropDistribution.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-xs font-semibold text-forest-500 uppercase tracking-wider mb-2">Crop Breakdown</h4>
                    <div className="flex flex-wrap gap-2">
                      {computedAnalytics.cropDistribution.map(([crop, count]) => (
                        <span key={crop} className="text-[11px] font-medium px-2 py-1 bg-forest-100 dark:bg-forest-800 text-forest-700 dark:text-forest-300 rounded-md">
                          {crop}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {computedAnalytics.diseaseDistribution.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-xs font-semibold text-forest-500 uppercase tracking-wider mb-2">Disease Distribution</h4>
                    <div className="space-y-2">
                      {computedAnalytics.diseaseDistribution.slice(0, 5).map(([disease, count]) => (
                        <div key={disease} className="flex items-center text-xs">
                          <span className="flex-1 truncate text-forest-700 dark:text-forest-300 pr-2">{disease}</span>
                          <span className="font-semibold text-forest-900 dark:text-forest-100 w-6 text-right">{count}</span>
                          <div className="w-16 h-1.5 ml-2 bg-forest-100 dark:bg-forest-800 rounded-full overflow-hidden">
                            <div className="h-full bg-red-400" style={{ width: `${(count / computedAnalytics.diseased) * 100}%` }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-forest-500 text-center py-4 bg-forest-50 dark:bg-forest-900/30 rounded-xl">
                No successful scans available yet.
              </div>
            )}
          </div>

          <div className="agri-card">
            <h3 className="font-bold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <ImageIcon size={18} className="text-forest-500" /> Recent Scans
            </h3>
            <div className="space-y-3">
              {history.length > 0 ? (
                history.slice(0, 5).map((scan) => {
                  const meta = diseaseMetadata[scan.predicted_class];
                  return (
                    <div key={scan.id} className="flex gap-3 items-center p-2 rounded-lg hover:bg-forest-50 dark:hover:bg-forest-900/40 transition-colors border border-transparent hover:border-forest-100 dark:hover:border-forest-800">
                      {scan.image_url ? (
                        <img src={scan.image_url} alt="scan" className="w-12 h-12 rounded object-cover border border-forest-200 dark:border-forest-800" />
                      ) : (
                        <div className="w-12 h-12 rounded bg-forest-100 flex items-center justify-center"><Leaf size={16} className="opacity-30" /></div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-semibold truncate ${
                          meta?.severity === 'None' ? 'text-green-600 dark:text-green-400' :
                          meta?.severity ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'
                        }`}>
                          {meta?.displayName || 'Unknown Scan'}
                        </div>
                        <div className="text-[10px] text-forest-400 uppercase tracking-wider">{new Date(scan.created_at).toLocaleDateString()}</div>
                      </div>
                    </div>
                  );
                })
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
