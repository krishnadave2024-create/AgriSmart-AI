import { useState, useRef } from 'react'
import axios from 'axios'
import { UploadCloud, ScanLine, Loader2, AlertTriangle, RefreshCw, CheckCircle, FileImage } from 'lucide-react'

function DiseaseDetection() {
  const [file, setFile]       = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef(null)

  const validate = (f) => {
    setError(null); setResult(null)
    if (!f) return false
    if (!['image/jpeg','image/png','image/jpg'].includes(f.type)) {
      setError('Unsupported format. Please upload JPG or PNG.'); return false
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10 MB limit.'); return false
    }
    return true
  }

  const pick = (f) => { if (validate(f)) { setFile(f); setPreview(URL.createObjectURL(f)) } }
  const handleInput = (e) => { if (e.target.files?.[0]) pick(e.target.files[0]) }
  const handleDrag  = (e) => {
    e.preventDefault(); e.stopPropagation()
    setDragActive(e.type === 'dragenter' || e.type === 'dragover')
  }
  const handleDrop  = (e) => {
    e.preventDefault(); e.stopPropagation(); setDragActive(false)
    if (e.dataTransfer.files?.[0]) pick(e.dataTransfer.files[0])
  }

  const reset = () => { setFile(null); setPreview(null); setResult(null); setError(null); if (inputRef.current) inputRef.current.value = '' }

  const analyze = async () => {
    if (!file) return
    setLoading(true); setError(null)
    const fd = new FormData(); fd.append('image', file)
    try {
      const r = await axios.post('http://localhost:8000/api/disease/predict/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setResult(r.data)
    } catch (err) {
      setError(err.response?.data?.error ?? 'Failed to connect to backend. Please ensure the Django API is running.')
    } finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <ScanLine size={26} className="text-forest-600" /> Crop Disease Detection
          </h1>
          <p className="page-subtitle">Upload a leaf image · ResNet18 inference · Development prototype</p>
        </div>
        <span className="badge-proto">Prototype</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload panel */}
        <div className="agri-card space-y-4">
          <h2 className="font-semibold text-forest-900">Upload Field Photograph</h2>

          {!file ? (
            <div
              className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag} onDragLeave={handleDrag}
              onDragOver={handleDrag} onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
              role="button" tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
              aria-label="Upload crop image"
            >
              <UploadCloud size={44} className="mx-auto mb-3 text-forest-400" />
              <p className="font-semibold text-forest-700 mb-1">Click to browse or drop field photograph here</p>
              <p className="text-xs text-forest-500">Supported formats: JPG, JPEG, PNG · Max 10 MB</p>
              <input ref={inputRef} type="file" className="hidden" accept="image/jpeg,image/png,image/jpg" onChange={handleInput} />
            </div>
          ) : (
            <div className="space-y-4">
              <div className="relative rounded-xl overflow-hidden border border-forest-200">
                <img src={preview} alt="Crop leaf preview" className="w-full object-contain max-h-64" />
                <div className="absolute top-2 left-2">
                  <span className="badge bg-black/60 text-white text-[10px]">
                    <FileImage size={10} /> {file.name}
                  </span>
                </div>
              </div>
              <div className="flex gap-3">
                <button className="btn-secondary" onClick={reset}>Cancel</button>
                {!result && !loading && (
                  <button className="btn-primary flex-1 justify-center" onClick={analyze}>
                    <ScanLine size={16} /> Analyse Disease
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

        {/* Results panel */}
        <div className="agri-card flex flex-col">
          <h2 className="font-semibold text-forest-900 mb-4">Pathogen Identification</h2>

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 py-12 text-forest-600">
              <Loader2 size={36} className="spin" />
              <span className="text-sm font-medium">Running Inference Pipeline…</span>
            </div>
          )}

          {!loading && !result && !error && (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-forest-400">
              <ScanLine size={36} className="mb-3 opacity-40" />
              <p className="text-sm">Upload and analyse an image to see results here.</p>
            </div>
          )}

          {result && !loading && (
            <div className="slide-up space-y-4">
              <div className="flex items-center gap-3">
                <CheckCircle size={24} className="text-forest-500" />
                <div>
                  <div className="text-xl font-bold text-forest-900 capitalize">{result.predicted_class}</div>
                  {result.confidence && (
                    <div className="text-sm text-forest-600">
                      Confidence: <strong>{(result.confidence * 100).toFixed(1)}%</strong>
                    </div>
                  )}
                </div>
              </div>

              {/* Confidence bar */}
              {result.confidence && (
                <div>
                  <div className="flex justify-between text-xs text-forest-500 mb-1">
                    <span>Model Confidence</span>
                    <span>{(result.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="h-2 bg-forest-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-forest-500 rounded-full transition-all duration-700"
                      style={{ width: `${(result.confidence * 100).toFixed(1)}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="proto-banner">
                <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                <div>
                  <strong>Development Prototype</strong>
                  <p className="mt-0.5">{result.warning}</p>
                </div>
              </div>

              <button className="btn-secondary w-full justify-center" onClick={reset}>
                <RefreshCw size={15} /> Scan Another Image
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DiseaseDetection
