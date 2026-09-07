import { useQuery } from '@tanstack/react-query'
import { dataQualityApi } from '@/services/api'
import { Shield } from 'lucide-react'
import { format } from 'date-fns'
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar } from 'recharts'

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 80 ? '#10b981' : score >= 65 ? '#f59e0b' : '#f43f5e'
  return <span style={{ fontSize: 14, fontWeight: 800, color }}>{score?.toFixed(0)}</span>
}

export default function DataQualityPage() {
  const { data: reports } = useQuery({ queryKey: ['dq-reports'], queryFn: () => dataQualityApi.list().then(r => r.data) })
  const { data: summary } = useQuery({ queryKey: ['dq-summary'], queryFn: () => dataQualityApi.summary().then(r => r.data) })

  const radarData = summary ? [
    { dim: 'Completeness', value: summary.avg_completeness_score },
    { dim: 'Validity', value: summary.avg_validity_score },
    { dim: 'Consistency', value: summary.avg_consistency_score || 0 },
    { dim: 'Uniqueness', value: summary.avg_uniqueness_score || 0 },
    { dim: 'Timeliness', value: summary.avg_timeliness_score || 0 },
  ] : []

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Data Quality</h1>
        <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Completeness, validity, consistency, uniqueness, and timeliness scores</p>
      </div>

      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
          {/* Radar */}
          <div className="glass-card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-secondary)', marginBottom: 14 }}>Quality Dimensions</h3>
            {radarData.some(d => d.value > 0) ? (
              <ResponsiveContainer width="100%" height={220}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(30,45,71,0.5)" />
                  <PolarAngleAxis dataKey="dim" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <Radar name="Score" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.15} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)', fontSize: 13 }}>No quality data yet</div>
            )}
          </div>

          {/* Summary stats */}
          <div className="glass-card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-secondary)', marginBottom: 14 }}>Overall Summary</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {[
                { l: 'Overall Quality Score', v: summary.avg_overall_score, unit: '/100' },
                { l: 'Total Records Assessed', v: summary.total_records_assessed?.toLocaleString(), unit: '' },
                { l: 'Invalid Records', v: summary.total_invalid_records?.toLocaleString(), unit: '' },
                { l: 'Duplicate Records', v: summary.total_duplicate_records?.toLocaleString(), unit: '' },
              ].map(s => (
                <div key={s.l} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid var(--color-bg-border)' }}>
                  <span style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>{s.l}</span>
                  <span style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-text-primary)' }}>{s.v ?? '—'}{s.unit}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Reports table */}
      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr><th>Dataset</th><th>Overall</th><th>Completeness</th><th>Validity</th><th>Total Records</th><th>Invalid</th><th>Duplicates</th><th>Date</th></tr>
          </thead>
          <tbody>
            {!reports?.length && (
              <tr><td colSpan={8} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>
                No quality reports — upload CSV/Excel files to generate assessments
              </td></tr>
            )}
            {reports?.map((r: any) => (
              <tr key={r.id}>
                <td style={{ fontSize: 13, fontWeight: 500, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.dataset_name}</td>
                <td><ScoreBadge score={r.overall_score} /></td>
                <td><ScoreBadge score={r.completeness_score} /></td>
                <td><ScoreBadge score={r.validity_score} /></td>
                <td style={{ fontSize: 12.5 }}>{r.total_records?.toLocaleString()}</td>
                <td style={{ fontSize: 12.5, color: r.invalid_records > 0 ? '#f43f5e' : 'var(--color-text-secondary)' }}>{r.invalid_records}</td>
                <td style={{ fontSize: 12.5, color: r.duplicate_records > 0 ? '#f59e0b' : 'var(--color-text-secondary)' }}>{r.duplicate_records}</td>
                <td style={{ fontSize: 11.5, color: 'var(--color-text-muted)' }}>
                  {r.report_date ? format(new Date(r.report_date), 'MMM d') : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
