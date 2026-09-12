import { Shield, Lock, Activity, Droplets, Cloud, AlertTriangle } from 'lucide-react'

const PILLARS = [
  { icon: Activity,     label: 'Foliar Disease Incidence',     status: 'Planned', desc: 'Aggregated disease scan results and spread index.' },
  { icon: Droplets,     label: 'Hydrological Tension & Water Stress', status: 'Planned', desc: 'Root-zone moisture and irrigation efficiency metrics.' },
  { icon: Cloud,        label: 'Weather & Microclimate Instability', status: 'Planned', desc: 'Temperature, humidity, and precipitation risk aggregation.' },
  { icon: AlertTriangle, label: 'Phenological Stage Fragility', status: 'Planned', desc: 'Growth-stage vulnerability to environmental stress.' },
]

function FieldGuard() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Shield size={28} className="text-forest-600" /> FieldGuard Risk Intelligence
          </h1>
          <p className="page-subtitle">Composite agricultural threat analysis · Coming soon</p>
        </div>
        <span className="badge-proto">Prototype Preview</span>
      </div>

      {/* Coming soon banner */}
      <div className="agri-card border-2 border-dashed border-forest-300 text-center py-12">
        <div className="w-16 h-16 rounded-2xl bg-forest-100 flex items-center justify-center mx-auto mb-4">
          <Lock size={28} className="text-forest-500" />
        </div>
        <h2 className="text-xl font-bold text-forest-900 mb-2">FieldGuard is Coming Soon</h2>
        <p className="text-forest-600 text-sm max-w-lg mx-auto mb-4">
          FieldGuard will synthesise crop disease probability, micro-meteorology, and root-canopy moisture 
          stress into a single composite Farm Threat Index. This feature is planned for a future development phase.
        </p>
        <div className="proto-banner max-w-lg mx-auto text-left">
          <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
          <span>
            <strong>No live risk scores are available.</strong> This page is a planned-feature preview only.
            No satellite data, IoT sensors, or live meteorological feeds are connected.
          </span>
        </div>
      </div>

      {/* Planned risk pillars */}
      <div className="agri-card">
        <h2 className="font-bold text-lg text-forest-900 mb-4">Planned Risk Pillars</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {PILLARS.map((p, i) => {
            const Icon = p.icon
            return (
              <div key={i} className="flex items-start gap-3 p-4 rounded-xl bg-forest-50 border border-forest-100">
                <div className="w-9 h-9 rounded-lg bg-white border border-forest-200 flex items-center justify-center flex-shrink-0">
                  <Icon size={18} className="text-forest-600" />
                </div>
                <div>
                  <div className="font-semibold text-forest-900 text-sm">{p.label}</div>
                  <div className="text-forest-500 text-xs mt-0.5">{p.desc}</div>
                  <span className="badge-proto mt-2">{p.status}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default FieldGuard
