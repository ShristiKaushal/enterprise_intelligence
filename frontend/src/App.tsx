import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import Layout from '@/components/Layout'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import DataSourcesPage from '@/pages/DataSourcesPage'
import UploadPage from '@/pages/UploadPage'
import ProcessingPage from '@/pages/ProcessingPage'
import CustomersPage from '@/pages/CustomersPage'
import IncidentsPage from '@/pages/IncidentsPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import InsightsPage from '@/pages/InsightsPage'
import InsightDetailPage from '@/pages/InsightDetailPage'
import AnomaliesPage from '@/pages/AnomaliesPage'
import DataQualityPage from '@/pages/DataQualityPage'
import QueryPage from '@/pages/QueryPage'
import ReviewPage from '@/pages/ReviewPage'
import SettingsPage from '@/pages/SettingsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#111827',
              color: '#f1f5f9',
              border: '1px solid #1e2d47',
              borderRadius: '10px',
              fontSize: '13.5px',
            },
          }}
        />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="data-sources" element={<DataSourcesPage />} />
            <Route path="upload" element={<UploadPage />} />
            <Route path="processing" element={<ProcessingPage />} />
            <Route path="customers" element={<CustomersPage />} />
            <Route path="incidents" element={<IncidentsPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="insights" element={<InsightsPage />} />
            <Route path="insights/:id" element={<InsightDetailPage />} />
            <Route path="anomalies" element={<AnomaliesPage />} />
            <Route path="data-quality" element={<DataQualityPage />} />
            <Route path="query" element={<QueryPage />} />
            <Route path="review" element={<ReviewPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
