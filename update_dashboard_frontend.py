dashboard_jsx = """
import React, { useState, useEffect } from 'react'
import { ScanLine, Leaf, Droplets, Globe, Shield, Activity, Info, Loader2, AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'

function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await api.get('dashboard/summary/');
        setData(res.data);
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
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page header */}
      <div className="page-header border-b border-forest-100 dark:border-forest-800 pb-4">
        <div>
          <h1 className="page-title text-2xl">
            Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'}, {user?.full_name || user?.username}
          </h1>
          <p className="page-subtitle text-forest-600 dark:text-forest-400 mt-1">
            {user?.has_farm_profile && user?.farm_name ? user.farm_name : 'Farm profile incomplete'} 
            {metrics.location ? ` • ${metrics.location}` : ''}
          </p>
        </div>
        <div className="text-right text-sm text-forest-500 dark:text-forest-400">
            {new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        
        {/* Disease Scans */}
        <div className="metric-card">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-forest-50 dark:bg-forest-900 flex items-center justify-center">
              <ScanLine size={16} className="text-forest-600 dark:text-forest-400" />
            </div>
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">Disease Scans</div>
          </div>
          <div className="text-2xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.total_disease_scans > 0 ? metrics.total_disease_scans : '-'}
          </div>
          <div className="text-xs text-forest-500 dark:text-forest-400 mt-1 truncate">
            {metrics.total_disease_scans > 0 
              ? `Latest: ${metrics.latest_disease_class || 'N/A'}`
              : 'No disease scans recorded yet'}
          </div>
        </div>

        {/* Crop Recommendations */}
        <div className="metric-card">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center">
              <Leaf size={16} className="text-emerald-600 dark:text-emerald-400" />
            </div>
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">Crop Advice</div>
          </div>
          <div className="text-2xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.total_crop_recommendations > 0 ? metrics.total_crop_recommendations : '-'}
          </div>
          <div className="text-xs text-forest-500 dark:text-forest-400 mt-1 truncate">
            {metrics.total_crop_recommendations > 0 
              ? `Latest: ${metrics.latest_crop_rec || 'N/A'}`
              : 'No recommendations yet'}
          </div>
        </div>

        {/* Irrigation */}
        <div className="metric-card">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
              <Droplets size={16} className="text-blue-600 dark:text-blue-400" />
            </div>
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">Irrigation</div>
          </div>
          <div className="text-2xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.total_irrigation_assessments > 0 ? metrics.total_irrigation_assessments : '-'}
          </div>
          <div className="text-xs text-forest-500 dark:text-forest-400 mt-1 truncate">
            {metrics.total_irrigation_assessments > 0 
              ? `Assessments run` 
              : 'No assessments available'}
          </div>
        </div>

        {/* FieldGuard Risk */}
        <div className="metric-card">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-orange-50 dark:bg-orange-900/30 flex items-center justify-center">
              <Shield size={16} className="text-orange-600 dark:text-orange-400" />
            </div>
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">FieldGuard Risk</div>
          </div>
          <div className="text-2xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.latest_fieldguard_score !== null ? Math.round(metrics.latest_fieldguard_score) : '-'}
          </div>
          <div className="text-xs text-forest-500 dark:text-forest-400 mt-1 truncate">
            {metrics.latest_fieldguard_score !== null 
              ? `Category: ${metrics.latest_fieldguard_category}` 
              : 'No risk score available'}
          </div>
        </div>

        {/* Sustainability Score */}
        <div className="metric-card">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-harvest-50 dark:bg-harvest-900/30 flex items-center justify-center">
              <Globe size={16} className="text-harvest-600 dark:text-harvest-400" />
            </div>
            <div className="text-xs font-semibold text-forest-700 dark:text-forest-300">Sustainability</div>
          </div>
          <div className="text-2xl font-bold text-forest-900 dark:text-forest-50">
            {metrics.latest_sustainability_score !== null ? Math.round(metrics.latest_sustainability_score) : '-'}
          </div>
          <div className="text-xs text-forest-500 dark:text-forest-400 mt-1 truncate">
            {metrics.latest_sustainability_score !== null 
              ? `Category: ${metrics.latest_sustainability_category}` 
              : 'Assessment unavailable'}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (Analytics) */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="font-bold text-lg text-forest-900 dark:text-forest-100">Farm Analytics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Activity Trend */}
            <div className="agri-card flex flex-col h-72">
              <h3 className="text-sm font-semibold text-forest-800 dark:text-forest-200 mb-4">Activity Trend</h3>
              <div className="flex-1">
                {analytics.activity_trend.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={analytics.activity_trend}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="date" tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <YAxis allowDecimals={false} tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                      <Line type="monotone" dataKey="count" name="Activities" stroke="#22c55e" strokeWidth={3} dot={{r: 4}} activeDot={{r: 6}} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-forest-500 dark:text-forest-400">
                    Not enough historical activity for a trend
                  </div>
                )}
              </div>
            </div>

            {/* Disease Breakdown */}
            <div className="agri-card flex flex-col h-72">
              <h3 className="text-sm font-semibold text-forest-800 dark:text-forest-200 mb-4">Disease Analysis</h3>
              <div className="flex-1">
                {metrics.total_disease_scans > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={diseaseChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
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
                <div className="flex justify-center gap-4 mt-2">
                  <div className="flex items-center gap-1 text-xs">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div> Healthy
                  </div>
                  <div className="flex items-center gap-1 text-xs">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div> Diseased
                  </div>
                </div>
              )}
            </div>
            
            {/* FieldGuard Trend */}
            <div className="agri-card flex flex-col h-72 md:col-span-2">
              <h3 className="text-sm font-semibold text-forest-800 dark:text-forest-200 mb-4">FieldGuard Risk Trend</h3>
              <div className="flex-1">
                {analytics.fieldguard_trend.length > 1 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={analytics.fieldguard_trend}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="date" tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 100]} tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                      <Line type="monotone" dataKey="score" name="Risk Score (Higher = Lower Risk)" stroke="#f59e0b" strokeWidth={3} dot={{r: 4}} activeDot={{r: 6}} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-xs text-forest-500 dark:text-forest-400">
                    <Shield size={24} className="mb-2 opacity-50" />
                    Not enough historical data for analytics (requires multiple assessments)
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>

        {/* Right Column (Insights & Attention & Activity) */}
        <div className="space-y-6">
          
          {/* Needs Attention */}
          <div className="agri-card">
            <h2 className="font-bold text-lg text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <AlertCircle size={20} className="text-amber-500" /> Needs Attention
            </h2>
            <div className="space-y-3">
              {needs_attention && needs_attention.length > 0 ? (
                needs_attention.map((item, idx) => (
                  <div key={idx} className={`p-3 rounded-lg border flex flex-col gap-2 ${
                    item.severity === 'error' ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200' :
                    item.severity === 'warning' ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200' :
                    item.severity === 'success' ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200' :
                    'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'
                  }`}>
                    <div className="text-sm font-medium">{item.reason}</div>
                    <NavLink to={item.link} className="text-xs font-bold underline opacity-80 hover:opacity-100">
                      {item.action} →
                    </NavLink>
                  </div>
                ))
              ) : (
                <div className="text-sm text-forest-500 dark:text-forest-400">
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
              <ul className="space-y-2 text-sm text-forest-700 dark:text-forest-300">
                {insights.map((insight, idx) => (
                  <li key={idx} className="flex gap-2 items-start">
                    <CheckCircle size={14} className="text-green-500 mt-1 flex-shrink-0" />
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-sm text-forest-500 dark:text-forest-400">
                Complete your farm profile and run assessments to generate insights.
              </div>
            )}
          </div>

          {/* Recent Activity Timeline */}
          <div className="agri-card">
            <h2 className="font-bold text-lg text-forest-900 dark:text-forest-100 mb-4 flex items-center gap-2">
              <Activity size={20} className="text-forest-500" /> Recent Activity
            </h2>
            <div className="space-y-0">
              {recent_activities && recent_activities.length > 0 ? (
                recent_activities.map((a, i) => (
                  <div key={i} className="flex items-start gap-3 border-b border-forest-100 dark:border-forest-800 py-3 last:border-0 last:pb-0 first:pt-0">
                    <div className="w-2 h-2 rounded-full bg-forest-400 dark:bg-forest-600 mt-2 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-forest-800 dark:text-forest-200 leading-snug">{a.title}</div>
                      {a.description && <div className="text-xs text-forest-500 dark:text-forest-400 mt-0.5">{a.description}</div>}
                      <div className="text-[10px] text-forest-400 dark:text-forest-500 mt-1">{new Date(a.created_at).toLocaleString()}</div>
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
print("Dashboard.jsx updated")
