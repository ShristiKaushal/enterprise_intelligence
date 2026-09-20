import { useState } from 'react'
import { BarChart2, ExternalLink, RefreshCw, Check, Copy, Info } from 'lucide-react'
import toast from 'react-hot-toast'

export default function TableauPage() {
  const [embedUrl, setEmbedUrl] = useState<string>(
    localStorage.getItem('eip_tableau_embed_url') || ''
  )
  const [inputUrl, setInputUrl] = useState<string>(embedUrl)
  const [isEditing, setIsEditing] = useState<boolean>(!embedUrl)

  const handleSaveUrl = (e: React.FormEvent) => {
    e.preventDefault()
    setEmbedUrl(inputUrl)
    localStorage.setItem('eip_tableau_embed_url', inputUrl)
    setIsEditing(false)
    toast.success('Tableau embed URL saved!')
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              padding: 8, borderRadius: 8,
              background: 'rgba(233,118,39,0.12)', border: '1px solid rgba(233,118,39,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <BarChart2 size={20} color="#e97627" />
            </div>
            <div>
              <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--color-text-primary)' }}>Tableau BI Dashboard</h1>
              <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>
                Embedded interactive Tableau visualization connected live to PostgreSQL Star Schema
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="btn btn-secondary"
            style={{ fontSize: 12 }}
          >
            {isEditing ? 'Close Embed Settings' : 'Configure Embed URL'}
          </button>
        </div>
      </div>

      {/* Embed Config Drawer / Form */}
      {isEditing && (
        <div className="glass-card" style={{ padding: 20, marginBottom: 24, border: '1px solid rgba(233,118,39,0.3)' }}>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 8 }}>
            📊 Embed Your Tableau Dashboard
          </h3>
          <p style={{ fontSize: 12, color: 'var(--color-text-secondary)', marginBottom: 16 }}>
            Paste the Share / Embed Link from your Tableau Public, Tableau Server, or Tableau Cloud workbook below.
          </p>

          <form onSubmit={handleSaveUrl} style={{ display: 'flex', gap: 12 }}>
            <input
              type="url"
              className="input"
              placeholder="https://public.tableau.com/views/YourWorkbook/YourDashboard?:embed=y&:showVizHome=n"
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              style={{ flex: 1 }}
            />
            <button type="submit" className="btn btn-primary" style={{ whiteSpace: 'nowrap' }}>
              Save Dashboard Link
            </button>
          </form>

          <div style={{ marginTop: 16, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 12 }}>
            <div style={{ padding: 12, background: 'rgba(15,23,42,0.6)', borderRadius: 8, fontSize: 12 }}>
              <div style={{ fontWeight: 600, color: '#60a5fa', marginBottom: 4 }}>Example Tableau Public Embed URL:</div>
              <code style={{ fontSize: 11, color: 'var(--color-text-secondary)', wordBreak: 'break-all' }}>
                https://public.tableau.com/views/Regional/GlobalSales?:showVizHome=no&:embed=true
              </code>
            </div>
            <div style={{ padding: 12, background: 'rgba(15,23,42,0.6)', borderRadius: 8, fontSize: 12 }}>
              <div style={{ fontWeight: 600, color: '#10b981', marginBottom: 4 }}>PostgreSQL Connection Parameters:</div>
              <div style={{ color: 'var(--color-text-secondary)', fontSize: 11 }}>
                Server: <code>localhost:5432</code> | DB: <code>enterprise_intelligence</code> | User: <code>eip_user</code>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Embed Display */}
      {embedUrl ? (
        <div className="glass-card" style={{ padding: 0, overflow: 'hidden', height: 800, border: '1px solid var(--color-bg-border)' }}>
          <iframe
            src={embedUrl}
            title="Tableau BI Dashboard"
            width="100%"
            height="100%"
            style={{ border: 'none' }}
            allowFullScreen
          />
        </div>
      ) : (
        <div className="glass-card" style={{ padding: 48, textAlign: 'center' }}>
          <div style={{
            width: 64, height: 64, borderRadius: '50%',
            background: 'rgba(233,118,39,0.1)', border: '1px solid rgba(233,118,39,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <BarChart2 size={32} color="#e97627" />
          </div>

          <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 8 }}>
            No Tableau Dashboard Embedded Yet
          </h2>

          <p style={{ fontSize: 13, color: 'var(--color-text-secondary)', maxWidth: 600, margin: '0 auto 24px', lineHeight: 1.5 }}>
            Connect Tableau Desktop to your local PostgreSQL database, build your visualizations, publish your dashboard to Tableau Public/Server, and paste the embed URL here to view it natively inside the Enterprise Intelligence Platform.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 32 }}>
            <button
              onClick={() => setIsEditing(true)}
              className="btn btn-primary"
            >
              Paste Embed URL Now
            </button>
            <button
              onClick={() => copyToClipboard('postgresql://eip_user:eip_password@localhost:5432/enterprise_intelligence')}
              className="btn btn-secondary"
            >
              <Copy size={14} /> Copy PostgreSQL Connection String
            </button>
          </div>

          {/* Quick Tableau Specs Cheat-sheet */}
          <div style={{
            textAlign: 'left',
            background: 'rgba(15,23,42,0.8)',
            border: '1px solid var(--color-bg-border)',
            borderRadius: 12,
            padding: 24,
            maxWidth: 900,
            margin: '0 auto'
          }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, color: '#e97627', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>
              📌 Quick Setup & Relationship Guide for Tableau Desktop
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: 12, color: 'var(--color-text-primary)', marginBottom: 6 }}>
                  1. Fact & Dimension Relationships:
                </div>
                <ul style={{ fontSize: 12, color: 'var(--color-text-secondary)', paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <li><code>fact_ticket.customer_id</code> = <code>dim_customer.id</code></li>
                  <li><code>fact_ticket.service_id</code> = <code>dim_service.id</code></li>
                  <li><code>fact_ticket.assigned_to_id</code> = <code>dim_employee.id</code></li>
                  <li><code>fact_incident.service_id</code> = <code>dim_service.id</code></li>
                </ul>
              </div>

              <div>
                <div style={{ fontWeight: 600, fontSize: 12, color: 'var(--color-text-primary)', marginBottom: 6 }}>
                  2. Ready-Made Pre-computed Tables:
                </div>
                <ul style={{ fontSize: 12, color: 'var(--color-text-secondary)', paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <li><code>analytics_customer_health</code> (Health Scores & Risk)</li>
                  <li><code>analytics_sentiment</code> (12-Month Trends)</li>
                  <li><code>analytics_anomalies</code> (Metric Deviations)</li>
                  <li><code>analytics_data_quality</code> (Completeness Scores)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
