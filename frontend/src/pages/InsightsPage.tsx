import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { insightsApi } from '@/services/api'
import { useNavigate } from 'react-router-dom'
import { Lightbulb, Filter, Check } from 'lucide-react'
import toast from 'react-hot-toast'

const SEV = ['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
const TYPES = ['', 'risk', 'emerging_issue', 'anomaly', 'sla_risk', 'root_cause', 'trend']

export default function InsightsPage() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [sev, setSev] = useState('')
  const [type, setType] = useState('')
  const [status, setStatus] = useState('active')

  const { data, isLoading } = useQuery({
    queryKey: ['insights', sev, type, status],
    queryFn: () => insightsApi.list({ severity: sev || undefined, insight_type: type || undefined, status }).then(r => r.data),
  })

  const ackMutation = useMutation({
    mutationFn: (id: string) => insightsApi.acknowledge(id),
    onSuccess: () => { toast.success('Insight acknowledged'); qc.invalidateQueries({ queryKey: ['insights'] }) },
  })

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1300, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Business Insights</h1>
          <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>AI-generated intelligence, prioritized by business impact × confidence × urgency</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['active', 'acknowledged'].map(s => (
            <button key={s} onClick={() => setStatus(s)} className={`btn ${status === s ? 'btn-primary' : 'btn-secondary'}`} style={{ fontSize: 12, padding: '7px 14px', textTransform: 'capitalize' }}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 18, flexWrap: 'wrap', alignItems: 'center' }}>
        <Filter size={14} style={{ color: 'var(--color-text-muted)' }} />
        {SEV.map(s => (
          <button key={s} onClick={() => setSev(s)}
            className={`btn ${sev === s ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: 11.5, padding: '5px 12px' }}>
            {s || 'All Severity'}
          </button>
        ))}
        <div style={{ width: 1, height: 20, background: 'var(--color-bg-border)', margin: '0 4px' }} />
        {TYPES.map(t => (
          <button key={t} onClick={() => setType(t)}
            className={`btn ${type === t ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: 11.5, padding: '5px 12px', textTransform: 'capitalize' }}>
            {t ? t.replace('_', ' ') : 'All Types'}
          </button>
        ))}
      </div>

      {isLoading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 120, borderRadius: 12 }} />)}
        </div>
      )}

      {!isLoading && !data?.items?.length && (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Lightbulb size={40} style={{ color: 'var(--color-text-muted)', margin: '0 auto 12px' }} />
          <p style={{ fontSize: 15, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 6 }}>No insights yet</p>
          <p style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>Upload and process data to generate business intelligence</p>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {data?.items?.map((ins: any) => (
          <div key={ins.id} className={`insight-card ${ins.severity?.toLowerCase()}`} style={{ cursor: 'default' }}>
            <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
              {/* Main content */}
              <div style={{ flex: 1, cursor: 'pointer' }} onClick={() => navigate(`/insights/${ins.id}`)}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <span className={`badge badge-${ins.severity?.toLowerCase()}`}>{ins.severity}</span>
                  <span style={{ fontSize: 11, color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
                    {ins.insight_type?.replace(/_/g, ' ')}
                  </span>
                  {ins.is_cross_domain && <span className="badge badge-info">Cross-domain</span>}
                  <span style={{ fontSize: 11, color: 'var(--color-text-muted)', marginLeft: 'auto' }}>
                    Priority: <strong style={{ color: '#60a5fa' }}>{(ins.priority_score * 100).toFixed(0)}</strong>
                  </span>
                </div>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 6 }}>{ins.title}</h3>
                <p style={{ fontSize: 13, color: 'var(--color-text-secondary)', lineHeight: 1.55, marginBottom: 10 }}>{ins.description}</p>

                {/* Evidence chips */}
                {ins.evidence?.length > 0 && (
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {ins.evidence.slice(0, 3).map((e: any, i: number) => (
                      <span key={i} style={{ fontSize: 11, padding: '2px 8px', background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: 6, color: '#94a3b8' }}>
                        {e.label}: <strong style={{ color: '#f1f5f9' }}>{String(e.value)}</strong>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Right panel */}
              <div style={{ flexShrink: 0, textAlign: 'right', minWidth: 120 }}>
                <p style={{ fontSize: 11, color: 'var(--color-text-muted)', marginBottom: 4 }}>Confidence</p>
                <p style={{ fontSize: 20, fontWeight: 800, color: '#60a5fa', marginBottom: 12 }}>
                  {((ins.confidence || 0) * 100).toFixed(0)}%
                </p>
                {ins.financial_impact_estimate && (
                  <p style={{ fontSize: 11, color: '#f59e0b', marginBottom: 12 }}>
                    ~${ins.financial_impact_estimate?.toLocaleString()} est. risk
                  </p>
                )}
                {status === 'active' && (
                  <button
                    className="btn btn-secondary"
                    style={{ fontSize: 11, padding: '5px 12px' }}
                    onClick={() => ackMutation.mutate(ins.id)}
                  >
                    <Check size={12} /> Acknowledge
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
