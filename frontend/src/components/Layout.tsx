import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Database, Upload, Cpu, Users, AlertTriangle,
  BarChart3, Lightbulb, Activity, Shield, Search, GitBranch,
  Settings, LogOut, Brain, ChevronRight, Bell,
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/services/api'

const NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/upload', icon: Upload, label: 'Upload Data' },
  { to: '/processing', icon: Cpu, label: 'Processing' },
  { to: '/data-sources', icon: Database, label: 'Data Sources' },
  { label: 'INTELLIGENCE', isSection: true },
  { to: '/insights', icon: Lightbulb, label: 'Insights' },
  { to: '/anomalies', icon: Activity, label: 'Anomalies' },
  { to: '/query', icon: Search, label: 'NL Query' },
  { label: 'ENTITIES', isSection: true },
  { to: '/customers', icon: Users, label: 'Customers' },
  { to: '/incidents', icon: AlertTriangle, label: 'Incidents' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { label: 'GOVERNANCE', isSection: true },
  { to: '/data-quality', icon: Shield, label: 'Data Quality' },
  { to: '/review', icon: GitBranch, label: 'Review Queue' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const { data: overview } = useQuery({
    queryKey: ['overview'],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
    refetchInterval: 60_000,
  })

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside style={{
        width: 240,
        background: 'var(--color-bg-secondary)',
        borderRight: '1px solid var(--color-bg-border)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
        overflow: 'hidden',
      }}>
        {/* Logo */}
        <div style={{ padding: '20px 16px 16px', borderBottom: '1px solid var(--color-bg-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 34, height: 34,
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              borderRadius: 8,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Brain size={18} color="white" />
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--color-text-primary)', lineHeight: 1.2 }}>EIP</div>
              <div style={{ fontSize: 10, color: 'var(--color-text-muted)', letterSpacing: '0.05em' }}>Intelligence Platform</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, overflowY: 'auto', padding: '8px 8px' }}>
          {NAV.map((item, i) =>
            item.isSection ? (
              <div key={i} style={{
                fontSize: 10, fontWeight: 700, color: 'var(--color-text-muted)',
                letterSpacing: '0.1em', padding: '14px 8px 4px',
              }}>
                {item.label}
              </div>
            ) : (
              <NavLink
                key={item.to}
                to={item.to!}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <item.icon size={15} />
                {item.label}
              </NavLink>
            )
          )}
        </nav>

        {/* User */}
        <div style={{ padding: '12px 12px', borderTop: '1px solid var(--color-bg-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 30, height: 30, borderRadius: '50%',
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 12, fontWeight: 700, color: 'white', flexShrink: 0,
            }}>
              {user?.full_name?.[0] || 'U'}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--color-text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.full_name}
              </div>
              <div style={{ fontSize: 10, color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>{user?.role}</div>
            </div>
            <button
              onClick={() => { logout(); navigate('/login') }}
              style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer', padding: 4 }}
              title="Logout"
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top bar */}
        <header style={{
          height: 52,
          background: 'var(--color-bg-secondary)',
          borderBottom: '1px solid var(--color-bg-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-text-secondary)', fontSize: 13 }}>
            <span>Enterprise Intelligence Platform</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {overview && (
              <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'var(--color-text-secondary)' }}>
                {(overview.critical_insights ?? 0) > 0 && (
                  <span style={{ color: '#f43f5e', fontWeight: 600 }}>
                    ⚡ {overview.critical_insights} critical insights
                  </span>
                )}
                <span>{overview.total_customers ?? 0} customers</span>
                <span>{overview.open_incidents ?? 0} open incidents</span>
              </div>
            )}
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 6px #10b981' }} title="Connected" />
          </div>
        </header>

        {/* Page content */}
        <main style={{ flex: 1, overflowY: 'auto', background: 'var(--color-bg-primary)' }}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
