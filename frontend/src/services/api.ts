import axios from 'axios'

const rawUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const BASE_URL = rawUrl.replace(/\/+$/, '')

export const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
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
  check: () => axios.get(`${BASE_URL}/health`),
}
