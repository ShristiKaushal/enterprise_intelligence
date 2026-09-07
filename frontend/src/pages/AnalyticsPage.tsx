import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/services/api'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  AreaChart, Area, PieChart, Pie, Cell, Legend,
} from 'recharts'

const TT_STYLE = { background: '#111827', border: '1px solid #1e2d47', borderRadius: 8, fontSize: 12 }

export default function AnalyticsPage() {
  const { data: overview } = useQuery({ queryKey: ['overview'], queryFn: () => analyticsApi.overview().then(r => r.data) })
  const { data: sentimentTrend } = useQuery({ queryKey: ['sentiment-trend'], queryFn: () => analyticsApi.sentimentTrend().then(r => r.data) })
  const { data: healthDist } = useQuery({ queryKey: ['health-dist'], queryFn: () => analyticsApi.healthDistribution().then(r => r.data) })

  const RISK_COLORS: Record<string, string> = { CRITICAL: '#f43f5e', HIGH: '#f59e0b', MEDIUM: '#3b82f6', LOW: '#10b981', UNKNOWN: '#475569' }

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1300, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Analytics</h1>
        <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Aggregated metrics derived from PostgreSQL — Tableau-ready views</p>
      </div>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 24 }}>
        {[
          { l: 'Total Customers', v: overview?.total_customers, c: '#3b82f6' },
          { l: 'High Risk', v: overview?.high_risk_customers, c: '#f43f5e' },
          { l: 'SLA Breaches', v: overview?.sla_breaches, c: '#f59e0b' },
          { l: 'Active Insights', v: overview?.critical_insights, c: '#8b5cf6' },
        ].map(k => (
          <div key={k.l} className="kpi-card" style={{ '--card-accent': `linear-gradient(90deg, ${k.c}, ${k.c})` } as any}>
            <p style={{ fontSize: 11, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>{k.l}</p>
            <p style={{ fontSize: 30, fontWeight: 800, color: k.c }}>{k.v ?? '—'}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        {/* Sentiment trend */}
        <div className="glass-card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>
            Sentiment Trend (12 Months)
          </h3>
          {sentimentTrend?.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={sentimentTrend}>
                <defs>
                  <linearGradient id="gradPos" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} /><stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradNeg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} /><stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(30,45,71,0.5)" />
                <XAxis dataKey="period" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} unit="%" />
                <Tooltip contentStyle={TT_STYLE} formatter={(v: any) => [`${v?.toFixed(1)}%`]} />
                <Area type="monotone" dataKey="positive_pct" name="Positive" stroke="#10b981" fill="url(#gradPos)" strokeWidth={2} />
                <Area type="monotone" dataKey="neutral_pct" name="Neutral" stroke="#64748b" fill="none" strokeWidth={1.5} strokeDasharray="4 2" />
                <Area type="monotone" dataKey="negative_pct" name="Negative" stroke="#f43f5e" fill="url(#gradNeg)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)', fontSize: 13 }}>
              No sentiment data — upload documents to begin
            </div>
          )}
        </div>

        {/* Risk distribution */}
        <div className="glass-card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>
            Customer Risk Distribution
          </h3>
          {healthDist?.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={healthDist} layout="vertical" margin={{ left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(30,45,71,0.5)" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="risk_level" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} width={70} />
                <Tooltip contentStyle={TT_STYLE} />
                <Bar dataKey="count" name="Customers" radius={[0, 4, 4, 0]}>
                  {healthDist.map((entry: any) => (
                    <Cell key={entry.risk_level} fill={RISK_COLORS[entry.risk_level] || '#475569'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)', fontSize: 13 }}>
              No customer data — process customer files to populate
            </div>
          )}
        </div>
      </div>

      {/* Tableau note */}
      <div className="glass-card" style={{ padding: 20, display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ fontSize: 28 }}>📊</div>
        <div>
          <p style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 4 }}>
            Tableau Integration
          </p>
          <p style={{ fontSize: 12.5, color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
            All analytics are materialized as PostgreSQL views in the <span className="mono" style={{ color: '#60a5fa' }}>analytics</span> schema.
            Connect Tableau Desktop to <span className="mono" style={{ color: '#60a5fa' }}>postgresql://localhost:5432/enterprise_intelligence</span> and
            use the pre-built views: <span className="mono" style={{ color: '#10b981' }}>vw_executive_kpi</span>,{' '}
            <span className="mono" style={{ color: '#10b981' }}>vw_customer_health</span>,{' '}
            <span className="mono" style={{ color: '#10b981' }}>vw_sentiment_trend</span>.
          </p>
        </div>
      </div>
    </div>
  )
}
