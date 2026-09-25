import { useState } from 'react'
import { createListing, uploadListingImage } from '../api'

const CITIES = ['Hyderabad', 'Bangalore', 'Chennai', 'Mumbai', 'Pune', 'Delhi', 'Kolkata', 'Ahmedabad', 'Jaipur']
const CONDITIONS = ['Unused', 'Good', 'Fair']

export default function ListingForm() {
  const [form, setForm] = useState({
    supplier_name: '', material_category: '', material_type: '', quantity: '', unit: 'Pieces',
    dimension_length_mm: '', dimension_width_mm: '', condition: 'Unused', color: '',
    location_city: 'Hyderabad', available_until: '',
  })
  const [createdListing, setCreatedListing] = useState(null)
  const [aiPrediction, setAiPrediction] = useState(null)
  const [status, setStatus] = useState(null)
  const [imageFile, setImageFile] = useState(null)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setStatus('Creating listing…')
    try {
      const payload = {
        ...form,
        quantity: parseFloat(form.quantity),
        dimension_length_mm: form.dimension_length_mm ? parseFloat(form.dimension_length_mm) : null,
        dimension_width_mm: form.dimension_width_mm ? parseFloat(form.dimension_width_mm) : null,
        available_until: new Date(form.available_until).toISOString(),
      }
      const listing = await createListing(payload)
      setCreatedListing(listing)
      setStatus(`✅ Listing #${listing.id} created.`)
    } catch (err) {
      setStatus(`❌ ${err.message}`)
    }
  }

  async function handleImageUpload() {
    if (!imageFile || !createdListing) return
    setStatus('Analyzing photo with material AI…')
    try {
      const result = await uploadListingImage(createdListing.id, imageFile)
      setAiPrediction(result.ai_prediction)
      setStatus('✅ Photo uploaded and analyzed.')
    } catch (err) {
      setStatus(`❌ ${err.message}`)
    }
  }

  return (
    <div className="form-panel">
      <h2>🏗️ List Surplus Material</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Supplier / Site name</label>
            <input required value={form.supplier_name} onChange={(e) => update('supplier_name', e.target.value)} placeholder="Site A - Gachibowli Tower" />
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
            <label>Quantity</label>
            <input required type="number" step="0.01" value={form.quantity} onChange={(e) => update('quantity', e.target.value)} placeholder="120" />
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
            <label>Condition</label>
            <select value={form.condition} onChange={(e) => update('condition', e.target.value)}>
              {CONDITIONS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Color</label>
            <input value={form.color} onChange={(e) => update('color', e.target.value)} placeholder="White" />
          </div>
        </div>
        <div className="form-row full">
          <div className="form-group">
            <label>Available until</label>
            <input required type="date" value={form.available_until} onChange={(e) => update('available_until', e.target.value)} />
          </div>
        </div>
        <button className="btn" type="submit" disabled={!!createdListing}>
          {createdListing ? 'Listing created' : 'Create listing'}
        </button>
      </form>

      {createdListing && (
        <div style={{ marginTop: 20 }}>
          <div className="section-title" style={{ marginTop: 0 }}>📷 Add a photo (optional — AI will suggest the material)</div>
          <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files[0])} />
          <button className="btn blue" style={{ marginLeft: 10 }} onClick={handleImageUpload} disabled={!imageFile}>
            Upload &amp; analyze
          </button>

          {aiPrediction && (
            <div className="ai-box">
              <strong>🤖 AI suggests:</strong> {aiPrediction.material_category} / {aiPrediction.material_type}
              {' '}(confidence {Math.round(aiPrediction.confidence * 100)}%)
              <div style={{ color: '#93a39a', marginTop: 4 }}>{aiPrediction.reasoning}</div>
              <div style={{ color: '#93a39a', marginTop: 4, fontSize: 12 }}>
                This is a suggestion only — it does not change your listing. Please verify the material details above are correct.
              </div>
            </div>
          )}
        </div>
      )}

      {status && <div className="status-msg">{status}</div>}
    </div>
  )
}
