import { useEffect, useState } from 'react'
import { fetchDashboardStats } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDashboardStats().then(setStats).catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="error-banner">{error}</div>
  if (!stats) return <div className="loading">Loading impact stats…</div>

  return (
    <div>
      <div className="section-title">♻️ Impact Dashboard</div>
      <div className="stat-grid">
        <div className="stat-card">
          <div className="value">{stats.materials_reused_units}</div>
          <div className="label">MATERIAL UNITS REUSED</div>
        </div>
        <div className="stat-card">
          <div className="value">{stats.waste_diverted_kg} kg</div>
          <div className="label">WASTE DIVERTED FROM LANDFILL</div>
        </div>
        <div className="stat-card">
          <div className="value">{stats.projects_connected}</div>
          <div className="label">PROJECTS CONNECTED</div>
        </div>
        <div className="stat-card">
          <div className="value">{stats.active_listings}</div>
          <div className="label">ACTIVE LISTINGS</div>
        </div>
        <div className="stat-card">
          <div className="value">{stats.open_requirements}</div>
          <div className="label">OPEN REQUIREMENTS</div>
        </div>
      </div>
    </div>
  )
}
