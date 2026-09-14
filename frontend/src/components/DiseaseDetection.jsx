import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { UploadCloud, ScanLine, Loader2, AlertTriangle, RefreshCw, CheckCircle, FileImage, ShieldAlert, HeartPulse, History, ChevronRight } from 'lucide-react'
import api from '../utils/api'

function DiseaseDetection() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [history, setHistory] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(true)

  const inputRef = useRef(null)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      setLoadingHistory(true)
      const res = await api.get('disease/history/')
      setHistory(res.data.history || [])
    } catch (err) {
      console.error('Failed to load history', err)
    } finally {
      setLoadingHistory(false)
    }
  }

  const validate = (f) => {
    setError(null)
    setResult(null)
    if (!f) return false
    if (!['image/jpeg', 'image/png', 'image/jpg'].includes(f.type)) {
      setError('Unsupported format. Please upload JPG or PNG.')
      return false
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10 MB limit.')
      return false
    }
    return true
  }

  const pick = (f) => {
    if (validate(f)) {
      setFile(f)
      setPreview(URL.createObjectURL(f))
    }
  }

  const handleInput = (e) => {
    if (e.target.files?.[0]) pick(e.target.files[0])
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(e.type === 'dragenter' || e.type === 'dragover')
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) pick(e.dataTransfer.files[0])
  }

  const reset = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  const analyze = async () => {
    if (!file) return
    setLoading(true)
    setError(null)

    const fd = new FormData()
    fd.append('image', file)

    try {
      // Need to attach auth header manually if using raw axios, but let's use the api instance so auth is handled.
      // Wait, api uses interceptors which works great. But we need FormData.
      const r = await api.post('disease/predict/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(r.data)
      fetchHistory() // Refresh history after successful scan
    } catch (err) {
      setError(err.response?.data?.error ?? 'Failed to connect to backend. Please ensure the Django API is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <ScanLine size={26} className="text-forest-600" /> Plant Disease Diagnosis
          </h1>
          <p className="page-subtitle">Upload a leaf image for AI-powered pathogen identification.</p>
        </div>
        <span className="badge-proto">Prototype</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Upload Panel */}
        <div className="agri-card space-y-4">
          <h2 className="font-semibold text-forest-900">Upload Leaf Image</h2>

          {!file ? (
            <div
              className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag} onDragLeave={handleDrag}
              onDragOver={handleDrag} onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
              role="button" tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
              aria-label="Upload leaf image"
            >
              <UploadCloud size={44} className="mx-auto mb-3 text-forest-400" />
              <p className="font-semibold text-forest-700 mb-1">Click to browse or drag image here</p>
              <p className="text-xs text-forest-500">Supported formats: JPG, JPEG, PNG · Max 10 MB</p>
              <input ref={inputRef} type="file" className="hidden" accept="image/jpeg,image/png,image/jpg" onChange={handleInput} />
            </div>
          ) : (
            <div className="space-y-4">
              <div className="relative rounded-xl overflow-hidden border border-forest-200">
                <img src={preview} alt="Leaf preview" className="w-full object-contain max-h-64 bg-forest-50" />
                <div className="absolute top-2 left-2">
                  <span className="badge bg-black/60 text-white text-[10px]">
                    <FileImage size={10} className="mr-1 inline-block" /> {file.name}
                  </span>
                </div>
              </div>
              <div className="flex gap-3">
                <button className="btn-secondary" onClick={reset}>Cancel</button>
                {!result && !loading && (
                  <button className="btn-primary flex-1 justify-center" onClick={analyze}>
                    <ScanLine size={16} /> Analyze Leaf
                  </button>
                )}
              </div>
            </div>
          )}

          {error && (
            <div className="error-banner">
              <AlertTriangle size={18} className="flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

        </div>

        {/* Results Panel */}
        <div className="agri-card flex flex-col">
          <h2 className="font-semibold text-forest-900 mb-4">Diagnosis Report</h2>

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 py-12 text-forest-600">
              <Loader2 size={36} className="spin" />
              <span className="text-sm font-medium">Running Diagnosis Pipeline…</span>
            </div>
          )}

          {!loading && !result && !error && (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400">
              <ScanLine size={36} className="mb-3 opacity-40" />
              <p className="text-sm">Upload and analyze a leaf to generate a report.</p>
            </div>
          )}

          {result && !loading && (
            <div className="slide-up space-y-5">

              <div className={`p-4 rounded-xl border ${result.predicted_class === 'healthy' ? 'bg-emerald-50 border-emerald-100' : 'bg-red-50 border-red-100'}`}>
                <div className="flex items-center gap-3">
                  {result.predicted_class === 'healthy' ? (
                    <HeartPulse size={28} className="text-emerald-600" />
                  ) : (
                    <AlertTriangle size={28} className="text-red-600" />
                  )}
                  <div>
                    <div className={`text-xl font-bold capitalize ${result.predicted_class === 'healthy' ? 'text-emerald-900' : 'text-red-900'}`}>
                      {result.knowledge?.disease_name || result.predicted_class}
                    </div>
                    {result.confidence && (
                      <div className={`text-sm ${result.predicted_class === 'healthy' ? 'text-emerald-700' : 'text-red-700'}`}>
                        Confidence: <strong>{(result.confidence * 100).toFixed(1)}%</strong>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {result.knowledge && (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-xs font-bold text-forest-500 uppercase tracking-wider mb-2">Symptoms & Signs</h3>
                    <ul className="list-disc list-inside text-sm text-forest-800 space-y-1">
                      {result.knowledge.symptoms.map((sym, idx) => (
                        <li key={idx}>{sym}</li>
                      ))}
                    </ul>
                  </div>

                  {result.predicted_class !== 'healthy' && (
                    <>
                      <div className="pt-3 border-t border-forest-100">
                        <h3 className="text-xs font-bold text-forest-500 uppercase tracking-wider mb-2">Treatment</h3>
                        <ul className="list-disc list-inside text-sm text-forest-800 space-y-1">
                          {result.knowledge.treatment.map((tr, idx) => (
                            <li key={idx}>{tr}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="pt-3 border-t border-forest-100">
                        <h3 className="text-xs font-bold text-forest-500 uppercase tracking-wider mb-2">Prevention</h3>
                        <ul className="list-disc list-inside text-sm text-forest-800 space-y-1">
                          {result.knowledge.prevention.map((pr, idx) => (
                            <li key={idx}>{pr}</li>
                          ))}
                        </ul>
                      </div>
                    </>
                  )}
                </div>
              )}

              {result.is_development && (
                <div className="proto-banner">
                  <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />

                </div>
              )}

              <button className="btn-secondary w-full justify-center mt-4" onClick={reset}>
                <RefreshCw size={15} /> Scan Another Leaf
              </button>
            </div>
          )}
        </div>
      </div>

      {/* History Section */}
      <div className="agri-card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-lg text-forest-900 flex items-center gap-2">
            <History size={20} className="text-forest-600" /> Recent Scans
          </h2>
          {!loadingHistory && history.length > 0 && (
            <span className="text-xs font-medium bg-forest-100 text-forest-700 px-2 py-1 rounded-full">
              {history.length} Total
            </span>
          )}
        </div>

        {loadingHistory ? (
          <div className="flex justify-center py-8 text-forest-400">
            <Loader2 size={24} className="spin" />
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-8 text-forest-500 text-sm">
            You haven't run any disease scans yet.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {history.slice(0, 8).map(scan => (
              <div key={scan.id} className="border border-forest-100 rounded-xl overflow-hidden hover:shadow-md transition-shadow bg-white flex flex-col">
                {scan.image_url ? (
                  <img src={scan.image_url} alt="Scan thumbnail" className="w-full h-32 object-cover border-b border-forest-100" />
                ) : (
                  <div className="w-full h-32 bg-forest-50 flex items-center justify-center border-b border-forest-100">
                    <FileImage size={24} className="text-forest-300" />
                  </div>
                )}
                <div className="p-3 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-xs font-bold capitalize ${scan.predicted_class === 'healthy' ? 'text-emerald-700' : 'text-red-700'}`}>
                        {scan.predicted_class}
                      </span>
                      <span className="text-[10px] text-forest-500">{(scan.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="text-[10px] text-forest-400 mb-2">
                      {new Date(scan.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  {scan.is_development && (
                    <div className="text-[9px] bg-amber-50 text-amber-700 px-1.5 py-0.5 rounded border border-amber-100 self-start">
                      Dev Model
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  )
}

export default DiseaseDetection
