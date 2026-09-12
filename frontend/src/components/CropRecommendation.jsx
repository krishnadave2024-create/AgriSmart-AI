import { useState } from 'react'
import axios from 'axios'
import { Loader2, AlertTriangle, Leaf, RefreshCw } from 'lucide-react'

function CropRecommendation() {
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    ph: '',
    temperature: '',
    humidity: '',
    rainfall: ''
  })
  
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const resetForm = () => {
    setFormData({
      nitrogen: '', phosphorus: '', potassium: '', ph: '',
      temperature: '', humidity: '', rainfall: ''
    })
    setResult(null)
    setError(null)
  }

  const submitForm = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    
    try {
      const response = await axios.post('http://localhost:8000/api/crops/recommend/', formData)
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
    <div className="card">
      <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem'}}>
        <Leaf size={32} color="var(--primary-color)" />
        <h2 style={{margin: 0}}>Crop Recommendation</h2>
      </div>

      {!result ? (
        <form onSubmit={submitForm} className="form-grid">
          <div className="form-group">
            <label>Nitrogen (N)</label>
            <input type="number" name="nitrogen" value={formData.nitrogen} onChange={handleInputChange} required min="0" />
          </div>
          <div className="form-group">
            <label>Phosphorus (P)</label>
            <input type="number" name="phosphorus" value={formData.phosphorus} onChange={handleInputChange} required min="0" />
          </div>
          <div className="form-group">
            <label>Potassium (K)</label>
            <input type="number" name="potassium" value={formData.potassium} onChange={handleInputChange} required min="0" />
          </div>
          <div className="form-group">
            <label>Soil pH</label>
            <input type="number" step="0.1" name="ph" value={formData.ph} onChange={handleInputChange} required min="0" max="14" />
          </div>
          <div className="form-group">
            <label>Temperature (°C)</label>
            <input type="number" step="0.1" name="temperature" value={formData.temperature} onChange={handleInputChange} required />
          </div>
          <div className="form-group">
            <label>Humidity (%)</label>
            <input type="number" step="0.1" name="humidity" value={formData.humidity} onChange={handleInputChange} required min="0" max="100" />
          </div>
          <div className="form-group">
            <label>Rainfall (mm)</label>
            <input type="number" step="0.1" name="rainfall" value={formData.rainfall} onChange={handleInputChange} required min="0" />
          </div>
          
          <div style={{gridColumn: '1 / -1', marginTop: '1rem'}}>
            <button type="submit" className="btn" disabled={loading} style={{width: '100%', justifyContent: 'center'}}>
              {loading ? <Loader2 className="loader" size={20} /> : "Recommend Crops"}
            </button>
          </div>
          
          {error && (
            <div className="error-banner" style={{gridColumn: '1 / -1', marginTop: '1rem'}}>
              <AlertTriangle size={20} /> {error}
            </div>
          )}
        </form>
      ) : (
        <div className="result-container" style={{animation: 'slideUp 0.5s ease'}}>
          <h3 style={{marginTop: 0, color: 'var(--primary-color)'}}>Top Recommendations</h3>
          
          <div className="recommendations-list">
            {result.recommendations.map((rec, idx) => (
              <div key={idx} className="rec-card">
                <div className="rec-header">
                  <span className="rec-crop">{rec.crop}</span>
                  <span className="rec-score">Score: {rec.suitability_score}</span>
                </div>
                <p className="rec-reason">{rec.reason}</p>
              </div>
            ))}
          </div>
          
          <div className="warning-banner" style={{marginTop: '2rem'}}>
            <AlertTriangle size={24} style={{flexShrink: 0}} />
            <div style={{textAlign: 'left'}}>
              <strong>Development Prototype</strong>
              <p style={{margin: '0.25rem 0 0 0'}}>{result.warning}</p>
            </div>
          </div>
          
          <button className="btn" onClick={resetForm} style={{marginTop: '2rem'}}>
            <RefreshCw size={18} /> New Recommendation
          </button>
        </div>
      )}
    </div>
  )
}

export default CropRecommendation
