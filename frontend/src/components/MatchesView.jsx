import { useEffect, useState } from 'react'
import { fetchRequirements, runMatching, fetchMatches, createTransaction } from '../api'

function scoreClass(score) {
  if (score >= 0.7) return 'score-high'
  if (score >= 0.4) return 'score-mid'
  return 'score-low'
}

function ScoreBar({ label, value }) {
  return (
    <div className="score-bar-row">
      <span>{label}</span>
      <div className="score-bar-track"><div className="score-bar-fill" style={{ width: `${value * 100}%` }} /></div>
      <span>{Math.round(value * 100)}%</span>
    </div>
  )
}

export default function MatchesView({ onTransactionCreated }) {
  const [requirements, setRequirements] = useState([])
  const [selectedReq, setSelectedReq] = useState(null)
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [status, setStatus] = useState(null)

  useEffect(() => {
    fetchRequirements().then((reqs) => { setRequirements(reqs); setLoading(false) })
  }, [])

  async function selectRequirement(req) {
    setSelectedReq(req)
    setStatus('Loading matches…')
    try {
      const existing = await fetchMatches(req.id)
      setMatches(existing)
      setStatus(null)
    } catch {
      setMatches([])
      setStatus(null)
    }
  }

  async function handleRunMatching() {
    setStatus('🔍 Running matching engine…')
    try {
      const results = await runMatching(selectedReq.id)
      setMatches(results)
      setStatus(`Found ${results.length} candidate match(es).`)
    } catch (err) {
      setStatus(`❌ ${err.message}`)
    }
  }

  async function handleRequestMaterial(match) {
    setStatus('Creating transaction…')
    try {
      const tx = await createTransaction({
        match_id: match.id,
        agreed_quantity: Math.min(match.listing.quantity, selectedReq.quantity),
      })
      setStatus(`✅ Transaction #${tx.id} created (status: ${tx.status}).`)
      if (onTransactionCreated) onTransactionCreated(tx.id)
    } catch (err) {
      setStatus(`❌ ${err.message}`)
    }
  }

  if (loading) return <div className="loading">Loading requirements…</div>

  return (
    <div>
      <div className="section-title">🎯 Find Matches</div>

      {!selectedReq ? (
        <div className="list-simple">
          {requirements.length === 0 && <div className="empty">No requirements posted yet.</div>}
          {requirements.map((r) => (
            <div key={r.id} className="list-item" onClick={() => selectRequirement(r)}>
              <div>
                <strong>{r.material_type}</strong> — {r.quantity} {r.unit}
                <div style={{ color: '#93a39a', fontSize: 12 }}>{r.requester_name} · {r.location_city}</div>
              </div>
              <span>View matches →</span>
            </div>
          ))}
        </div>
      ) : (
        <div>
          <span className="status-msg" style={{ cursor: 'pointer', color: '#4f7cff' }} onClick={() => setSelectedReq(null)}>← Back to requirements</span>
          <h3 style={{ marginBottom: 4 }}>{selectedReq.material_type} — {selectedReq.quantity} {selectedReq.unit}</h3>
          <div style={{ color: '#93a39a', fontSize: 13, marginBottom: 14 }}>
            Requested by {selectedReq.requester_name} in {selectedReq.location_city}
          </div>

          <button className="btn blue" onClick={handleRunMatching}>Run matching engine</button>
          {status && <div className="status-msg">{status}</div>}

          {matches.map((m) => (
            <div className="match-card" key={m.id}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div className="sub">{m.listing.supplier_name} · {m.listing.location_city}</div>
                  <h3 style={{ margin: '2px 0' }}>{m.listing.material_type} — {m.listing.quantity} {m.listing.unit} available</h3>
                </div>
                <div className={`match-score ${scoreClass(m.score)}`}>{Math.round(m.score * 100)}%</div>
              </div>

              <div className="score-bars">
                <ScoreBar label="Material (30%)" value={m.material_score} />
                <ScoreBar label="Dimension (20%)" value={m.dimension_score} />
                <ScoreBar label="Quantity (15%)" value={m.quantity_score} />
                <ScoreBar label="Condition (15%)" value={m.condition_score} />
                <ScoreBar label="Distance (10%)" value={m.distance_score} />
                <ScoreBar label="Availability (10%)" value={m.availability_score} />
              </div>
              <div style={{ marginTop: 10, fontSize: 13, color: '#93a39a' }}>
                Distance: {m.distance_km?.toFixed(1)} km
              </div>

              <button className="btn" style={{ marginTop: 14 }} onClick={() => handleRequestMaterial(m)}>
                Request this material
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
