import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { reviewApi } from '@/services/api'
import { GitBranch, Check, X, Eye, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

const PRIORITY_COLOR: Record<string, string> = { high: '#f43f5e', medium: '#f59e0b', low: '#3b82f6' }

export default function ReviewPage() {
  const [status, setStatus] = useState('pending')
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['review', status],
    queryFn: () => reviewApi.list({ status }).then(r => r.data),
  })

  const actionMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: string }) =>
      reviewApi.action(id, action),
    onSuccess: (_, { action }) => {
      toast.success(`Item ${action}`)
      qc.invalidateQueries({ queryKey: ['review'] })
    },
  })

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1100, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Review Queue</h1>
          <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>
            Human-in-the-loop: low-confidence extractions and ambiguous entity resolutions
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['pending', 'approved', 'rejected'].map(s => (
            <button key={s} onClick={() => setStatus(s)}
              className={`btn ${status === s ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: 12, padding: '7px 14px', textTransform: 'capitalize' }}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {!isLoading && !data?.items?.length && (
        <div style={{ textAlign: 'center', padding: '80px 0' }}>
          <GitBranch size={40} style={{ color: 'var(--color-text-muted)', margin: '0 auto 12px' }} />
          <p style={{ fontSize: 15, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 6 }}>
            {status === 'pending' ? 'No items pending review' : `No ${status} items`}
          </p>
          <p style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>
            {status === 'pending'
              ? 'Low-confidence extractions will appear here automatically'
              : 'Reviewed items appear here once actioned'}
          </p>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {data?.items?.map((item: any) => (
          <div key={item.id} className="glass-card" style={{ padding: 20, borderLeft: `3px solid ${PRIORITY_COLOR[item.priority] || '#475569'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <span style={{ fontSize: 11, padding: '2px 8px', background: 'rgba(30,45,71,0.6)', borderRadius: 4, color: 'var(--color-text-secondary)', textTransform: 'capitalize' }}>
                    {item.item_type?.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontSize: 11, color: PRIORITY_COLOR[item.priority], fontWeight: 600, textTransform: 'capitalize' }}>
                    {item.priority} priority
                  </span>
                  <span style={{ fontSize: 11, color: 'var(--color-text-muted)', marginLeft: 'auto' }}>
                    {item.created_at ? format(new Date(item.created_at), 'MMM d, HH:mm') : ''}
                  </span>
                </div>
                <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 4 }}>{item.title}</p>
                <p style={{ fontSize: 13, color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>{item.description}</p>
                <p style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 8 }}>
                  Confidence: <strong style={{ color: item.confidence < 0.6 ? '#f43f5e' : '#f59e0b' }}>{((item.confidence || 0) * 100).toFixed(0)}%</strong>
                </p>
              </div>

              {status === 'pending' && (
                <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                  <button
                    className="btn btn-secondary"
                    style={{ fontSize: 12, padding: '7px 14px', color: '#10b981', borderColor: 'rgba(16,185,129,0.3)' }}
                    onClick={() => actionMutation.mutate({ id: item.id, action: 'approved' })}
                    disabled={actionMutation.isPending}
                  >
                    <Check size={13} /> Approve
                  </button>
                  <button
                    className="btn btn-danger"
                    style={{ fontSize: 12, padding: '7px 14px' }}
                    onClick={() => actionMutation.mutate({ id: item.id, action: 'rejected' })}
                    disabled={actionMutation.isPending}
                  >
                    <X size={13} /> Reject
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
