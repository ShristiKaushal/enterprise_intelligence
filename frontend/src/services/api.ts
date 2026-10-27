import axios, { type AxiosResponse } from 'axios'
import {
  MOCK_USER,
  MOCK_OVERVIEW,
  MOCK_SENTIMENT_TREND,
  MOCK_HEALTH_DISTRIBUTION,
  MOCK_INSIGHTS,
  MOCK_CUSTOMERS,
  MOCK_INCIDENTS,
  MOCK_ANOMALIES,
  MOCK_DATA_QUALITY_SUMMARY,
  MOCK_DATA_QUALITY_REPORTS,
  MOCK_REVIEW_QUEUE,
  MOCK_DOCUMENTS,
  MOCK_JOBS,
  MOCK_SETTINGS_SYSTEM,
  MOCK_SETTINGS_AI,
  MOCK_HEALTH,
} from './mockData'

// Get configured API URL from localStorage, env var, or default to localhost
export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const customUrl = localStorage.getItem('eip_api_url')
    if (customUrl) return customUrl.replace(/\/+$/, '')
  }
  const rawUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  return rawUrl.replace(/\/+$/, '')
}

export function setApiBaseUrl(url: string): void {
  if (typeof window !== 'undefined') {
    if (!url) {
      localStorage.removeItem('eip_api_url')
    } else {
      localStorage.setItem('eip_api_url', url.replace(/\/+$/, ''))
    }
  }
}

export const BASE_URL = getApiBaseUrl()

export const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 8000,
})

// Dynamic baseURL updater in case user changed it in settings
api.interceptors.request.use((config) => {
  const currentBase = getApiBaseUrl()
  config.baseURL = `${currentBase}/api/v1`

  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Reactive flag indicating whether fallback demo mode was triggered
let demoModeActive = false
export function isDemoMode(): boolean {
  return demoModeActive
}

// Router to match mock endpoints when backend is unreachable
function getMockFallback(url: string = ''): any {
  const clean = url.split('?')[0].replace(/^.*\/api\/v1/, '')

  if (clean.includes('/auth/login') || clean.includes('/auth/register')) {
    return {
      access_token: 'demo_token_' + Date.now(),
      token_type: 'bearer',
      user: MOCK_USER,
    }
  }
  if (clean.includes('/auth/me')) return MOCK_USER
  if (clean.includes('/analytics/overview')) return MOCK_OVERVIEW
  if (clean.includes('/analytics/sentiment-trend')) return MOCK_SENTIMENT_TREND
  if (clean.includes('/analytics/customer-health-distribution')) return MOCK_HEALTH_DISTRIBUTION
  if (clean.includes('/insights')) {
    if (clean.match(/\/insights\/[^/]+$/)) return MOCK_INSIGHTS.items[0]
    return MOCK_INSIGHTS
  }
  if (clean.includes('/customers')) {
    if (clean.match(/\/customers\/[^/]+$/)) return MOCK_CUSTOMERS.items[0]
    return MOCK_CUSTOMERS
  }
  if (clean.includes('/incidents')) {
    if (clean.match(/\/incidents\/[^/]+$/)) return MOCK_INCIDENTS.items[0]
    return MOCK_INCIDENTS
  }
  if (clean.includes('/anomalies')) return MOCK_ANOMALIES
  if (clean.includes('/data-quality/summary')) return MOCK_DATA_QUALITY_SUMMARY
  if (clean.includes('/data-quality')) return MOCK_DATA_QUALITY_REPORTS
  if (clean.includes('/review')) return MOCK_REVIEW_QUEUE
  if (clean.includes('/documents')) return MOCK_DOCUMENTS
  if (clean.includes('/jobs')) return MOCK_JOBS
  if (clean.includes('/settings/system')) return MOCK_SETTINGS_SYSTEM
  if (clean.includes('/settings/ai-provider')) return MOCK_SETTINGS_AI
  if (clean.includes('/health')) return MOCK_HEALTH
  if (clean.includes('/query')) {
    return {
      answer:
        'Based on cross-dimensional analysis of our 10 enterprise accounts, churn risk is highest for RetailGiant Corp (82%) and Velocity Telecom (71%), linked to recent database latency spikes and pending SLA credits.',
      sources: ['Customer Health Scorecard', 'Incident Postmortem INC-2026-001', 'Q3 NPS Feedback'],
    }
  }

  return null
}

// Interceptor to handle responses and provide graceful demo fallbacks when backend is down/unreachable
api.interceptors.response.use(
  (res) => res,
  (err) => {
    // 401 Unauthorized handling
    if (err.response?.status === 401 && !err.config?.url?.includes('/auth/login')) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
      return Promise.reject(err)
    }

    // Check if network error, mixed-content block, timeout, or server error (500, 502, 503, 504, 404)
    const isNetworkOrServerError =
      !err.response ||
      err.code === 'ERR_NETWORK' ||
      err.code === 'ECONNABORTED' ||
      [404, 500, 502, 503, 504].includes(err.response?.status)

    if (isNetworkOrServerError) {
      const fallback = getMockFallback(err.config?.url)
      if (fallback !== null) {
        demoModeActive = true
        console.warn(
          `[EIP Platform] Backend at "${getApiBaseUrl()}" unreachable (${err.message || 'Network Error'}). Using demo fallback for:`,
          err.config?.url
        )

        const syntheticResponse: AxiosResponse = {
          data: fallback,
          status: 200,
          statusText: 'OK (Demo Fallback)',
          headers: {},
          config: err.config,
        }
        return Promise.resolve(syntheticResponse)
      }
    }

    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: { email: string; username: string; full_name: string; password: string; role?: string }) =>
    api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

// ── Documents ─────────────────────────────────────────────────────────────────
export const documentsApi = {
  upload: (file: File, domain: string) => {
    const form = new FormData()
    form.append('file', file)
    form.append('domain', domain)
    return api.post('/documents/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  list: (params?: { page?: number; page_size?: number; domain?: string; status?: string }) =>
    api.get('/documents', { params }),
  get: (id: string) => api.get(`/documents/${id}`),
  process: (id: string) => api.post(`/documents/${id}/process`, { job_type: 'full_pipeline' }),
}

// ── Jobs ──────────────────────────────────────────────────────────────────────
export const jobsApi = {
  list: (params?: { page?: number; status?: string }) => api.get('/jobs', { params }),
  get: (id: string) => api.get(`/jobs/${id}`),
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export const analyticsApi = {
  overview: () => api.get('/analytics/overview'),
  sentimentTrend: () => api.get('/analytics/sentiment-trend'),
  healthDistribution: () => api.get('/analytics/customer-health-distribution'),
}

// ── Customers ─────────────────────────────────────────────────────────────────
export const customersApi = {
  list: (params?: { page?: number; risk_level?: string; search?: string }) =>
    api.get('/customers', { params }),
  get: (id: string) => api.get(`/customers/${id}`),
}

// ── Incidents ─────────────────────────────────────────────────────────────────
export const incidentsApi = {
  list: (params?: { page?: number; severity?: string; status?: string; sla_breached?: boolean }) =>
    api.get('/incidents', { params }),
  get: (id: string) => api.get(`/incidents/${id}`),
}

// ── Insights ──────────────────────────────────────────────────────────────────
export const insightsApi = {
  list: (params?: { page?: number; severity?: string; insight_type?: string; status?: string }) =>
    api.get('/insights', { params }),
  get: (id: string) => api.get(`/insights/${id}`),
  acknowledge: (id: string) => api.patch(`/insights/${id}/acknowledge`),
}

// ── Anomalies ─────────────────────────────────────────────────────────────────
export const anomaliesApi = {
  list: (params?: { page?: number }) => api.get('/anomalies', { params }),
}

// ── Data Quality ──────────────────────────────────────────────────────────────
export const dataQualityApi = {
  list: (params?: { page?: number }) => api.get('/data-quality', { params }),
  summary: () => api.get('/data-quality/summary'),
}

// ── Review Queue ──────────────────────────────────────────────────────────────
export const reviewApi = {
  list: (params?: { page?: number; status?: string }) => api.get('/review', { params }),
  action: (id: string, action: string, note?: string) =>
    api.post(`/review/${id}/action`, { action, resolution_note: note }),
}

// ── NL Query ──────────────────────────────────────────────────────────────────
export const queryApi = {
  ask: (question: string) => api.post('/query', { question }),
}

// ── Settings ──────────────────────────────────────────────────────────────────
export const settingsApi = {
  system: () => api.get('/settings/system'),
  aiProvider: () => api.get('/settings/ai-provider'),
}

// ── Health ────────────────────────────────────────────────────────────────────
export const healthApi = {
  check: () => api.get('/health'),
}
