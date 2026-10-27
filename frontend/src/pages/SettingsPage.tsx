import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { settingsApi, healthApi, getApiBaseUrl, setApiBaseUrl } from '@/services/api'
import { Settings, Cpu, Database, Shield, Globe, Save } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import toast from 'react-hot-toast'

function Row({ label, value, mono = false }: { label: string; value: any; mono?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid var(--color-bg-border)' }}>
      <span style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>{label}</span>
      <span className={mono ? 'mono' : ''} style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>{String(value ?? '—')}</span>
    </div>
  )
}

function Section({ icon: Icon, title, children }: any) {
  return (
    <div className="glass-card" style={{ padding: 24, marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <Icon size={16} style={{ color: '#60a5fa' }} />
        <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-secondary)' }}>{title}</h3>
      </div>
      {children}
    </div>
  )
}

export default function SettingsPage() {
  const user = useAuthStore(s => s.user)
  const isAdmin = user?.role === 'admin'

  const [apiUrl, setApiUrl] = useState(getApiBaseUrl())

  const { data: health, refetch: refetchHealth } = useQuery({
    queryKey: ['health'],
    queryFn: () => healthApi.check().then(r => r.data),
  })
  const { data: aiStatus } = useQuery({
    queryKey: ['ai-status'],
    queryFn: () => settingsApi.aiProvider().then(r => r.data),
  })
  const { data: sysSettings } = useQuery({
    queryKey: ['sys-settings'],
    queryFn: () => settingsApi.system().then(r => r.data),
    enabled: isAdmin,
  })

  const handleSaveApiUrl = (e: React.FormEvent) => {
    e.preventDefault()
    setApiBaseUrl(apiUrl.trim())
    toast.success('Backend API URL updated! Refreshing connection...')
    refetchHealth()
    setTimeout(() => window.location.reload(), 600)
  }

  return (
    <div style={{ padding: '24px 28px', maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Settings</h1>
        <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>System configuration and deployment status</p>
      </div>

      {/* Backend API Connection Config */}
      <Section icon={Globe} title="Backend API Connection">
        <p style={{ fontSize: 12.5, color: 'var(--color-text-secondary)', marginBottom: 14, lineHeight: 1.5 }}>
          When hosted on Vercel, connect this frontend to your deployed backend (e.g., on Railway, Render, or Fly.io). If left as localhost, the platform automatically runs in seamless Demo Mode.
        </p>
        <form onSubmit={handleSaveApiUrl} style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
          <input
            type="url"
            className="input"
            placeholder="https://your-backend.railway.app or http://localhost:8000"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            style={{ flex: 1, fontSize: 13 }}
          />
          <button type="submit" className="btn btn-primary" style={{ gap: 6, fontSize: 13, whiteSpace: 'nowrap' }}>
            <Save size={14} />
            Save & Connect
          </button>
        </form>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: 11.5, color: 'var(--color-text-muted)' }}>Current Target:</span>
          <code style={{ fontSize: 11.5, color: '#60a5fa' }}>{getApiBaseUrl()}</code>
        </div>
      </Section>

      {/* Health */}
      <Section icon={Database} title="System Health">
        <Row label="Backend Status" value={health?.status || 'Active (Demo mode)'} />
        <Row label="Database" value={health?.database || 'Connected'} />
        <Row label="Environment" value={health?.env || 'Production'} />
        <Row label="Version" value={health?.version || '1.0.0'} mono />
      </Section>

      {/* AI Provider */}
      <Section icon={Cpu} title="AI Provider">
        <Row label="Provider" value={aiStatus?.provider || 'Mock AI Engine (Offline / Demo)'} />
        <Row label="Model" value={aiStatus?.model_version || 'v1.0-embedded'} mono />
        <Row label="Available" value={aiStatus?.available !== false ? '✓ Online' : '✗ Offline'} />
      </Section>

      {/* System config (admin only) */}
      {isAdmin && (
        <Section icon={Settings} title="System Configuration">
          <Row label="App Name" value={sysSettings?.app_name || 'Enterprise Intelligence Platform'} />
          <Row label="AI Provider" value={sysSettings?.ai_provider || 'mock'} />
          <Row label="Max File Size" value={`${sysSettings?.max_file_size_mb || 100} MB`} />
          <Row label="Allowed Extensions" value={sysSettings?.allowed_extensions?.join(', ') || 'pdf, docx, txt, csv, xlsx, xls, json'} />
          <Row label="Job Backend" value={sysSettings?.job_backend || 'memory'} />
          <Row label="ML Models Enabled" value={sysSettings?.enable_ml_models !== false ? '✓ Yes' : '✗ No'} />
        </Section>
      )}

      {/* User info */}
      <Section icon={Shield} title="Your Account">
        <Row label="Name" value={user?.full_name} />
        <Row label="Email" value={user?.email} mono />
        <Row label="Role" value={user?.role} />
        <Row label="Status" value={user?.is_active ? '✓ Active' : '✗ Inactive'} />
      </Section>

      {/* Tableau guide */}
      <div className="glass-card" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-secondary)', marginBottom: 14 }}>
          📊 Tableau Connection
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            ['Server', 'localhost'],
            ['Port', '5432'],
            ['Database', 'enterprise_intelligence'],
            ['Username', 'eip_user'],
            ['Schema', 'analytics'],
          ].map(([k, v]) => (
            <div key={k} style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <span style={{ fontSize: 12, color: 'var(--color-text-muted)', width: 80 }}>{k}</span>
              <code style={{ fontSize: 12, color: '#60a5fa' }}>{v}</code>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
