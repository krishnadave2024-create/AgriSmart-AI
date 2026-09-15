dashboard_jsx = """
import React, { useState, useEffect } from 'react'
import { ScanLine, Leaf, Droplets, Globe, Shield, Activity, Info, Loader2, AlertTriangle, AlertCircle, CheckCircle, Cloud, Wind, Thermometer, Sunrise, Sunset, Navigation } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'

function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [weather, setWeather] = useState(null);
  const [weatherError, setWeatherError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [dashRes, weatherRes] = await Promise.all([
            api.get('dashboard/summary/'),
            api.get('weather/navbar/').catch(() => ({ data: { error: 'Weather API failed' } }))
        ]);
        
        setData(dashRes.data);
        
        if (weatherRes.data && weatherRes.data.success) {
            setWeather(weatherRes.data);
        } else {
            setWeatherError(weatherRes.data?.error || 'Weather unavailable');
        }
      } catch (err) {
        console.error(err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-forest-600">
        <Loader2 className="animate-spin mb-4" size={32} />
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100 flex items-center gap-2">
        <AlertTriangle size={20} />
        {error}
      </div>
    );
  }

  const { metrics, analytics, needs_attention, insights, recent_activities } = data;
  
  // Format disease chart data
  const diseaseChartData = [
    { name: 'Healthy', value: metrics.healthy_scans, color: '#22c55e' },
    { name: 'Diseased', value: metrics.diseased_scans, color: '#ef4444' }
  ];

  return (
    <div className="space-y-6 w-full">
      
      {/* Full-Width Header & Weather Panel */}
      <div className="bg-forest-900 dark:bg-forest-950 rounded-2xl p-6 text-white shadow-lg overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-forest-800 rounded-full blur-3xl opacity-20 -mr-20 -mt-20"></div>
        <div className="relative z-10 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
            
            <div>
              <h1 className="text-3xl font-bold mb-1">
                Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'}, {user?.full_name || user?.username}
              </h1>
              <div className="flex items-center gap-2 text-forest-200">
                <Navigation size={16} />
                <span>
                    {user?.has_farm_profile && user?.farm_name ? user.farm_name : 'Farm profile incomplete'} 
                    {metrics.location ? ` • ${metrics.location}` : ''}
                </span>
              </div>
              <div className="text-forest-300 text-sm mt-4">
                  {new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
              </div>
            </div>

            {/* Weather Widget */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 min-w-[300px] border border-white/10">
                {weather ? (
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="text-4xl font-bold">{weather.temp.toFixed(1)}°C</div>
                            <div className="text-forest-200 capitalize text-sm">{weather.description}</div>
                            <div className="flex items-center gap-3 mt-2 text-xs text-forest-300">
                                <span className="flex items-center gap-1"><Wind size={12}/> {weather.wind_speed} m/s</span>
                                <span className="flex items-center gap-1"><Droplets size={12}/> {weather.humidity}%</span>
                            </div>
                        </div>
                        <div className="w-16 h-16 flex items-center justify-center bg-white/20 rounded-full">
                            <Cloud size={32} />
                        </div>
                    </div>
                ) : (
                    <div className="text-forest-200 flex flex-col items-center justify-center py-2">
                        <AlertCircle size={24} className="mb-2 opacity-50" />
                        <span className="text-sm">{weatherError === 'Farm city not set.' ? 'Update farm city to view weather' : 'Weather service unavailable'}</span>
                    </div>
                )}
            </div>

        </div>
      </div>

      {/* Farm Status & Quick Actions row */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        
        {/* Farm Status / Data Readiness */}
        <div className="agri-card lg:col-span-1 bg-gradient-to-br from-forest-50 to-white dark:from-forest-900/50 dark:to-forest-950 border-forest-100 dark:border-forest-800">
            <h3 className="font-bold text-forest-900 dark:text-forest-100 mb-3 text-sm">Data Readiness</h3>
            <ul className="space-y-2 text-xs">
                <li className="flex items-center justify-between">
                    <span className="text-forest-600 dark:text-forest-400">Farm Profile</span>
                    {metrics.missing_profile ? <span className="text-red-500 font-medium">Incomplete</span> : <span className="text-green-500 font-medium">Complete</span>}
                </li>
                <li className="flex items-center justify-between">
                    <span className="text-forest-600 dark:text-forest-400">Disease History</span>
                    {metrics.total_disease_scans > 0 ? <span className="text-green-500 font-medium">Available</span> : <span className="text-forest-400">None</span>}
                </li>
                <li className="flex items-center justify-between">
                    <span className="text-forest-600 dark:text-forest-400">FieldGuard Data</span>
                    {metrics.latest_fieldguard_score ? <span className="text-green-500 font-medium">Available</span> : <span className="text-forest-400">None</span>}
                </li>
            </ul>
        </div>

        {/* Quick Actions */}
        <div className="agri-card lg:col-span-3">
            <h3 className="font-bold text-forest-900 dark:text-forest-100 mb-3 text-sm">Quick Actions</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
                { to: '/disease', icon: ScanLine, label: 'Scan Leaf', color: 'bg-forest-100 text-forest-700 dark:bg-forest-900/40 dark:text-forest-300' },
                { to: '/crops', icon: Leaf, label: 'Recommend Crop', color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300' },
                { to: '/irrigation', icon: Droplets, label: 'Irrigation', color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' },
                { to: '/fieldguard', icon: Shield, label: 'FieldGuard', color: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300' },
            ].map((item) => {
                const Icon = item.icon
                return (
                <NavLink
                    key={item.to}
                    to={item.to}
                    className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg ${item.color} hover:opacity-80 transition-opacity text-center no-underline text-xs font-semibold`}
                >
                    <Icon size={16} />
                    <span>{item.label}</span>
                </NavLink>
                )
            })}
            </div>
        </div>
      </div>

      {/* Full-Width Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 w-full">
        <div className="metric-card">
          <div className="flex justify-between items-start mb-2">
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">Disease Scans</div>
            <ScanLine size={16} className="text-forest-500" />
          </div>
          <div className="text-3xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.total_disease_scans > 0 ? metrics.total_disease_scans : '-'}
          </div>
          <div className="text-[11px] text-forest-500 dark:text-forest-400 mt-2 truncate bg-forest-50 dark:bg-forest-900/30 px-2 py-1 rounded">
            {metrics.total_disease_scans > 0 ? `Latest: ${metrics.latest_disease_class || 'N/A'}` : 'No scans yet'}
          </div>
        </div>

        <div className="metric-card">
          <div className="flex justify-between items-start mb-2">
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">Crop Advice</div>
            <Leaf size={16} className="text-emerald-500" />
          </div>
          <div className="text-3xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.total_crop_recommendations > 0 ? metrics.total_crop_recommendations : '-'}
          </div>
          <div className="text-[11px] text-forest-500 dark:text-forest-400 mt-2 truncate bg-emerald-50 dark:bg-emerald-900/30 px-2 py-1 rounded">
            {metrics.total_crop_recommendations > 0 ? `Latest: ${metrics.latest_crop_rec || 'N/A'}` : 'No records yet'}
          </div>
        </div>

        <div className="metric-card">
          <div className="flex justify-between items-start mb-2">
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">Irrigation</div>
            <Droplets size={16} className="text-blue-500" />
          </div>
          <div className="text-3xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.total_irrigation_assessments > 0 ? metrics.total_irrigation_assessments : '-'}
          </div>
          <div className="text-[11px] text-forest-500 dark:text-forest-400 mt-2 truncate bg-blue-50 dark:bg-blue-900/30 px-2 py-1 rounded">
            {metrics.total_irrigation_assessments > 0 ? `Assessments run` : 'No assessments'}
          </div>
        </div>

        <div className="metric-card">
          <div className="flex justify-between items-start mb-2">
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">FieldGuard Risk</div>
            <Shield size={16} className="text-orange-500" />
          </div>
          <div className="text-3xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.latest_fieldguard_score !== null ? Math.round(metrics.latest_fieldguard_score) : '-'}
          </div>
          <div className="text-[11px] text-forest-500 dark:text-forest-400 mt-2 truncate bg-orange-50 dark:bg-orange-900/30 px-2 py-1 rounded">
            {metrics.latest_fieldguard_score !== null ? `Category: ${metrics.latest_fieldguard_category}` : 'No score'}
          </div>
        </div>

        <div className="metric-card">
          <div className="flex justify-between items-start mb-2">
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">Sustainability</div>
            <Globe size={16} className="text-harvest-500" />
          </div>
          <div className="text-3xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.latest_sustainability_score !== null ? Math.round(metrics.latest_sustainability_score) : '-'}
          </div>
          <div className="text-[11px] text-forest-500 dark:text-forest-400 mt-2 truncate bg-harvest-50 dark:bg-harvest-900/30 px-2 py-1 rounded">
            {metrics.latest_sustainability_score !== null ? `Category: ${metrics.latest_sustainability_category}` : 'No assessment'}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 w-full">
        {/* Main Analytics Area - Much Wider */}
        <div className="xl:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-xl text-forest-900 dark:text-forest-100">Farm Analytics</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Activity Trend */}
            <div className="agri-card flex flex-col h-80">
              <h3 className="text-sm font-semibold text-forest-800 dark:text-forest-200 mb-4">Activity Trend (30 Days)</h3>
              <div className="flex-1 w-full">
                {analytics.activity_trend.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={analytics.activity_trend}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.5} />
                      <XAxis dataKey="date" tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <YAxis allowDecimals={false} tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <RechartsTooltip cursor={{fill: 'rgba(0,0,0,0.05)'}} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                      <Bar dataKey="count" name="Activities" fill="#22c55e" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-forest-500 dark:text-forest-400">
                    Not enough historical activity for a trend
                  </div>
                )}
              </div>
            </div>

            {/* Disease Breakdown */}
            <div className="agri-card flex flex-col h-80">
              <h3 className="text-sm font-semibold text-forest-800 dark:text-forest-200 mb-4">Disease Analysis</h3>
              <div className="flex-1 w-full">
                {metrics.total_disease_scans > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={diseaseChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={65}
                        outerRadius={90}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {diseaseChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-forest-500 dark:text-forest-400">
                    No disease scans recorded yet
                  </div>
                )}
              </div>
              {metrics.total_disease_scans > 0 && (
                <div className="flex justify-center gap-6 mt-4">
                  <div className="flex items-center gap-2 text-sm text-forest-700 dark:text-forest-300">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div> Healthy
                  </div>
                  <div className="flex items-center gap-2 text-sm text-forest-700 dark:text-forest-300">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div> Diseased
                  </div>
                </div>
              )}
            </div>
            
            {/* FieldGuard Trend */}
            <div className="agri-card flex flex-col h-80 md:col-span-2">
              <h3 className="text-sm font-semibold text-forest-800 dark:text-forest-200 mb-4">FieldGuard Risk Trend</h3>
              <div className="flex-1 w-full">
                {analytics.fieldguard_trend.length > 1 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={analytics.fieldguard_trend}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.5} />
                      <XAxis dataKey="date" tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 100]} tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                      <Line type="monotone" dataKey="score" name="Risk Score (Higher = Lower Risk)" stroke="#f59e0b" strokeWidth={3} dot={{r: 4}} activeDot={{r: 6}} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-sm text-forest-500 dark:text-forest-400 text-center px-4">
                    <Shield size={32} className="mb-3 opacity-30" />
                    Not enough historical data for analytics (requires multiple assessments)
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>

        {/* Right Sidebar Area */}
        <div className="space-y-6">
          
          {/* Needs Attention */}
          <div className="agri-card border-amber-200 dark:border-amber-900/50">
            <h2 className="font-bold text-lg text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <AlertCircle size={20} className="text-amber-500" /> Needs Attention
            </h2>
            <div className="space-y-3">
              {needs_attention && needs_attention.length > 0 ? (
                needs_attention.map((item, idx) => (
                  <div key={idx} className={`p-3 rounded-xl border flex flex-col gap-2 ${
                    item.severity === 'error' ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200' :
                    item.severity === 'warning' ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200' :
                    item.severity === 'success' ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200' :
                    'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'
                  }`}>
                    <div className="text-sm font-medium">{item.reason}</div>
                    <NavLink to={item.link} className="text-xs font-bold underline opacity-80 hover:opacity-100 inline-block w-fit">
                      {item.action} →
                    </NavLink>
                  </div>
                ))
              ) : (
                <div className="text-sm text-forest-500 dark:text-forest-400 p-4 bg-forest-50 dark:bg-forest-900/30 rounded-xl text-center">
                  No urgent actions detected from your available records.
                </div>
              )}
            </div>
          </div>

          {/* Farm Insights */}
          <div className="agri-card">
            <h2 className="font-bold text-lg text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <Info size={20} className="text-blue-500" /> Farm Insights
            </h2>
            {insights && insights.length > 0 ? (
              <ul className="space-y-3 text-sm text-forest-700 dark:text-forest-300">
                {insights.map((insight, idx) => (
                  <li key={idx} className="flex gap-3 items-start bg-forest-50 dark:bg-forest-900/30 p-3 rounded-xl">
                    <CheckCircle size={16} className="text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="leading-snug">{insight}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-sm text-forest-500 dark:text-forest-400 text-center p-4">
                Complete your farm profile and run assessments to generate insights.
              </div>
            )}
          </div>

          {/* Recent Activity Timeline */}
          <div className="agri-card">
            <h2 className="font-bold text-lg text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <Activity size={20} className="text-forest-500" /> Recent Activity
            </h2>
            <div className="space-y-0 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-forest-200 dark:before:via-forest-700 before:to-transparent">
              {recent_activities && recent_activities.length > 0 ? (
                recent_activities.map((a, i) => (
                  <div key={i} className="relative flex items-start gap-4 py-3 group">
                    <div className="w-4 h-4 rounded-full bg-forest-200 dark:bg-forest-700 border-2 border-white dark:border-forest-950 mt-1 relative z-10 group-hover:bg-forest-500 transition-colors flex-shrink-0" />
                    <div className="flex-1 min-w-0 bg-white dark:bg-forest-900/50 p-3 rounded-xl border border-forest-100 dark:border-forest-800 shadow-sm">
                      <div className="text-sm font-semibold text-forest-900 dark:text-forest-100 leading-snug">{a.title}</div>
                      {a.description && <div className="text-xs text-forest-600 dark:text-forest-400 mt-1">{a.description}</div>}
                      <div className="text-[10px] font-medium text-forest-400 dark:text-forest-500 mt-2 uppercase tracking-wider">{new Date(a.created_at).toLocaleString()}</div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-forest-500 dark:text-forest-400 text-sm">
                  No activity recorded yet. Start by completing a disease scan or farm assessment.
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default Dashboard
"""
with open('frontend/src/components/Dashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(dashboard_jsx)
print("Dashboard.jsx full width update completed")
