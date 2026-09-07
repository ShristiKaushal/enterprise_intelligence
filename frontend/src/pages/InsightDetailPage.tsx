import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { insightsApi } from '@/services/api'
import { ArrowLeft, Check, AlertTriangle, Target, Lightbulb, TrendingUp } from 'lucide-react'
import toast from 'react-hot-toast'

export default function InsightDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: ins, isLoading } = useQuery({
    queryKey: ['insight', id],
    queryFn: () => insightsApi.get(id!).then(r => r.data),
  })

  const ackMutation = useMutation({
    mutationFn: () => insightsApi.acknowledge(id!),
    onSuccess: () => { toast.success('Acknowledged'); qc.invalidateQueries({ queryKey: ['insight', id] }) },
  })

  if (isLoading) return <div style={{ padding: 40, color: 'var(--color-text-muted)' }}>Loading…</div>
  if (!ins) return <div style={{ padding: 40, color: 'var(--color-text-muted)' }}>Insight not found</div>

  const Section = ({ icon: Icon, title, children }: any) => (
    <div className="glass-card" style={{ padding: 24, marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <Icon size={16} style={{ color: '#60a5fa' }} />
        <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-secondary)' }}>{title}</h3>
      </div>
      {children}
    </div>
  )

  return (
    <div style={{ padding: '24px 28px', maxWidth: 900, margin: '0 auto' }}>
      <button className="btn btn-secondary" onClick={() => navigate(-1)} style={{ marginBottom: 20, fontSize: 12 }}>
        <ArrowLeft size={13} /> Back to Insights
      </button>

      {/* Header */}
      <div className="glass-card" style={{ padding: 28, marginBottom: 16, borderLeft: `3px solid ${ins.severity === 'CRITICAL' ? '#f43f5e' : ins.severity === 'HIGH' ? '#f59e0b' : '#3b82f6'}` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
              <span className={`badge badge-${ins.severity?.toLowerCase()}`}>{ins.severity}</span>
              <span style={{ fontSize: 11, color: 'var(--color-text-muted)', textTransform: 'capitalize', alignSelf: 'center' }}>
                {ins.insight_type?.replace(/_/g, ' ')}
              </span>
              {ins.is_cross_domain && <span className="badge badge-info">Cross-domain</span>}
            </div>
            <h1 style={{ fontSize: 20, fontWeight: 800, marginBottom: 10, lineHeight: 1.3 }}>{ins.title}</h1>
            <p style={{ fontSize: 13.5, color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>{ins.description}</p>
          </div>
          <div style={{ textAlign: 'right', marginLeft: 20, flexShrink: 0 }}>
            <p style={{ fontSize: 11, color: 'var(--color-text-muted)', marginBottom: 4 }}>Confidence</p>
            <p style={{ fontSize: 32, fontWeight: 800, color: '#60a5fa' }}>{((ins.confidence || 0) * 100).toFixed(0)}%</p>
            <p style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 4 }}>Priority: {(ins.priority_score * 100).toFixed(0)}/100</p>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <Section icon={AlertTriangle} title="What Happened">
          <p style={{ fontSize: 13.5, color: 'var(--color-text-primary)', lineHeight: 1.6 }}>{ins.what_happened || ins.description}</p>
        </Section>
        <Section icon={TrendingUp} title="Why It Matters">
          <p style={{ fontSize: 13.5, color: 'var(--color-text-primary)', lineHeight: 1.6 }}>{ins.why_it_matters || 'See description above.'}</p>
        </Section>
      </div>

      <Section icon={Target} title="Recommended Action">
        <div style={{ background: 'rgba(59,130,246,0.06)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: 8, padding: '14px 16px' }}>
          <p style={{ fontSize: 13.5, color: 'var(--color-text-primary)', lineHeight: 1.6 }}>{ins.recommended_action || 'No recommendation generated.'}</p>
        </div>
      </Section>

      {/* Evidence */}
      {ins.evidence?.length > 0 && (
        <Section icon={Lightbulb} title="Supporting Evidence">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
            {ins.evidence.map((e: any, i: number) => (
              <div key={i} style={{ padding: '12px 14px', background: 'rgba(30,45,71,0.4)', borderRadius: 8, border: '1px solid var(--color-bg-border)' }}>
                <p style={{ fontSize: 11, color: 'var(--color-text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{e.label}</p>
                <p style={{ fontSize: 14, fontWeight: 700, color: 'var(--color-text-primary)' }}>{String(e.value)}</p>
                <p style={{ fontSize: 10, color: 'var(--color-text-muted)', marginTop: 2, textTransform: 'capitalize' }}>{e.source_type}</p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Contributing factors */}
      {ins.contributing_factors?.length > 0 && (
        <div className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
          <h3 style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-secondary)', marginBottom: 12 }}>Contributing Factors</h3>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {ins.contributing_factors.map((f: string, i: number) => (
              <span key={i} style={{ padding: '4px 12px', background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.25)', borderRadius: 20, fontSize: 12, color: '#fbbf24' }}>
                {f}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Metrics */}
      {(ins.metric_name || ins.financial_impact_estimate) && (
        <div className="glass-card" style={{ padding: 20, marginBottom: 16, display: 'flex', gap: 24 }}>
          {ins.metric_name && (
            <div>
              <p style={{ fontSize: 11, color: 'var(--color-text-muted)', marginBottom: 4 }}>Metric</p>
              <p style={{ fontSize: 13, fontWeight: 600 }}>{ins.metric_name?.replace(/_/g, ' ')}</p>
              <p style={{ fontSize: 18, fontWeight: 800, color: '#60a5fa' }}>{ins.current_value?.toFixed(1)}</p>
              {ins.change_pct != null && <p style={{ fontSize: 11, color: ins.change_pct > 0 ? '#f43f5e' : '#10b981' }}>{ins.change_pct > 0 ? '+' : ''}{ins.change_pct?.toFixed(1)}%</p>}
            </div>
          )}
          {ins.financial_impact_estimate && (
            <div>
              <p style={{ fontSize: 11, color: 'var(--color-text-muted)', marginBottom: 4 }}>Estimated Financial Impact</p>
              <p style={{ fontSize: 18, fontWeight: 800, color: '#f59e0b' }}>${ins.financial_impact_estimate?.toLocaleString()}</p>
              <p style={{ fontSize: 10, color: 'var(--color-text-muted)' }}>ESTIMATED — based on industry averages</p>
            </div>
          )}
        </div>
      )}

      {ins.status === 'active' && (
        <button className="btn btn-primary" onClick={() => ackMutation.mutate()} style={{ gap: 8 }}>
          <Check size={15} /> Acknowledge Insight
        </button>
      )}
    </div>
  )
}
