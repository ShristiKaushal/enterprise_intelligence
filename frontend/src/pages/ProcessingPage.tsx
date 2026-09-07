import { useQuery } from '@tanstack/react-query'
import { jobsApi, documentsApi } from '@/services/api'
import { Cpu, RefreshCw, CheckCircle2, XCircle, Clock, Loader2 } from 'lucide-react'
import { format } from 'date-fns'

const STATUS_COLOR: Record<string, string> = {
  completed: '#10b981', failed: '#f43f5e', running: '#3b82f6', pending: '#f59e0b',
}

export default function ProcessingPage() {
  const { data: jobs, isLoading, refetch } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.list({ page: 1 }).then(r => r.data),
    refetchInterval: 5000,
  })
  const { data: docs } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsApi.list({ page: 1, page_size: 50 }).then(r => r.data),
  })

  const StatusIcon = ({ s }: { s: string }) => {
    if (s === 'completed') return <CheckCircle2 size={14} style={{ color: '#10b981' }} />
    if (s === 'failed') return <XCircle size={14} style={{ color: '#f43f5e' }} />
    if (s === 'running') return <Loader2 size={14} style={{ color: '#3b82f6', animation: 'spin 1s linear infinite' }} />
    return <Clock size={14} style={{ color: '#f59e0b' }} />
  }

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Processing Jobs</h1>
          <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Monitor pipeline execution status</p>
        </div>
        <button className="btn btn-secondary" onClick={() => refetch()}><RefreshCw size={13} /> Refresh</button>
      </div>

      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Status</th><th>Document</th><th>Job Type</th><th>Progress</th>
              <th>Step</th><th>Duration</th><th>Started</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr><td colSpan={7} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>Loading jobs…</td></tr>
            )}
            {!isLoading && !jobs?.length && (
              <tr><td colSpan={7} style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-muted)' }}>No jobs yet — upload a document to start processing</td></tr>
            )}
            {jobs?.map((job: any) => (
              <tr key={job.id}>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <StatusIcon s={job.status} />
                    <span style={{ fontSize: 12.5, color: STATUS_COLOR[job.status] || '#94a3b8', fontWeight: 600, textTransform: 'capitalize' }}>
                      {job.status}
                    </span>
                  </div>
                </td>
                <td><span className="mono" style={{ fontSize: 11 }}>{job.document_id?.slice(0, 12)}…</span></td>
                <td><span style={{ fontSize: 12.5, textTransform: 'capitalize' }}>{job.job_type?.replace('_', ' ')}</span></td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div className="progress-bar" style={{ width: 80 }}>
                      <div className="progress-fill" style={{ width: `${job.progress || 0}%` }} />
                    </div>
                    <span style={{ fontSize: 11.5, color: 'var(--color-text-secondary)' }}>{job.progress || 0}%</span>
                  </div>
                </td>
                <td style={{ fontSize: 12.5, color: 'var(--color-text-secondary)' }}>{job.current_step || '—'}</td>
                <td style={{ fontSize: 12.5 }}>{job.duration_seconds ? `${job.duration_seconds.toFixed(1)}s` : '—'}</td>
                <td style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
                  {job.started_at ? format(new Date(job.started_at), 'HH:mm:ss') : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
