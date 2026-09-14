import { ScanLine, Leaf, Droplets, Globe, Activity, Info } from 'lucide-react'
import { NavLink } from 'react-router-dom'

/* ─── Demo metric cards (clearly marked as demo data) ──────────────────── */
const METRICS = [
  {
    label: 'Crop Health Index',
    value: '92%',
    sub: '+4.2% this week',
    trend: 'up',
    icon: Activity,
    color: 'text-forest-600',
    bg: 'bg-forest-50',
    border: 'border-forest-200',
    demo: true,
  },
  {
    label: 'Disease Risk',
    value: 'Low',
    sub: 'No flagged detections',
    trend: 'good',
    icon: ScanLine,
    color: 'text-forest-600',
    bg: 'bg-forest-50',
    border: 'border-forest-200',
    demo: true,
  },
  {
    label: 'Soil Moisture',
    value: '68%',
    sub: 'Manual input · Optimal zone',
    trend: 'stable',
    icon: Droplets,
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    demo: true,
  },
  {
    label: 'Sustainability Score',
    value: '84',
    sub: '/ 100 · Excellent',
    trend: 'up',
    icon: Globe,
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    demo: true,
  },
]

/* ─── Advisory items (prototype rule-based, clearly labeled) ─────────────── */
const ADVISORY = [
  {
    priority: 'HIGH',
    priorityClass: 'badge-red',
    title: 'Delay Tube-Well Irrigation',
    why: 'Rainfall forecast (manual input) indicates precipitation expected in 24h. Running irrigation now may cause water waste.',
    action: 'Hold irrigation until tomorrow morning and reassess soil moisture.',
    feature: '/irrigation',
    featureLabel: 'Check Irrigation',
  },
  {
    priority: 'MEDIUM',
    priorityClass: 'badge-amber',
    title: 'Inspect Lower Canopy for Fungal Risk',
    why: 'High humidity (manual input) above 85% combined with temperatures above 25°C creates conditions suitable for fungal growth.',
    action: 'Visually inspect the lower canopy of your crop and check for spots or discolouration.',
    feature: '/disease',
    featureLabel: 'Disease Detection',
  },
  {
    priority: 'OPTIMAL',
    priorityClass: 'badge-green',
    title: 'Crop Rotation Planning Window',
    why: "Approaching end of current crop cycle — consider planning next season's rotation for soil health.",
    action: 'Use the Crop Recommendation tool to find suitable follow-on crops.',
    feature: '/crops',
    featureLabel: 'Crop Recommendation',
  },
]

/* ─── Recent activities (demo) ─────────────────────────────────────────── */
const ACTIVITIES = [
  { icon: ScanLine, text: 'Disease scan completed — No disease detected', time: '2h ago', color: 'text-forest-600', bg: 'bg-forest-50' },
  { icon: Droplets, text: 'Irrigation advisory updated — Delay recommended', time: '4h ago', color: 'text-blue-600', bg: 'bg-blue-50' },
  { icon: Leaf, text: 'Crop recommendation run — Rice (85), Maize (82)', time: 'Yesterday', color: 'text-emerald-600', bg: 'bg-emerald-50' },
]

function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">AgriSmart AI · Prototype overview for your farm operations</p>
        </div>
        <span className="badge-proto">Demo Data</span>
      </div>
      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {METRICS.map((m) => {
          const Icon = m.icon
          return (
            <div key={m.label} className={`metric-card border ${m.border}`}>
              <div className={`w-10 h-10 rounded-xl ${m.bg} flex items-center justify-center mb-2`}>
                <Icon size={20} className={m.color} />
              </div>
              <div className="text-2xl font-bold text-forest-900">{m.value}</div>
              <div className="text-xs font-semibold text-forest-700">{m.label}</div>
              <div className="text-xs text-forest-500">{m.sub}</div>
              {m.demo && <span className="badge-proto mt-1 self-start">Demo</span>}
            </div>
          )
        })}
      </div>

      {/* Advisory + Activity grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Advisory panel */}
        <div className="lg:col-span-2 agri-card space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-bold text-lg text-forest-900">Today's Advisory</h2>
            <div className="flex items-center gap-2">
              <span className="badge-proto">Rule-based · Prototype</span>
            </div>
          </div>

          {ADVISORY.map((a, i) => (
            <div key={i} className="p-4 rounded-xl border border-forest-100 bg-forest-50 space-y-2">
              <div className="flex items-center gap-2">
                <span className={a.priorityClass}>{a.priority}</span>
                <span className="font-semibold text-forest-900 text-sm">{a.title}</span>
              </div>
              <div className="text-xs text-forest-600">
                <strong>Why:</strong> {a.why}
              </div>
              <div className="text-xs text-forest-700">
                <strong>Action:</strong> {a.action}
              </div>
              <NavLink
                to={a.feature}
                className="inline-flex items-center gap-1 text-xs font-semibold text-forest-700 hover:text-forest-900 hover:underline"
              >
                → {a.featureLabel}
              </NavLink>
            </div>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="agri-card space-y-3">
          <h2 className="font-bold text-lg text-forest-900 mb-2">Recent Activity</h2>
          {ACTIVITIES.map((a, i) => {
            const Icon = a.icon
            return (
              <div key={i} className="flex items-start gap-3">
                <div className={`w-8 h-8 rounded-lg ${a.bg} flex items-center justify-center flex-shrink-0 mt-0.5`}>
                  <Icon size={15} className={a.color} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-medium text-forest-800 leading-snug">{a.text}</div>
                  <div className="text-[10px] text-forest-500 mt-0.5">{a.time} · Demo data</div>
                </div>
              </div>
            )
          })}
          <div className="pt-2 border-t border-forest-100 text-[10px] text-forest-400">
            Activity log is prototype demo data. No real farm records are stored.
          </div>
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
