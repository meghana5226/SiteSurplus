import { useState } from 'react'
import Dashboard from './components/Dashboard'
import Marketplace from './components/Marketplace'
import ListingForm from './components/ListingForm'
import RequirementForm from './components/RequirementForm'
import MatchesView from './components/MatchesView'
import TransactionView from './components/TransactionView'

const TABS = [
  { id: 'dashboard', label: '📊 Dashboard' },
  { id: 'marketplace', label: '📦 Marketplace' },
  { id: 'list', label: '➕ List Material' },
  { id: 'requirement', label: '📋 Post Requirement' },
  { id: 'matches', label: '🎯 Find Matches' },
  { id: 'transaction', label: '🚚 Transaction' },
]

export default function App() {
  const [tab, setTab] = useState('dashboard')
  const [activeTransactionId, setActiveTransactionId] = useState(null)

  function handleTransactionCreated(id) {
    setActiveTransactionId(id)
    setTab('transaction')
  }

  return (
    <div className="app">
      <div className="header">
        <div>
          <div className="logo"><span className="dot" />ConstructionWaste Exchange</div>
          <div className="tagline">Match surplus construction material between sites — AI-assisted, logistics-aware</div>
        </div>
      </div>

      <div className="nav">
        {TABS.map((t) => (
          <button key={t.id} className={tab === t.id ? 'active' : ''} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'dashboard' && <Dashboard />}
      {tab === 'marketplace' && <Marketplace />}
      {tab === 'list' && <ListingForm />}
      {tab === 'requirement' && <RequirementForm onCreated={() => setTab('matches')} />}
      {tab === 'matches' && <MatchesView onTransactionCreated={handleTransactionCreated} />}
      {tab === 'transaction' && <TransactionView transactionId={activeTransactionId} />}
    </div>
  )
}
