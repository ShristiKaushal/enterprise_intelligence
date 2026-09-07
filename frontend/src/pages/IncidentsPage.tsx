import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { incidentsApi } from '@/services/api'
import { AlertTriangle, Search } from 'lucide-react'
import { format } from 'date-fns'

const SEV_COLOR: Record<string, string> = { critical: '#f43f5e', high: '#f59e0b', medium: '#3b82f6', low: '#10b981' }

export default function IncidentsPage() {
  const [sevFilter, setSevFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['incidents', sevFilter, statusFilter],
    queryFn: () => incidentsApi.list({ severity: sevFilter || undefined, status: statusFilter || undefined }).then(r => r.data),
  })

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1300, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Incidents</h1>
        <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Extracted and normalized IT incidents with SLA tracking</p>
      </div>

      <div style={{ display: 'flex', gap: 10, marginBottom: 18, flexWrap: 'wrap' }}>
        {['', 'critical', 'high', 'medium', 'low'].map(s => (
          <button key={s} onClick={() => setSevFilter(s)}
            className={`btn ${sevFilter === s ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: 12, padding: '7px 14px', textTransform: 'capitalize' }}>
            {s || 'All Severity'}
          </button>
        ))}
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          {['', 'open', 'closed', 'resolved'].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`btn ${statusFilter === s ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: 12, padding: '7px 14px', textTransform: 'capitalize' }}>
              {s || 'All Status'}
            </button>
          ))}
        </div>
      </div>

      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr><th>Incident #</th><th>Title</th><th>Severity</th><th>Category</th><th>Status</th><th>SLA</th><th>Downtime</th><th>Occurred</th></tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={8} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>Loading…</td></tr>}
            {!isLoading && !data?.items?.length && (
              <tr><td colSpan={8} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>No incidents found — process IT operations data to populate</td></tr>
            )}
            {data?.items?.map((inc: any) => (
              <tr key={inc.id}>
                <td><span className="mono">{inc.incident_number}</span></td>
                <td style={{ maxWidth: 280 }}>
                  <p style={{ fontSize: 13, fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{inc.title}</p>
                </td>
                <td><span className={`badge badge-${inc.severity?.toLowerCase()}`}>{inc.severity?.toUpperCase()}</span></td>
                <td style={{ fontSize: 12, color: 'var(--color-text-secondary)' }}>
                  {[inc.category, inc.subcategory].filter(Boolean).join(' / ')}
                </td>
                <td>
                  <span style={{ fontSize: 12, textTransform: 'capitalize', color: inc.status === 'open' ? '#f59e0b' : '#10b981' }}>
                    {inc.status}
                  </span>
                </td>
                <td>
                  {inc.sla_breached
                    ? <span style={{ fontSize: 12, color: '#f43f5e', fontWeight: 600 }}>⚠ Breached</span>
                    : <span style={{ fontSize: 12, color: '#10b981' }}>✓ OK</span>}
                </td>
                <td style={{ fontSize: 12.5 }}>{inc.downtime_minutes ? `${inc.downtime_minutes?.toFixed(0)}m` : '—'}</td>
                <td style={{ fontSize: 11.5, color: 'var(--color-text-muted)' }}>
                  {inc.occurred_at ? format(new Date(inc.occurred_at), 'MMM d, HH:mm') : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
