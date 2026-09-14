import React, { useState, useEffect } from 'react'
import { Cloud, ThermometerSun, AlertTriangle, RefreshCw, Search, CloudRain, Wind, Droplets, Sun, Moon, MapPin, CheckCircle, Info, Calendar } from 'lucide-react'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'

function WeatherIntelligence() {
  const { user } = useAuth()
  
  const defaultCity = user?.has_farm_profile ? user.farm_location : ''
  const [city, setCity] = useState(defaultCity)
  const [loading, setLoading] = useState(false)
  const [currentWeather, setCurrentWeather] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (defaultCity) {
      fetchWeatherData(defaultCity)
    }
  }, [defaultCity])

  const fetchWeatherData = async (searchCity) => {
    if (!searchCity) {
      setError('Please enter a location.')
      return
    }
    setLoading(true)
    setError(null)
    setCurrentWeather(null)
    setForecast(null)
    
    try {
      const currentRes = await api.get(`/weather/current/?city=${encodeURIComponent(searchCity)}`)
      setCurrentWeather(currentRes.data)
      
      try {
        const forecastRes = await api.get(`/weather/forecast/?city=${encodeURIComponent(searchCity)}`)
        setForecast(forecastRes.data)
      } catch (err) {
        console.warn('Forecast unavailable', err)
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Weather data is temporarily unavailable.')
    } finally {
      setLoading(false)
    }
  }

  const submit = (e) => {
    e.preventDefault()
    fetchWeatherData(city)
  }

  const formatTime = (timestamp) => {
    if (!timestamp) return '--:--'
    return new Date(timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  
  const formatDate = (timestamp) => {
    if (!timestamp) return '--'
    return new Date(timestamp * 1000).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const getInsights = (weather) => {
    if (!weather) return []
    const insights = []
    
    if (weather.rainfall > 5) {
      insights.push({ type: 'warning', text: 'Heavy rainfall detected. Postpone fertilizer application to prevent runoff.' })
    }
    if (weather.temperature > 32) {
      insights.push({ type: 'warning', text: 'High heat stress risk. Ensure adequate irrigation.' })
    } else if (weather.temperature < 5) {
      insights.push({ type: 'warning', text: 'Frost risk. Protect sensitive crops.' })
    }
    if (weather.wind_speed > 25) {
      insights.push({ type: 'warning', text: 'High winds. Avoid spraying chemicals.' })
    }
    if (weather.humidity > 85) {
      insights.push({ type: 'warning', text: 'High humidity. Monitor for fungal diseases.' })
    }
    
    if (insights.length === 0) {
      insights.push({ type: 'success', text: 'Weather conditions are optimal for routine field operations.' })
    }
    
    return insights
  }

  const insights = getInsights(currentWeather)

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Cloud size={26} className="text-blue-500" /> Weather Intelligence
          </h1>
          <p className="page-subtitle">Real-time professional agricultural weather data</p>
        </div>
        <div className="flex flex-col items-end gap-1 text-xs text-forest-500 dark:text-forest-400">
            {currentWeather && (
                <>
                    <span className="flex items-center gap-1"><Info size={12}/> Data Source: OpenWeather API</span>
                    <span>Updated: {formatTime(currentWeather.timestamp)}</span>
                    {currentWeather.cached && <span className="bg-forest-100 dark:bg-forest-800 px-2 py-0.5 rounded text-forest-600 dark:text-forest-300">Cached (15m)</span>}
                </>
            )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="agri-card dark:bg-forest-900 dark:border-forest-800">
            <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
                <MapPin size={18} className="text-harvest-500" /> Location
            </h2>
            <form onSubmit={submit} className="space-y-4">
              <div>
                <label className="agri-label dark:text-forest-400">City / Farm Location</label>
                <div className="relative">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-forest-400" />
                  <input 
                    className="agri-input pl-9 dark:bg-forest-950 dark:border-forest-700 dark:text-white" 
                    type="text" 
                    value={city} 
                    onChange={e => setCity(e.target.value)} 
                    placeholder="e.g. Pune" 
                    required 
                  />
                </div>
                {user?.has_farm_profile && city === user.farm_location && (
                    <p className="text-xs text-forest-500 mt-1 flex items-center gap-1">
                        <CheckCircle size={12} className="text-forest-500"/> Saved farm location
                    </p>
                )}
              </div>
              <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
                {loading ? 'Fetching...' : 'Fetch Weather'}
              </button>
            </form>
            {error && (
              <div className="error-banner mt-4">
                <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                <div className="text-sm">{error}</div>
              </div>
            )}
          </div>
          
          {currentWeather && (
             <div className="agri-card dark:bg-forest-900 dark:border-forest-800">
                <h3 className="font-semibold text-forest-900 dark:text-forest-100 mb-3 flex items-center gap-2 text-sm">
                   <Info size={16} className="text-blue-500" /> Rule-based Guidance
                </h3>
                <div className="space-y-2">
                    {insights.map((ins, idx) => (
                        <div key={idx} className={`p-3 rounded-lg border-l-4 text-sm flex gap-2 ${ins.type === 'warning' ? 'bg-orange-50 border-orange-400 text-orange-800 dark:bg-orange-900/20 dark:text-orange-200' : 'bg-forest-50 border-forest-500 text-forest-800 dark:bg-forest-900/40 dark:border-forest-400 dark:text-forest-200'}`}>
                            {ins.type === 'warning' ? <AlertTriangle size={16} className="flex-shrink-0 mt-0.5"/> : <CheckCircle size={16} className="flex-shrink-0 mt-0.5" />}
                            <span>{ins.text}</span>
                        </div>
                    ))}
                </div>
                <p className="text-xs text-forest-400 mt-3 italic">This guidance is rule-based and not a professional advisory.</p>
             </div>
          )}
        </div>

        <div className="lg:col-span-3 space-y-6">
          {!currentWeather && !loading && !error && (
            <div className="agri-card flex flex-col items-center justify-center py-20 text-forest-400 dark:bg-forest-900 dark:border-forest-800">
              <Cloud size={48} className="mb-4 opacity-40" />
              <p>Enter a location to view live weather data.</p>
            </div>
          )}
          
          {loading && (
             <div className="agri-card flex flex-col items-center justify-center py-20 text-forest-500 dark:bg-forest-900 dark:border-forest-800">
                <RefreshCw size={32} className="spin mb-3" />
                <p>Connecting to OpenWeather...</p>
             </div>
          )}

          {currentWeather && (
            <div className="space-y-6 slide-up">
                {/* Current Weather Card */}
                <div className="agri-card dark:bg-forest-900 dark:border-forest-800">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h2 className="text-2xl font-bold text-forest-900 dark:text-white capitalize">{currentWeather.location}</h2>
                            <p className="text-forest-500 dark:text-forest-400 capitalize">{currentWeather.description}</p>
                        </div>
                        <div className="text-right">
                            <div className="text-4xl font-bold text-forest-900 dark:text-white">{Math.round(currentWeather.temperature)}°C</div>
                            <p className="text-sm text-forest-500 dark:text-forest-400">Feels like {Math.round(currentWeather.feels_like)}°C</p>
                        </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-3 bg-forest-50 dark:bg-forest-950 rounded-xl border border-forest-100 dark:border-forest-800 flex items-center gap-3">
                            <Droplets size={24} className="text-blue-500" />
                            <div>
                                <p className="text-xs text-forest-500 dark:text-forest-400">Humidity</p>
                                <p className="font-semibold text-forest-900 dark:text-white">{currentWeather.humidity ?? '--'}%</p>
                            </div>
                        </div>
                        <div className="p-3 bg-forest-50 dark:bg-forest-950 rounded-xl border border-forest-100 dark:border-forest-800 flex items-center gap-3">
                            <Wind size={24} className="text-gray-500" />
                            <div>
                                <p className="text-xs text-forest-500 dark:text-forest-400">Wind</p>
                                <p className="font-semibold text-forest-900 dark:text-white">{currentWeather.wind_speed ?? '--'} m/s</p>
                            </div>
                        </div>
                        <div className="p-3 bg-forest-50 dark:bg-forest-950 rounded-xl border border-forest-100 dark:border-forest-800 flex items-center gap-3">
                            <CloudRain size={24} className="text-blue-400" />
                            <div>
                                <p className="text-xs text-forest-500 dark:text-forest-400">Rain (1h)</p>
                                <p className="font-semibold text-forest-900 dark:text-white">{currentWeather.rainfall ?? '0'} mm</p>
                            </div>
                        </div>
                        <div className="p-3 bg-forest-50 dark:bg-forest-950 rounded-xl border border-forest-100 dark:border-forest-800 flex items-center gap-3">
                            <Cloud size={24} className="text-gray-400" />
                            <div>
                                <p className="text-xs text-forest-500 dark:text-forest-400">Clouds</p>
                                <p className="font-semibold text-forest-900 dark:text-white">{currentWeather.clouds ?? '--'}%</p>
                            </div>
                        </div>
                        <div className="p-3 bg-forest-50 dark:bg-forest-950 rounded-xl border border-forest-100 dark:border-forest-800 flex items-center gap-3">
                            <ThermometerSun size={24} className="text-orange-500" />
                            <div>
                                <p className="text-xs text-forest-500 dark:text-forest-400">Min/Max</p>
                                <p className="font-semibold text-forest-900 dark:text-white">{currentWeather.temp_min ? Math.round(currentWeather.temp_min) : '--'}° / {currentWeather.temp_max ? Math.round(currentWeather.temp_max) : '--'}°</p>
                            </div>
                        </div>
                        <div className="p-3 bg-forest-50 dark:bg-forest-950 rounded-xl border border-forest-100 dark:border-forest-800 flex items-center gap-3">
                            <Info size={24} className="text-forest-400" />
                            <div>
                                <p className="text-xs text-forest-500 dark:text-forest-400">Pressure</p>
                                <p className="font-semibold text-forest-900 dark:text-white">{currentWeather.pressure ?? '--'} hPa</p>
                            </div>
                        </div>
                        <div className="p-3 bg-forest-50 dark:bg-forest-950 rounded-xl border border-forest-100 dark:border-forest-800 flex items-center gap-3">
                            <Sun size={24} className="text-yellow-500" />
                            <div>
                                <p className="text-xs text-forest-500 dark:text-forest-400">Sunrise</p>
                                <p className="font-semibold text-forest-900 dark:text-white">{formatTime(currentWeather.sunrise)}</p>
                            </div>
                        </div>
                        <div className="p-3 bg-forest-50 dark:bg-forest-950 rounded-xl border border-forest-100 dark:border-forest-800 flex items-center gap-3">
                            <Moon size={24} className="text-indigo-400" />
                            <div>
                                <p className="text-xs text-forest-500 dark:text-forest-400">Sunset</p>
                                <p className="font-semibold text-forest-900 dark:text-white">{formatTime(currentWeather.sunset)}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Forecast section */}
                {forecast && forecast.forecast && forecast.forecast.length > 0 ? (
                    <div className="agri-card dark:bg-forest-900 dark:border-forest-800">
                        <h2 className="font-semibold text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
                            <Calendar size={18} className="text-blue-500" /> 5-Day Forecast (3-Hour Intervals)
                        </h2>
                        <div className="flex overflow-x-auto gap-3 pb-2 custom-scrollbar">
                            {forecast.forecast.slice(0, 15).map((f, i) => (
                                <div key={i} className="flex-shrink-0 w-32 p-3 bg-forest-50 dark:bg-forest-950 rounded-xl border border-forest-100 dark:border-forest-800 flex flex-col items-center text-center">
                                    <p className="text-xs font-semibold text-forest-700 dark:text-forest-300 mb-1">{formatDate(f.timestamp)}</p>
                                    <Cloud size={24} className="text-forest-400 my-2" />
                                    <p className="text-lg font-bold text-forest-900 dark:text-white">{Math.round(f.temperature)}°C</p>
                                    <p className="text-xs text-forest-500 dark:text-forest-400 capitalize">{f.condition}</p>
                                    {f.rain_prob > 0 && <p className="text-xs text-blue-500 mt-1">{Math.round(f.rain_prob * 100)}% Rain</p>}
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="agri-card py-8 text-center text-forest-500 dark:bg-forest-900 dark:border-forest-800 dark:text-forest-400">
                        Forecast data is currently unavailable.
                    </div>
                )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default WeatherIntelligence
