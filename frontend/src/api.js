const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function handleResponse(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

// --- Listings ---
export const fetchListings = (status) =>
  fetch(`${API_BASE}/api/listings${status ? `?status=${status}` : ''}`).then(handleResponse)

export const fetchListing = (id) => fetch(`${API_BASE}/api/listings/${id}`).then(handleResponse)

export const createListing = (payload) =>
  fetch(`${API_BASE}/api/listings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(handleResponse)

export const uploadListingImage = (listingId, file) => {
  const form = new FormData()
  form.append('file', file)
  return fetch(`${API_BASE}/api/listings/${listingId}/images`, { method: 'POST', body: form }).then(handleResponse)
}

// --- Requirements ---
export const fetchRequirements = () => fetch(`${API_BASE}/api/requirements`).then(handleResponse)

export const createRequirement = (payload) =>
  fetch(`${API_BASE}/api/requirements`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(handleResponse)

// --- Matching ---
export const runMatching = (requirementId) =>
  fetch(`${API_BASE}/api/matching/run/${requirementId}`, { method: 'POST' }).then(handleResponse)

export const fetchMatches = (requirementId) =>
  fetch(`${API_BASE}/api/matching/for-requirement/${requirementId}`).then(handleResponse)

// --- Transactions ---
export const createTransaction = (payload) =>
  fetch(`${API_BASE}/api/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(handleResponse)

export const fetchTransaction = (id) => fetch(`${API_BASE}/api/transactions/${id}`).then(handleResponse)

export const updateTransactionStatus = (id, status) =>
  fetch(`${API_BASE}/api/transactions/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  }).then(handleResponse)

// --- Reuse ---
export const confirmReuse = (transactionId, quantityConfirmed, notes, photoFile) => {
  const form = new FormData()
  form.append('transaction_id', transactionId)
  form.append('quantity_confirmed', quantityConfirmed)
  if (notes) form.append('notes', notes)
  if (photoFile) form.append('photo', photoFile)
  return fetch(`${API_BASE}/api/reuse`, { method: 'POST', body: form }).then(handleResponse)
}

// --- Dashboard ---
export const fetchDashboardStats = () => fetch(`${API_BASE}/api/dashboard/stats`).then(handleResponse)

export const assetUrl = (path) => (path ? `${API_BASE}${path}` : null)
