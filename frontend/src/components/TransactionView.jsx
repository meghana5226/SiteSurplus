import { useEffect, useState } from 'react'
import { fetchTransaction, updateTransactionStatus, confirmReuse } from '../api'

const STAGES = ['MATCHED', 'ACCEPTED', 'PICKUP_SCHEDULED', 'PICKED_UP', 'DELIVERED', 'REUSE_CONFIRMED']
const NEXT = {
  MATCHED: 'ACCEPTED',
  ACCEPTED: 'PICKUP_SCHEDULED',
  PICKUP_SCHEDULED: 'PICKED_UP',
  PICKED_UP: 'DELIVERED',
}

export default function TransactionView({ transactionId }) {
  const [tx, setTx] = useState(null)
  const [status, setStatus] = useState(null)
  const [quantityConfirmed, setQuantityConfirmed] = useState('')
  const [notes, setNotes] = useState('')
  const [photo, setPhoto] = useState(null)
  const [confirmed, setConfirmed] = useState(false)

  useEffect(() => {
    if (transactionId) load()
  }, [transactionId])

  async function load() {
    const data = await fetchTransaction(transactionId)
    setTx(data)
    setQuantityConfirmed(data.agreed_quantity)
  }

  async function advance() {
    setStatus('Updating…')
    try {
      const updated = await updateTransactionStatus(transactionId, NEXT[tx.status])
      setTx(updated)
      setStatus(`✅ Moved to ${updated.status}`)
    } catch (err) {
      setStatus(`❌ ${err.message}`)
    }
  }

  async function handleConfirmReuse(e) {
    e.preventDefault()
    setStatus('Confirming reuse…')
    try {
      await confirmReuse(transactionId, parseFloat(quantityConfirmed), notes, photo)
      setConfirmed(true)
      setStatus('✅ Reuse confirmed! Dashboard stats updated.')
      load()
    } catch (err) {
      setStatus(`❌ ${err.message}`)
    }
  }

  if (!transactionId) return <div className="empty">Request a material match first to create a transaction.</div>
  if (!tx) return <div className="loading">Loading transaction…</div>

  const currentIndex = STAGES.indexOf(tx.status)

  return (
    <div>
      <div className="section-title">🚚 Transaction #{tx.id}</div>

      <div className="stepper">
        {STAGES.map((stage, i) => (
          <span key={stage}>
            <span className={`step ${i < currentIndex ? 'done' : i === currentIndex ? 'current' : ''}`}>
              {stage.replace('_', ' ')}
            </span>
            {i < STAGES.length - 1 && <span className="step-arrow"> → </span>}
          </span>
        ))}
      </div>

      <div className="card" style={{ maxWidth: 440 }}>
        <div className="row"><span className="k">Agreed quantity</span><span>{tx.agreed_quantity}</span></div>
        <div className="row"><span className="k">Material value (est.)</span><span>₹{tx.agreed_value_inr.toLocaleString()}</span></div>
        <div className="row"><span className="k">Transport cost (est.)</span><span>₹{tx.estimated_transport_cost_inr.toLocaleString()}</span></div>
        <div className="row"><span className="k">Distance</span><span>{tx.distance_km.toFixed(1)} km</span></div>
      </div>

      {NEXT[tx.status] && (
        <button className="btn blue" style={{ marginTop: 16 }} onClick={advance}>
          Mark as {NEXT[tx.status].replace('_', ' ')}
        </button>
      )}

      {tx.status === 'DELIVERED' && !confirmed && (
        <div className="form-panel" style={{ marginTop: 20 }}>
          <h2>✅ Confirm Reuse</h2>
          <form onSubmit={handleConfirmReuse}>
            <div className="form-row full">
              <div className="form-group">
                <label>Quantity actually reused</label>
                <input type="number" step="0.01" value={quantityConfirmed} onChange={(e) => setQuantityConfirmed(e.target.value)} required />
              </div>
            </div>
            <div className="form-row full">
              <div className="form-group">
                <label>Notes</label>
                <textarea rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Installed in Block C ground floor lobby." />
              </div>
            </div>
            <div className="form-row full">
              <div className="form-group">
                <label>Photo of material installed/reused (optional)</label>
                <input type="file" accept="image/*" onChange={(e) => setPhoto(e.target.files[0])} />
              </div>
            </div>
            <button className="btn" type="submit">Confirm reuse</button>
          </form>
        </div>
      )}

      {tx.status === 'REUSE_CONFIRMED' && (
        <div className="ai-box" style={{ marginTop: 16, borderColor: 'rgba(34,197,94,0.4)', background: 'rgba(34,197,94,0.08)' }}>
          ♻️ This material has been successfully reused. Great work closing the loop!
        </div>
      )}

      {status && <div className="status-msg">{status}</div>}
    </div>
  )
}
