import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { documentsApi } from '@/services/api'

const DOMAINS = [
  { value: 'customer_intelligence', label: 'Customer Intelligence' },
  { value: 'it_operations', label: 'IT / Operations' },
  { value: 'document_intelligence', label: 'Document / Contract' },
  { value: 'unknown', label: 'Auto-detect' },
]

const ALLOWED = ['.pdf', '.docx', '.doc', '.txt', '.csv', '.xlsx', '.xls', '.log', '.md']

interface UploadItem {
  file: File
  domain: string
  status: 'pending' | 'uploading' | 'done' | 'error'
  docId?: string
  error?: string
}

export default function UploadPage() {
  const [items, setItems] = useState<UploadItem[]>([])
  const [domain, setDomain] = useState('customer_intelligence')
  const [uploading, setUploading] = useState(false)

  const onDrop = useCallback((accepted: File[]) => {
    setItems(prev => [
      ...prev,
      ...accepted.map(f => ({ file: f, domain, status: 'pending' as const })),
    ])
  }, [domain])

  const { getRootProps, getInputProps, isDragActive } = (useDropzone as any)({
    onDrop,
    accept: { 'application/*': ALLOWED, 'text/*': ['.txt', '.csv', '.log', '.md'] },
    maxSize: 100 * 1024 * 1024,
  })

  const remove = (i: number) => setItems(prev => prev.filter((_, idx) => idx !== i))

  const uploadAll = async () => {
    const pending = items.filter(i => i.status === 'pending')
    if (!pending.length) return
    setUploading(true)
    for (let i = 0; i < items.length; i++) {
      if (items[i].status !== 'pending') continue
      setItems(prev => prev.map((it, idx) => idx === i ? { ...it, status: 'uploading' } : it))
      try {
        const res = await documentsApi.upload(items[i].file, items[i].domain)
        setItems(prev => prev.map((it, idx) => idx === i ? { ...it, status: 'done', docId: res.data.id } : it))
        toast.success(`Uploaded: ${items[i].file.name}`)
      } catch (err: any) {
        const msg = err?.response?.data?.detail || 'Upload failed'
        setItems(prev => prev.map((it, idx) => idx === i ? { ...it, status: 'error', error: msg } : it))
        toast.error(msg)
      }
    }
    setUploading(false)
  }

  const fmtSize = (bytes: number) => bytes > 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : `${Math.round(bytes / 1024)} KB`

  return (
    <div style={{ padding: '24px 28px', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Upload Data</h1>
        <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>
          Upload files for AI extraction, normalization, and analysis
        </p>
      </div>

      {/* Domain selector */}
      <div className="glass-card" style={{ padding: 20, marginBottom: 20 }}>
        <label style={{ display: 'block', fontSize: 12.5, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 8 }}>
          Business Domain
        </label>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          {DOMAINS.map(d => (
            <button
              key={d.value}
              onClick={() => setDomain(d.value)}
              className={`btn ${domain === d.value ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: 13, padding: '7px 16px' }}
            >
              {d.label}
            </button>
          ))}
        </div>
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`drop-zone ${isDragActive ? 'drag-over' : ''}`}
        style={{ marginBottom: 20 }}
      >
        <input {...getInputProps()} />
        <Upload size={36} style={{ color: isDragActive ? '#3b82f6' : '#475569', margin: '0 auto 12px' }} />
        <p style={{ fontSize: 15, fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 6 }}>
          {isDragActive ? 'Drop files here…' : 'Drag & drop files, or click to browse'}
        </p>
        <p style={{ fontSize: 12.5, color: 'var(--color-text-secondary)' }}>
          Supports: PDF, DOCX, TXT, CSV, XLSX — up to 100 MB each
        </p>
      </div>

      {/* File list */}
      {items.length > 0 && (
        <div className="glass-card" style={{ padding: 0, overflow: 'hidden', marginBottom: 20 }}>
          {items.map((item, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 14,
              padding: '14px 20px',
              borderBottom: i < items.length - 1 ? '1px solid var(--color-bg-border)' : 'none',
            }}>
              <FileText size={18} style={{ color: '#60a5fa', flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontSize: 13.5, fontWeight: 500, color: 'var(--color-text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {item.file.name}
                </p>
                <p style={{ fontSize: 11.5, color: 'var(--color-text-muted)', marginTop: 2 }}>
                  {fmtSize(item.file.size)} · {DOMAINS.find(d => d.value === item.domain)?.label}
                  {item.error && <span style={{ color: '#f43f5e', marginLeft: 8 }}>· {item.error}</span>}
                  {item.docId && <span style={{ color: '#10b981', marginLeft: 8 }}>· Queued for processing</span>}
                </p>
              </div>
              <div style={{ flexShrink: 0 }}>
                {item.status === 'pending' && <span style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>Pending</span>}
                {item.status === 'uploading' && <Loader2 size={16} style={{ color: '#60a5fa', animation: 'spin 1s linear infinite' }} />}
                {item.status === 'done' && <CheckCircle2 size={16} style={{ color: '#10b981' }} />}
                {item.status === 'error' && <AlertCircle size={16} style={{ color: '#f43f5e' }} />}
              </div>
              {item.status === 'pending' && (
                <button onClick={() => remove(i)} style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer' }}>
                  <X size={15} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', gap: 10 }}>
        <button
          className="btn btn-primary"
          onClick={uploadAll}
          disabled={uploading || !items.some(i => i.status === 'pending')}
          style={{ gap: 8 }}
        >
          {uploading ? <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> : <Upload size={15} />}
          {uploading ? 'Uploading…' : `Upload ${items.filter(i => i.status === 'pending').length} File(s)`}
        </button>
        {items.length > 0 && (
          <button className="btn btn-secondary" onClick={() => setItems([])}>
            Clear All
          </button>
        )}
      </div>
    </div>
  )
}
