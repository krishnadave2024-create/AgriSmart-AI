import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { UploadCloud, Image as ImageIcon, Loader2, AlertTriangle, Moon, Sun, RefreshCw } from 'lucide-react'
import '../App.css'

function DiseaseDetection() {
  const [theme, setTheme] = useState('light')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  
  const inputRef = useRef(null)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(t => t === 'light' ? 'dark' : 'light')
  }

  const validateFile = (selectedFile) => {
    setError(null)
    setResult(null)
    if (!selectedFile) return false
    
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg']
    if (!validTypes.includes(selectedFile.type)) {
      setError("Unsupported file format. Please upload JPG or PNG.")
      return false
    }
    
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File size exceeds 10MB limit.")
      return false
    }
    
    return true
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (validateFile(selectedFile)) {
        setFile(selectedFile)
        setPreview(URL.createObjectURL(selectedFile))
      }
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selectedFile = e.dataTransfer.files[0]
      if (validateFile(selectedFile)) {
        setFile(selectedFile)
        setPreview(URL.createObjectURL(selectedFile))
      }
    }
  }

  const resetState = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
    if (inputRef.current) inputRef.current.value = ""
  }

  const analyzeImage = async () => {
    if (!file) return
    
    setLoading(true)
    setError(null)
    
    const formData = new FormData()
    formData.append('image', file)
    
    try {
      const response = await axios.post('http://localhost:8000/api/disease/predict/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      setResult(response.data)
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error)
      } else {
        setError("Failed to connect to the backend server. Please ensure the Django API is running.")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard-container">
      <header>
        <h1>AgriSmart AI</h1>
        <button className="theme-toggle" onClick={toggleTheme}>
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
      </header>

      <main className="card">
        {!file ? (
          <div 
            className={`upload-area ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
          >
            <UploadCloud className="upload-icon" size={48} />
            <h2>Upload a Crop Leaf Image</h2>
            <p style={{color: 'var(--text-secondary)'}}>Drag and drop an image here, or click to select a file</p>
            <p style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>Supports JPG, JPEG, PNG up to 10MB</p>
            <input 
              ref={inputRef}
              type="file" 
              className="file-input" 
              accept="image/jpeg, image/png, image/jpg"
              onChange={handleFileChange} 
            />
          </div>
        ) : (
          <div className="preview-container">
            <img src={preview} alt="Crop Leaf Preview" className="image-preview" />
            
            {!result && !loading && (
              <div style={{display: 'flex', gap: '1rem'}}>
                <button className="btn btn-secondary" onClick={resetState}>
                  Cancel
                </button>
                <button className="btn" onClick={analyzeImage}>
                  Analyze Disease
                </button>
              </div>
            )}
            
            {loading && (
              <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary-color)'}}>
                <Loader2 className="loader" size={24} />
                <span>Running Inference Pipeline...</span>
              </div>
            )}
            
            {error && (
              <div style={{color: 'var(--danger)', textAlign: 'center', maxWidth: '500px'}}>
                <AlertTriangle size={32} style={{marginBottom: '0.5rem'}} />
                <p>{error}</p>
                <button className="btn btn-secondary" onClick={resetState} style={{marginTop: '1rem'}}>
                  Try Again
                </button>
              </div>
            )}
            
            {result && (
              <div className="result-card">
                <div className="disease-name">{result.predicted_class}</div>
                {result.confidence && (
                  <div className="confidence">Confidence: {(result.confidence * 100).toFixed(1)}%</div>
                )}
                
                <div className="warning-banner">
                  <AlertTriangle size={24} style={{flexShrink: 0}} />
                  <div style={{textAlign: 'left'}}>
                    <strong>Development Prototype</strong>
                    <p style={{margin: '0.25rem 0 0 0'}}>{result.warning}</p>
                  </div>
                </div>
                
                <button className="btn" onClick={resetState} style={{marginTop: '2rem'}}>
                  <RefreshCw size={18} /> Analyze Another Image
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default DiseaseDetection
