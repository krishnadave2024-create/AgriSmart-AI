import React, { useState, useEffect } from 'react'
import { ScanLine, Leaf, Droplets, Globe, Activity, Info, Loader2 } from 'lucide-react'
import { NavLink } from 'react-router-dom'
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
        setError('Failed to load dashboard data.');
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
      <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Welcome back, {user?.full_name || user?.username}</p>
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Disease Scans */}
        <div className="metric-card border border-forest-200">
          <div className="w-10 h-10 rounded-xl bg-forest-50 flex items-center justify-center mb-2">
            <ScanLine size={20} className="text-forest-600" />
          </div>
          <div className="text-2xl font-bold text-forest-900">
            {data.total_disease_scans > 0 ? data.total_disease_scans : '-'}
          </div>
          <div className="text-xs font-semibold text-forest-700">Disease Scans</div>
          <div className="text-xs text-forest-500">
            {data.total_disease_scans > 0 
              ? `${data.healthy_scans} healthy, ${data.diseased_scans} diseased` 
              : 'Run your first disease scan'}
          </div>
        </div>

        {/* Crop Recommendations */}
        <div className="metric-card border border-emerald-200">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center mb-2">
            <Leaf size={20} className="text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-forest-900">
            {data.total_crop_recommendations > 0 ? data.total_crop_recommendations : '-'}
          </div>
          <div className="text-xs font-semibold text-forest-700">Crop Recommendations</div>
          <div className="text-xs text-forest-500">
            {data.total_crop_recommendations > 0 
              ? 'Assessments run' 
              : 'No records yet'}
          </div>
        </div>

        {/* Irrigation */}
        <div className="metric-card border border-blue-200">
          <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center mb-2">
            <Droplets size={20} className="text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-forest-900">
            {data.total_irrigation_assessments > 0 ? data.total_irrigation_assessments : '-'}
          </div>
          <div className="text-xs font-semibold text-forest-700">Irrigation Advice</div>
          <div className="text-xs text-forest-500">
            {data.total_irrigation_assessments > 0 
              ? 'Assessments run' 
              : 'No assessment available'}
          </div>
        </div>

        {/* Sustainability Score */}
        <div className="metric-card border border-harvest-200">
          <div className="w-10 h-10 rounded-xl bg-harvest-50 flex items-center justify-center mb-2">
            <Globe size={20} className="text-harvest-600" />
          </div>
          <div className="text-2xl font-bold text-forest-900">
            {data.latest_sustainability_score !== null ? Math.round(data.latest_sustainability_score) : '-'}
          </div>
          <div className="text-xs font-semibold text-forest-700">Sustainability Score</div>
          <div className="text-[10px] text-forest-500">
            {data.latest_sustainability_score !== null 
              ? '/ 100' 
              : 'Sustainability assessment unavailable'}
          </div>
        </div>
      </div>

      {/* Advisory + Activity grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* FieldGuard Risk */}
        <div className="lg:col-span-2 agri-card space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-bold text-lg text-forest-900">Latest FieldGuard Risk</h2>
          </div>

          {data.latest_fieldguard_score !== null ? (
            <div className="p-4 rounded-xl border border-forest-100 bg-forest-50 space-y-2">
              <div className="flex items-center gap-2">
                <span className={`badge px-2 py-1 text-xs font-bold rounded-full ${
                  data.latest_fieldguard_score > 80 ? 'bg-green-100 text-green-800' :
                  data.latest_fieldguard_score > 60 ? 'bg-yellow-100 text-yellow-800' :
                  data.latest_fieldguard_score > 40 ? 'bg-orange-100 text-orange-800' : 'bg-red-100 text-red-800'
                }`}>
                  {data.latest_fieldguard_category}
                </span>
                <span className="font-semibold text-forest-900 text-sm">Score: {Math.round(data.latest_fieldguard_score)}/100</span>
              </div>
              <div className="text-xs text-forest-700 mt-2">
                This is your most recent FieldGuard risk assessment. Check the FieldGuard tab to run a new one.
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl border border-forest-100 bg-forest-50 text-center py-8">
              <p className="text-forest-600 text-sm">No risk assessments available yet.</p>
              <NavLink to="/fieldguard" className="mt-3 inline-block text-xs font-semibold text-harvest-600 hover:underline">
                Run an Assessment →
              </NavLink>
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="agri-card space-y-3">
          <h2 className="font-bold text-lg text-forest-900 mb-2">Recent Activity</h2>
          
          {data.recent_activities && data.recent_activities.length > 0 ? (
            data.recent_activities.map((a, i) => (
              <div key={i} className="flex items-start gap-3 border-b border-forest-50 pb-2 last:border-0 last:pb-0">
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-medium text-forest-800 leading-snug">{a.title}</div>
                  {a.description && <div className="text-[10px] text-forest-500 mt-0.5">{a.description}</div>}
                  <div className="text-[10px] text-forest-400 mt-1">{new Date(a.created_at).toLocaleString()}</div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-6 text-forest-500 text-xs">
              No recent activity.
            </div>
          )}
        </div>

      </div>

      {/* Quick access */}
      <div className="agri-card">
        <h2 className="font-bold text-lg text-forest-900 mb-4">Quick Access</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { to: '/disease', icon: ScanLine, label: 'Scan a Leaf', color: 'bg-forest-100 text-forest-700' },
            { to: '/crops', icon: Leaf, label: 'Recommend Crops', color: 'bg-emerald-100 text-emerald-700' },
            { to: '/irrigation', icon: Droplets, label: 'Irrigation Advice', color: 'bg-blue-100 text-blue-700' },
            { to: '/sustainability', icon: Globe, label: 'Check Sustainability', color: 'bg-harvest-100 text-harvest-600' },
          ].map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`flex flex-col items-center gap-2 p-4 rounded-xl ${item.color} hover:opacity-80 transition-opacity text-center no-underline`}
              >
                <Icon size={22} />
                <span className="text-xs font-semibold">{item.label}</span>
              </NavLink>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
