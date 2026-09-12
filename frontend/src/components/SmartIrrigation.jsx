import { useState } from 'react'
import axios from 'axios'
import { Loader2, AlertTriangle, Droplets, RefreshCw, CloudRain, ThermometerSun } from 'lucide-react'

function SmartIrrigation() {
  const [formData, setFormData] = useState({
    crop: '',
    soil_moisture: '',
    temperature: '',
    humidity: '',
    rainfall: '',
    growth_stage: ''
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
      crop: '', soil_moisture: '', temperature: '',
      humidity: '', rainfall: '', growth_stage: ''
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
      const response = await axios.post('http://localhost:8000/api/irrigation/recommend/', formData)
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
        <Droplets size={32} color="#3b82f6" />
        <h2 style={{margin: 0}}>Smart Irrigation & Weather</h2>
      </div>

      {!result ? (
        <form onSubmit={submitForm} className="form-grid">
          <div className="form-group" style={{gridColumn: '1 / -1'}}>
            <label>Crop Name</label>
            <input type="text" name="crop" value={formData.crop} onChange={handleInputChange} required />
          </div>
          
          <div className="form-group">
            <label>Soil Moisture (%) <span style={{color: 'var(--text-secondary)'}}>(Optional)</span></label>
            <input type="number" step="0.1" name="soil_moisture" value={formData.soil_moisture} onChange={handleInputChange} min="0" max="100" />
          </div>
          
          <div className="form-group">
            <label>Growth Stage</label>
            <select name="growth_stage" value={formData.growth_stage} onChange={handleInputChange}>
              <option value="">Select Stage...</option>
              <option value="seedling">Seedling</option>
              <option value="vegetative">Vegetative</option>
              <option value="flowering">Flowering</option>
              <option value="fruiting">Fruiting / Maturation</option>
            </select>
          </div>

          <h3 style={{gridColumn: '1 / -1', marginTop: '1rem', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '1.1rem'}}>
            Weather Information (Manual Override)
          </h3>

          <div className="form-group">
            <label>Temperature (°C)</label>
            <input type="number" step="0.1" name="temperature" value={formData.temperature} onChange={handleInputChange} required />
          </div>
          
          <div className="form-group">
            <label>Humidity (%) <span style={{color: 'var(--text-secondary)'}}>(Optional)</span></label>
            <input type="number" step="0.1" name="humidity" value={formData.humidity} onChange={handleInputChange} min="0" max="100" />
          </div>
          
          <div className="form-group">
            <label>Rainfall Forecast (mm)</label>
            <input type="number" step="0.1" name="rainfall" value={formData.rainfall} onChange={handleInputChange} required min="0" />
          </div>
          
          <div style={{gridColumn: '1 / -1', marginTop: '1rem'}}>
            <button type="submit" className="btn" disabled={loading} style={{width: '100%', justifyContent: 'center'}}>
              {loading ? <Loader2 className="loader" size={20} /> : "Get Irrigation & Weather Insights"}
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
          
          <div style={{padding: '1.5rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '0.5rem', border: '1px solid rgba(59, 130, 246, 0.3)', marginBottom: '1.5rem'}}>
            <h3 style={{marginTop: 0, color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              Irrigation Priority: {result.irrigation_priority}
            </h3>
            <p><strong>Action:</strong> {result.recommended_action}</p>
            <p style={{color: 'var(--text-secondary)'}}><strong>Reason:</strong> {result.reason}</p>
          </div>

          {result.insights && result.insights.length > 0 && (
            <div style={{marginBottom: '1.5rem'}}>
              <h3 style={{color: 'var(--text-primary)'}}>Weather & Field Insights</h3>
              <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
                {result.insights.map((insight, idx) => (
                  <div key={idx} style={{
                    padding: '1rem', 
                    borderRadius: '0.5rem', 
                    borderLeft: `4px solid ${insight.severity === 'high' ? 'var(--danger)' : insight.severity === 'medium' ? '#f59e0b' : 'var(--primary-color)'}`,
                    background: 'var(--bg-color)'
                  }}>
                    <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem'}}>
                      {insight.type === 'weather' ? <CloudRain size={20} /> : <ThermometerSun size={20} />}
                      <strong>{insight.severity.toUpperCase()} ALERT</strong>
                    </div>
                    <p style={{margin: 0}}>{insight.message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          <div className="warning-banner" style={{marginTop: '2rem'}}>
            <AlertTriangle size={24} style={{flexShrink: 0}} />
            <div style={{textAlign: 'left'}}>
              <strong>Development Prototype</strong>
              <p style={{margin: '0.25rem 0 0 0'}}>{result.warning}</p>
            </div>
          </div>
          
          <button className="btn" onClick={resetForm} style={{marginTop: '2rem'}}>
            <RefreshCw size={18} /> New Analysis
          </button>
        </div>
      )}
    </div>
  )
}

export default SmartIrrigation
