import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { customersApi } from '@/services/api'
import { Users, Search, TrendingDown, TrendingUp, Minus } from 'lucide-react'

const RISK_COLOR: Record<string, string> = { CRITICAL: '#f43f5e', HIGH: '#f59e0b', MEDIUM: '#3b82f6', LOW: '#10b981' }

function HealthBar({ score }: { score: number }) {
  const color = score >= 75 ? '#10b981' : score >= 55 ? '#f59e0b' : score >= 35 ? '#f97316' : '#f43f5e'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div className="progress-bar" style={{ width: 72, background: 'var(--color-bg-border)' }}>
        <div style={{ height: 6, width: `${score}%`, borderRadius: 9999, background: color, transition: 'width 0.5s' }} />
      </div>
      <span style={{ fontSize: 12.5, fontWeight: 600, color }}>{score?.toFixed(0)}</span>
    </div>
  )
}

export default function CustomersPage() {
  const [search, setSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['customers', search, riskFilter],
    queryFn: () => customersApi.list({ search: search || undefined, risk_level: riskFilter || undefined }).then(r => r.data),
  })

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1300, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Customers</h1>
        <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Customer health scores and churn risk</p>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1, maxWidth: 320 }}>
          <Search size={14} style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
          <input className="input" style={{ paddingLeft: 32 }} placeholder="Search customers…" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        {['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(r => (
          <button key={r} onClick={() => setRiskFilter(r)}
            className={`btn ${riskFilter === r ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: 12, padding: '7px 14px' }}>
            {r || 'All Risk'}
          </button>
        ))}
      </div>

      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr><th>Customer</th><th>Region</th><th>Tier</th><th>Health Score</th><th>Risk Level</th><th>Churn Risk</th><th>Contract Value</th></tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={7} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>Loading…</td></tr>}
            {!isLoading && !data?.items?.length && (
              <tr><td colSpan={7} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>No customers found — process customer data to populate</td></tr>
            )}
            {data?.items?.map((c: any) => (
              <tr key={c.id}>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, color: 'white', flexShrink: 0 }}>
                      {c.name?.[0]}
                    </div>
                    <div>
                      <p style={{ fontSize: 13.5, fontWeight: 600 }}>{c.name}</p>
                      {c.company && <p style={{ fontSize: 11.5, color: 'var(--color-text-muted)' }}>{c.company}</p>}
                    </div>
                  </div>
                </td>
                <td style={{ fontSize: 12.5, color: 'var(--color-text-secondary)' }}>{c.region || '—'}</td>
                <td>{c.tier ? <span className="badge badge-info">{c.tier}</span> : '—'}</td>
                <td><HealthBar score={c.health_score || 0} /></td>
                <td>
                  {c.risk_level && (
                    <span className={`badge badge-${c.risk_level?.toLowerCase()}`}>{c.risk_level}</span>
                  )}
                </td>
                <td style={{ fontSize: 12.5 }}>
                  {c.churn_risk_score != null
                    ? <span style={{ color: c.churn_risk_score > 0.6 ? '#f43f5e' : 'var(--color-text-secondary)' }}>{(c.churn_risk_score * 100).toFixed(0)}%</span>
                    : '—'}
                </td>
                <td style={{ fontSize: 12.5 }}>
                  {c.contract_value ? `$${c.contract_value.toLocaleString()}` : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
