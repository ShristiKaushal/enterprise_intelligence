import { useQuery } from '@tanstack/react-query'
import { anomaliesApi } from '@/services/api'
import { Activity } from 'lucide-react'
import { format } from 'date-fns'

export default function AnomaliesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['anomalies'],
    queryFn: () => anomaliesApi.list().then(r => r.data),
    refetchInterval: 30_000,
  })

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Anomalies</h1>
        <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Statistical anomalies detected via Z-score and IQR methods</p>
      </div>

      {!isLoading && !data?.length && (
        <div style={{ textAlign: 'center', padding: '80px 0' }}>
          <Activity size={40} style={{ color: 'var(--color-text-muted)', margin: '0 auto 12px' }} />
          <p style={{ fontSize: 15, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 6 }}>No anomalies detected</p>
          <p style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>Anomalies appear after sufficient data has been processed</p>
        </div>
      )}

      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr><th>Metric</th><th>Severity</th><th>Observed</th><th>Expected</th><th>Deviation</th><th>Method</th><th>Detected</th><th>Status</th></tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={8} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>Loading…</td></tr>}
            {data?.map((a: any) => (
              <tr key={a.id}>
                <td style={{ fontSize: 13, fontWeight: 500 }}>{a.metric_name?.replace(/_/g, ' ')}</td>
                <td><span className={`badge badge-${a.severity?.toLowerCase()}`}>{a.severity}</span></td>
                <td style={{ fontSize: 13, fontWeight: 700, color: '#f43f5e' }}>{a.observed_value?.toFixed(2)}</td>
                <td style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>{a.expected_value?.toFixed(2)}</td>
                <td style={{ fontSize: 13, color: Math.abs(a.deviation_pct || 0) > 50 ? '#f43f5e' : '#f59e0b', fontWeight: 600 }}>
                  {a.deviation_pct > 0 ? '+' : ''}{a.deviation_pct?.toFixed(1)}%
                </td>
                <td><span className="badge badge-info">{a.detection_method}</span></td>
                <td style={{ fontSize: 11.5, color: 'var(--color-text-muted)' }}>
                  {a.detected_at ? format(new Date(a.detected_at), 'MMM d, HH:mm') : '—'}
                </td>
                <td>
                  <span style={{ fontSize: 12, color: a.is_resolved ? '#10b981' : '#f59e0b', fontWeight: 600 }}>
                    {a.is_resolved ? '✓ Resolved' : '⚠ Active'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
