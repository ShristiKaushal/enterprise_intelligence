import { useQuery } from '@tanstack/react-query'
import { documentsApi } from '@/services/api'
import { Database, FileText, RefreshCw } from 'lucide-react'
import { format } from 'date-fns'

const STATUS_COLOR: Record<string, string> = {
  completed: '#10b981', failed: '#f43f5e', processing: '#3b82f6', uploaded: '#f59e0b', pending: '#94a3b8',
}

export default function DataSourcesPage() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['documents', 'all'],
    queryFn: () => documentsApi.list({ page: 1, page_size: 50 }).then(r => r.data),
    refetchInterval: 15_000,
  })

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Data Sources</h1>
          <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>All ingested documents and their processing status</p>
        </div>
        <button className="btn btn-secondary" onClick={() => refetch()}><RefreshCw size={13} /> Refresh</button>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 20 }}>
        {[
          { label: 'Total', val: data?.total ?? 0, color: '#3b82f6' },
          { label: 'Completed', val: data?.items?.filter((d: any) => d.status === 'completed').length ?? 0, color: '#10b981' },
          { label: 'Processing', val: data?.items?.filter((d: any) => d.status === 'processing').length ?? 0, color: '#f59e0b' },
          { label: 'Failed', val: data?.items?.filter((d: any) => d.status === 'failed').length ?? 0, color: '#f43f5e' },
        ].map(s => (
          <div key={s.label} className="kpi-card" style={{ padding: '16px 20px', '--card-accent': `linear-gradient(90deg, ${s.color}, ${s.color})` } as any}>
            <p style={{ fontSize: 11, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>{s.label}</p>
            <p style={{ fontSize: 26, fontWeight: 800, color: s.color }}>{s.val}</p>
          </div>
        ))}
      </div>

      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr><th>File</th><th>Type</th><th>Domain</th><th>Status</th><th>Pages</th><th>Words</th><th>Confidence</th><th>Uploaded</th></tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={8} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>Loading…</td></tr>}
            {!isLoading && !data?.items?.length && (
              <tr><td colSpan={8} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>No documents yet — go to Upload to add files</td></tr>
            )}
            {data?.items?.map((doc: any) => (
              <tr key={doc.id}>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <FileText size={14} style={{ color: '#60a5fa', flexShrink: 0 }} />
                    <span style={{ fontSize: 12.5, maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {doc.original_filename}
                    </span>
                  </div>
                </td>
                <td><span className="badge badge-info">{doc.file_type?.toUpperCase()}</span></td>
                <td style={{ fontSize: 12, color: 'var(--color-text-secondary)', textTransform: 'capitalize' }}>{doc.domain?.replace('_', ' ')}</td>
                <td>
                  <span style={{ fontSize: 12, fontWeight: 600, color: STATUS_COLOR[doc.status] || '#94a3b8', textTransform: 'capitalize' }}>
                    {doc.status}
                  </span>
                </td>
                <td style={{ fontSize: 12.5 }}>{doc.page_count ?? '—'}</td>
                <td style={{ fontSize: 12.5 }}>{doc.word_count?.toLocaleString() ?? '—'}</td>
                <td style={{ fontSize: 12.5 }}>
                  {doc.extraction_confidence != null
                    ? <span style={{ color: doc.extraction_confidence > 0.7 ? '#10b981' : '#f59e0b' }}>{(doc.extraction_confidence * 100).toFixed(0)}%</span>
                    : '—'}
                </td>
                <td style={{ fontSize: 11.5, color: 'var(--color-text-muted)' }}>
                  {doc.created_at ? format(new Date(doc.created_at), 'MMM d, HH:mm') : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
