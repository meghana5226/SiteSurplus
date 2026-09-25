import { useState } from 'react'
import { createRequirement } from '../api'

const CITIES = ['Hyderabad', 'Bangalore', 'Chennai', 'Mumbai', 'Pune', 'Delhi', 'Kolkata', 'Ahmedabad', 'Jaipur']
const CONDITIONS = ['Unused', 'Good', 'Fair']

export default function RequirementForm({ onCreated }) {
  const [form, setForm] = useState({
    requester_name: '', material_category: '', material_type: '', quantity: '', unit: 'Pieces',
    dimension_length_mm: '', dimension_width_mm: '', condition: 'Unused',
    location_city: 'Hyderabad', required_by: '',
  })
  const [status, setStatus] = useState(null)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setStatus('Posting requirement…')
    try {
      const payload = {
        ...form,
        quantity: parseFloat(form.quantity),
        dimension_length_mm: form.dimension_length_mm ? parseFloat(form.dimension_length_mm) : null,
        dimension_width_mm: form.dimension_width_mm ? parseFloat(form.dimension_width_mm) : null,
        required_by: new Date(form.required_by).toISOString(),
      }
      const requirement = await createRequirement(payload)
      setStatus(`✅ Requirement #${requirement.id} posted. Head to "Find Matches" to run the matching engine.`)
      if (onCreated) onCreated(requirement)
    } catch (err) {
      setStatus(`❌ ${err.message}`)
    }
  }

  return (
    <div className="form-panel">
      <h2>📋 Post a Material Requirement</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Requester / Site name</label>
            <input required value={form.requester_name} onChange={(e) => update('requester_name', e.target.value)} placeholder="Site X - Madhapur Build" />
          </div>
          <div className="form-group">
            <label>City</label>
            <select value={form.location_city} onChange={(e) => update('location_city', e.target.value)}>
              {CITIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Material category</label>
            <input required value={form.material_category} onChange={(e) => update('material_category', e.target.value)} placeholder="Flooring" />
          </div>
          <div className="form-group">
            <label>Material type</label>
            <input required value={form.material_type} onChange={(e) => update('material_type', e.target.value)} placeholder="Ceramic Tile" />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Quantity needed</label>
            <input required type="number" step="0.01" value={form.quantity} onChange={(e) => update('quantity', e.target.value)} placeholder="100" />
          </div>
          <div className="form-group">
            <label>Unit</label>
            <input required value={form.unit} onChange={(e) => update('unit', e.target.value)} placeholder="Pieces" />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Length (mm)</label>
            <input type="number" value={form.dimension_length_mm} onChange={(e) => update('dimension_length_mm', e.target.value)} placeholder="600" />
          </div>
          <div className="form-group">
            <label>Width (mm)</label>
            <input type="number" value={form.dimension_width_mm} onChange={(e) => update('dimension_width_mm', e.target.value)} placeholder="600" />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Minimum condition</label>
            <select value={form.condition} onChange={(e) => update('condition', e.target.value)}>
              {CONDITIONS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Required by</label>
            <input required type="date" value={form.required_by} onChange={(e) => update('required_by', e.target.value)} />
          </div>
        </div>
        <button className="btn" type="submit">Post requirement</button>
      </form>
      {status && <div className="status-msg">{status}</div>}
    </div>
  )
}
