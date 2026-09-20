import { useQuery } from '@tanstack/react-query'
import { analyticsApi, insightsApi } from '@/services/api'
import {
  Users, AlertTriangle, Shield, TrendingUp, Zap, Activity,
  ArrowUpRight, ArrowDownRight, BarChart2, RefreshCw,
} from 'lucide-react'
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  Tooltip, AreaChart, Area, PieChart, Pie, Cell, Legend,
} from 'recharts'
import { useNavigate } from 'react-router-dom'
import { format } from 'date-fns'

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: '#f43f5e', HIGH: '#f59e0b', MEDIUM: '#3b82f6', LOW: '#10b981',
}
const SENTIMENT_COLORS = ['#10b981', '#94a3b8', '#f43f5e']

function KpiCard({ label, value, sub, color, icon: Icon, trend }: any) {
  return (
    <div className="kpi-card hover-lift" style={{ '--card-accent': color } as any}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ fontSize: 11.5, color: 'var(--color-text-secondary)', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 8 }}>{label}</p>
          <p style={{ fontSize: 28, fontWeight: 800, color: 'var(--color-text-primary)', lineHeight: 1 }}>{value ?? '—'}</p>
          {sub && <p style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 6 }}>{sub}</p>}
        </div>
        <div style={{ padding: 10, borderRadius: 10, background: 'rgba(59,130,246,0.08)' }}>
          <Icon size={20} style={{ color: '#60a5fa' }} />
        </div>
      </div>
      {trend !== undefined && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 12 }}>
          {trend > 0
            ? <ArrowUpRight size={13} style={{ color: '#f43f5e' }} />
            : <ArrowDownRight size={13} style={{ color: '#10b981' }} />
          }
          <span style={{ fontSize: 11.5, color: trend > 0 ? '#f43f5e' : '#10b981', fontWeight: 600 }}>
            {Math.abs(trend)}% vs last month
          </span>
        </div>
      )}
    </div>
  )
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 style={{ fontSize: 14, fontWeight: 700, color: 'var(--color-text-secondary)', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 14 }}>
      {children}
    </h2>
  )
}

export default function DashboardPage() {
  const navigate = useNavigate()

  const { data: overview, isLoading: ovLoading, refetch } = useQuery({
    queryKey: ['overview'],
    queryFn: () => analyticsApi.overview().then(r => r.data),
    refetchInterval: 30_000,
  })

  const { data: sentimentTrend } = useQuery({
    queryKey: ['sentiment-trend'],
    queryFn: () => analyticsApi.sentimentTrend().then(r => r.data),
  })

  const { data: healthDist } = useQuery({
    queryKey: ['health-dist'],
    queryFn: () => analyticsApi.healthDistribution().then(r => r.data),
  })

  const { data: insightsRes } = useQuery({
    queryKey: ['insights', 'critical'],
    queryFn: () => insightsApi.list({ page: 1, status: 'active' }).then(r => r.data),
  })

  const p = (s: string) => ({ padding: s })

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1400, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Executive Dashboard</h1>
          <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>
            Real-time intelligence from your enterprise data
          </p>
        </div>
        <button className="btn btn-secondary" onClick={() => refetch()} style={{ gap: 6 }}>
          <RefreshCw size={13} />
          Refresh
        </button>
      </div>

      {/* KPI Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 28 }}>
        <KpiCard label="Total Customers" value={overview?.total_customers ?? '—'} icon={Users}
          color="linear-gradient(90deg, #3b82f6, #8b5cf6)" sub={`${overview?.high_risk_customers ?? 0} high risk`} />
        <KpiCard label="Open Incidents" value={overview?.open_incidents ?? '—'} icon={AlertTriangle}
          color="linear-gradient(90deg, #f43f5e, #f97316)" sub={`${overview?.sla_breaches ?? 0} SLA breaches`} />
        <KpiCard label="Active Insights" value={overview?.critical_insights ?? '—'} icon={Zap}
          color="linear-gradient(90deg, #8b5cf6, #6366f1)" sub="critical severity" />
        <KpiCard label="Open Tickets" value={overview?.open_tickets ?? '—'} icon={BarChart2}
          color="linear-gradient(90deg, #06b6d4, #3b82f6)" sub={`of ${overview?.total_tickets ?? 0} total`} />
      </div>

      {/* Charts row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20, marginBottom: 28 }}>
        {/* Sentiment trend */}
        <div className="glass-card" style={{ padding: 24 }}>
          <SectionTitle>Sentiment Trend</SectionTitle>
          {sentimentTrend?.length ? (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={sentimentTrend}>
                <defs>
                  <linearGradient id="gPos" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gNeg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="period" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} unit="%" />
                <Tooltip
                  contentStyle={{ background: '#111827', border: '1px solid #1e2d47', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: any) => [`${v?.toFixed(1)}%`]}
                />
                <Area type="monotone" dataKey="positive_pct" name="Positive" stroke="#10b981" fill="url(#gPos)" strokeWidth={2} />
                <Area type="monotone" dataKey="negative_pct" name="Negative" stroke="#f43f5e" fill="url(#gNeg)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart label="No sentiment data yet — upload documents to begin" />
          )}
        </div>

        {/* Health distribution donut */}
        <div className="glass-card" style={{ padding: 24 }}>
          <SectionTitle>Customer Risk Distribution</SectionTitle>
          {healthDist?.length ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={healthDist} dataKey="count" nameKey="risk_level" cx="50%" cy="50%" innerRadius={55} outerRadius={80} strokeWidth={0}>
                  {healthDist.map((entry: any) => (
                    <Cell key={entry.risk_level} fill={SEVERITY_COLORS[entry.risk_level] || '#475569'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1e2d47', borderRadius: 8, fontSize: 12 }} />
                <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart label="No customer risk data yet" />
          )}
        </div>
      </div>

      {/* Top insights */}
      <div className="glass-card" style={{ padding: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <SectionTitle>Top Priority Insights</SectionTitle>
          <button className="btn btn-secondary" onClick={() => navigate('/insights')} style={{ fontSize: 12, padding: '6px 14px' }}>
            View all
          </button>
        </div>
        {insightsRes?.items?.length ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {insightsRes.items.map((ins: any) => (
              <div
                key={ins.id}
                className={`insight-card ${ins.severity?.toLowerCase()}`}
                onClick={() => navigate(`/insights/${ins.id}`)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                      <span className={`badge badge-${ins.severity?.toLowerCase()}`}>{ins.severity}</span>
                      <span style={{ fontSize: 11, color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>{ins.insight_type?.replace('_', ' ')}</span>
                    </div>
                    <p style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 4 }}>{ins.title}</p>
                    <p style={{ fontSize: 12.5, color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>{ins.description}</p>
                  </div>
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <p style={{ fontSize: 11, color: 'var(--color-text-muted)', marginBottom: 4 }}>Confidence</p>
                    <p style={{ fontSize: 16, fontWeight: 700, color: '#60a5fa' }}>{((ins.confidence || 0) * 100).toFixed(0)}%</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState icon={<Zap size={32} style={{ color: 'var(--color-text-muted)' }} />}
            title="No insights yet"
            desc="Upload and process documents to generate business insights" />
        )}
      </div>
    </div>
  )
}

function EmptyChart({ label }: { label: string }) {
  return (
    <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <p style={{ fontSize: 13, color: 'var(--color-text-muted)', textAlign: 'center' }}>{label}</p>
    </div>
  )
}

function EmptyState({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div style={{ padding: '40px 0', textAlign: 'center' }}>
      <div style={{ marginBottom: 12, opacity: 0.5 }}>{icon}</div>
      <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 6 }}>{title}</p>
      <p style={{ fontSize: 12.5, color: 'var(--color-text-muted)' }}>{desc}</p>
    </div>
  )
}
