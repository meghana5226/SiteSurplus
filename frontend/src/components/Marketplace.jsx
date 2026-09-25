import { useEffect, useState } from 'react'
import { fetchListings } from '../api'

export default function Marketplace() {
  const [listings, setListings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchListings()
      .then(setListings)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (error) return <div className="error-banner">{error}</div>
  if (loading) return <div className="loading">Loading listings…</div>

  return (
    <div>
      <div className="section-title">📦 Surplus Material Marketplace</div>
      {listings.length === 0 && <div className="empty">No listings yet — be the first supplier to list material.</div>}
      <div className="grid">
        {listings.map((l) => (
          <div className="card" key={l.id}>
            <span className={`badge ${l.status.toLowerCase()}`}>{l.status}</span>
            <h3 style={{ marginTop: 8 }}>{l.material_type}</h3>
            <div className="sub">{l.supplier_name} · {l.location_city}</div>
            <div className="row"><span className="k">Quantity</span><span>{l.quantity} {l.unit}</span></div>
            {l.dimension_length_mm && (
              <div className="row"><span className="k">Dimensions</span><span>{l.dimension_length_mm}×{l.dimension_width_mm}mm</span></div>
            )}
            <div className="row"><span className="k">Condition</span><span>{l.condition}</span></div>
            <div className="row"><span className="k">Available until</span><span>{new Date(l.available_until).toLocaleDateString()}</span></div>
          </div>
        ))}
      </div>
    </div>
  )
}
