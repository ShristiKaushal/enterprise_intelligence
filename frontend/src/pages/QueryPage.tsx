import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { queryApi } from '@/services/api'
import { Search, Send, Loader2, Sparkles, ArrowRight } from 'lucide-react'

const EXAMPLES = [
  'Which customers have the highest support risk?',
  'Show incidents from the last month',
  'Which services have worsening sentiment?',
  'Platform overview and KPIs',
  'Customers with SLA breaches and negative sentiment',
]

export default function QueryPage() {
  const [question, setQuestion] = useState('')
  const [results, setResults] = useState<any>(null)

  const mutation = useMutation({
    mutationFn: (q: string) => queryApi.ask(q).then(r => r.data),
    onSuccess: (data) => setResults(data),
  })

  const ask = (q: string) => {
    setQuestion(q)
    mutation.mutate(q)
  }

  return (
    <div style={{ padding: '24px 28px', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <Sparkles size={20} style={{ color: '#8b5cf6' }} />
          <h1 style={{ fontSize: 22, fontWeight: 800 }}>Natural Language Query</h1>
        </div>
        <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>
          Ask business questions in plain English — answers come from pre-defined safe queries, never raw AI SQL
        </p>
      </div>

      {/* Input */}
      <div className="glass-card" style={{ padding: 20, marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 10 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
            <input
              className="input"
              style={{ paddingLeft: 36 }}
              placeholder="Ask a business question…"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && question.trim() && ask(question)}
            />
          </div>
          <button
            className="btn btn-primary"
            onClick={() => ask(question)}
            disabled={!question.trim() || mutation.isPending}
            style={{ flexShrink: 0 }}
          >
            {mutation.isPending ? <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={15} />}
            Ask
          </button>
        </div>

        {/* Example questions */}
        <div style={{ marginTop: 14 }}>
          <p style={{ fontSize: 11.5, color: 'var(--color-text-muted)', marginBottom: 8 }}>Try these questions:</p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {EXAMPLES.map(ex => (
              <button
                key={ex}
                onClick={() => ask(ex)}
                style={{
                  fontSize: 12, padding: '5px 12px',
                  background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.25)',
                  borderRadius: 20, color: '#a78bfa', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 5,
                  transition: 'all 0.15s',
                }}
              >
                <ArrowRight size={11} />
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results */}
      {results && (
        <div className="glass-card animate-fade-in" style={{ padding: 24 }}>
          <div style={{ marginBottom: 16 }}>
            <p style={{ fontSize: 11.5, color: 'var(--color-text-muted)', marginBottom: 4 }}>Question</p>
            <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-text-primary)' }}>"{results.question}"</p>
          </div>

          {results.matched_description && (
            <div style={{ padding: '10px 14px', background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, marginBottom: 16 }}>
              <p style={{ fontSize: 12.5, color: '#a78bfa' }}>
                <strong>Matched intent:</strong> {results.matched_description}
              </p>
            </div>
          )}

          <p style={{ fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 16, lineHeight: 1.6 }}>{results.explanation}</p>

          {/* Results table */}
          {Array.isArray(results.results) && results.results.length > 0 && (
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    {Object.keys(results.results[0]).map(k => (
                      <th key={k} style={{ textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.results.map((row: any, i: number) => (
                    <tr key={i}>
                      {Object.values(row).map((v: any, j) => (
                        <td key={j} style={{ fontSize: 12.5 }}>{String(v ?? '—')}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Dict results */}
          {results.results && !Array.isArray(results.results) && typeof results.results === 'object' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              {Object.entries(results.results).map(([k, v]) => (
                <div key={k} style={{ padding: '14px 16px', background: 'rgba(30,45,71,0.4)', borderRadius: 8, border: '1px solid var(--color-bg-border)' }}>
                  <p style={{ fontSize: 11, color: 'var(--color-text-muted)', textTransform: 'capitalize', marginBottom: 4 }}>{k.replace(/_/g, ' ')}</p>
                  <p style={{ fontSize: 20, fontWeight: 800, color: 'var(--color-text-primary)' }}>{String(v)}</p>
                </div>
              ))}
            </div>
          )}

          {results.intent === 'unknown' && (
            <div style={{ marginTop: 12 }}>
              <p style={{ fontSize: 12.5, color: 'var(--color-text-secondary)', marginBottom: 8 }}>Supported question types:</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {results.supported_questions?.map((q: string) => (
                  <button key={q} onClick={() => ask(q)} className="nav-item" style={{ textAlign: 'left', color: '#60a5fa' }}>
                    <ArrowRight size={12} /> {q}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
