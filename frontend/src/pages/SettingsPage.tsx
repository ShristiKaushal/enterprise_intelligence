import { useQuery } from '@tanstack/react-query'
import { settingsApi, healthApi } from '@/services/api'
import { Settings, Cpu, Database, Shield, Check } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'

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

  const { data: health } = useQuery({ queryKey: ['health'], queryFn: () => healthApi.check().then(r => r.data) })
  const { data: aiStatus } = useQuery({ queryKey: ['ai-status'], queryFn: () => settingsApi.aiProvider().then(r => r.data) })
  const { data: sysSettings } = useQuery({
    queryKey: ['sys-settings'],
    queryFn: () => settingsApi.system().then(r => r.data),
    enabled: isAdmin,
  })

  return (
    <div style={{ padding: '24px 28px', maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Settings</h1>
        <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>System configuration and status</p>
      </div>

      {/* Health */}
      <Section icon={Database} title="System Health">
        <Row label="Backend Status" value={health?.status || 'Unknown'} />
        <Row label="Database" value={health?.database || '—'} />
        <Row label="Environment" value={health?.env || '—'} />
        <Row label="Version" value={health?.version || '—'} mono />
      </Section>

      {/* AI Provider */}
      <Section icon={Cpu} title="AI Provider">
        <Row label="Provider" value={aiStatus?.provider || '—'} />
        <Row label="Model" value={aiStatus?.model_version || '—'} mono />
        <Row label="Available" value={aiStatus?.available ? '✓ Online' : '✗ Offline'} />
      </Section>

      {/* System config (admin only) */}
      {isAdmin && sysSettings && (
        <Section icon={Settings} title="System Configuration">
          <Row label="App Name" value={sysSettings.app_name} />
          <Row label="AI Provider" value={sysSettings.ai_provider} />
          <Row label="Max File Size" value={`${sysSettings.max_file_size_mb} MB`} />
          <Row label="Allowed Extensions" value={sysSettings.allowed_extensions?.join(', ')} />
          <Row label="Job Backend" value={sysSettings.job_backend} />
          <Row label="ML Models Enabled" value={sysSettings.enable_ml_models ? '✓ Yes' : '✗ No'} />
          <div style={{ paddingTop: 12 }}>
            <p style={{ fontSize: 11.5, color: 'var(--color-text-muted)' }}>
              CORS Origins: {sysSettings.cors_origins?.join(', ')}
            </p>
          </div>
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
              <span className="mono" style={{ fontSize: 12, color: '#60a5fa', padding: '2px 8px', background: 'rgba(59,130,246,0.08)', borderRadius: 4 }}>{v}</span>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 16, padding: '10px 14px', background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 8 }}>
          <p style={{ fontSize: 12, color: '#10b981' }}>
            <Check size={12} style={{ display: 'inline', marginRight: 4 }} />
            Views available: vw_executive_kpi · vw_customer_health · vw_sentiment_trend · vw_incident_summary · vw_data_quality
          </p>
        </div>
      </div>
    </div>
  )
}
