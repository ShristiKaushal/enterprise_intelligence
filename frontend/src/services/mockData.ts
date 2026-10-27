/**
 * Mock & Demo Fallback Dataset for Enterprise Intelligence Platform
 * Provides seamless realistic enterprise data when the backend is unreachable
 * (e.g. on Vercel deployment without live backend connection, mixed content, or offline demo mode).
 */

export const MOCK_USER = {
  id: '00000000-0000-0000-0000-000000000001',
  email: 'admin@eip.local',
  username: 'admin',
  full_name: 'Platform Admin (Demo)',
  role: 'admin' as const,
  is_active: true,
}

export const MOCK_OVERVIEW = {
  total_customers: 10,
  total_tickets: 8,
  open_tickets: 5,
  total_incidents: 5,
  open_incidents: 3,
  sla_breaches: 2,
  critical_insights: 4,
  high_risk_customers: 3,
}

export const MOCK_SENTIMENT_TREND = [
  { period: '2025-11', positive_pct: 68.5, neutral_pct: 21.0, negative_pct: 10.5, total_records: 120 },
  { period: '2025-12', positive_pct: 65.0, neutral_pct: 22.0, negative_pct: 13.0, total_records: 135 },
  { period: '2026-01', positive_pct: 72.0, neutral_pct: 18.0, negative_pct: 10.0, total_records: 140 },
  { period: '2026-02', positive_pct: 69.0, neutral_pct: 20.0, negative_pct: 11.0, total_records: 128 },
  { period: '2026-03', positive_pct: 74.5, neutral_pct: 16.5, negative_pct: 9.0, total_records: 150 },
  { period: '2026-04', positive_pct: 70.0, neutral_pct: 19.0, negative_pct: 11.0, total_records: 142 },
  { period: '2026-05', positive_pct: 66.0, neutral_pct: 21.0, negative_pct: 13.0, total_records: 160 },
  { period: '2026-06', positive_pct: 63.5, neutral_pct: 22.5, negative_pct: 14.0, total_records: 155 },
  { period: '2026-07', positive_pct: 67.0, neutral_pct: 20.0, negative_pct: 13.0, total_records: 165 },
  { period: '2026-08', positive_pct: 71.0, neutral_pct: 19.0, negative_pct: 10.0, total_records: 170 },
  { period: '2026-09', positive_pct: 73.0, neutral_pct: 18.0, negative_pct: 9.0, total_records: 180 },
  { period: '2026-10', positive_pct: 76.2, neutral_pct: 15.8, negative_pct: 8.0, total_records: 195 },
]

export const MOCK_HEALTH_DISTRIBUTION = [
  { risk_level: 'LOW', count: 5 },
  { risk_level: 'MEDIUM', count: 2 },
  { risk_level: 'HIGH', count: 2 },
  { risk_level: 'CRITICAL', count: 1 },
]

export const MOCK_INSIGHTS = {
  total: 4,
  page: 1,
  page_size: 20,
  items: [
    {
      id: 'ins-001',
      insight_type: 'churn_risk',
      severity: 'CRITICAL',
      title: 'High churn probability for RetailGiant Corp',
      description: 'Combination of 3 unresolved P1 incidents and negative sentiment trend in quarterly NPS reviews indicates 82% churn probability prior to contract renewal.',
      confidence: 0.88,
      status: 'active',
      recommended_actions: [
        'Schedule executive sponsor check-in',
        'Assign dedicated technical account manager',
        'Issue SLA breach service credit',
      ],
      impact_metric: 'ARR at risk: $420,000',
      created_at: '2026-10-25T10:00:00Z',
    },
    {
      id: 'ins-002',
      insight_type: 'sla_breach',
      severity: 'HIGH',
      title: 'Database connection pool exhaustion risk in EU cluster',
      description: 'P99 latency surged to 4.8s during peak hours. Projected to cause breach of 99.9% uptime SLA if unaddressed.',
      confidence: 0.92,
      status: 'active',
      recommended_actions: [
        'Increase connection pool max overflow to 40',
        'Implement query caching for hot ledger reads',
      ],
      impact_metric: 'Affected users: ~14,200',
      created_at: '2026-10-26T14:30:00Z',
    },
    {
      id: 'ins-003',
      insight_type: 'anomaly',
      severity: 'HIGH',
      title: 'Hourly support ticket volume spike (+300%)',
      description: 'Spike correlated with Client SDK v2.4 rollout in Central region causing authentication timeouts.',
      confidence: 0.85,
      status: 'active',
      recommended_actions: [
        'Push hotfix release v2.4.1',
        'Publish status page incident advisory',
      ],
      impact_metric: 'Tickets pending: 48',
      created_at: '2026-10-27T08:15:00Z',
    },
    {
      id: 'ins-004',
      insight_type: 'quality_alert',
      severity: 'MEDIUM',
      title: 'Contract penalty clause extraction ambiguity',
      description: 'Ambiguity in draft contract penalty clause for Acme Logistics requires manual legal analyst review.',
      confidence: 0.76,
      status: 'active',
      recommended_actions: ['Review queue confirmation required'],
      impact_metric: 'Contract value: $180,000',
      created_at: '2026-10-27T11:45:00Z',
    },
  ],
}

export const MOCK_CUSTOMERS = {
  total: 10,
  page: 1,
  page_size: 20,
  items: [
    { id: 'c-01', name: 'RetailGiant Corp', region: 'North America', tier: 'Enterprise', health_score: 38, risk_level: 'CRITICAL', churn_probability: 0.82, arr: 420000, industry: 'Retail' },
    { id: 'c-02', name: 'FinTech Global Inc', region: 'Europe', tier: 'Enterprise', health_score: 52, risk_level: 'HIGH', churn_probability: 0.65, arr: 350000, industry: 'Financial Services' },
    { id: 'c-03', name: 'Velocity Telecom', region: 'Latin America', tier: 'Enterprise', health_score: 44, risk_level: 'HIGH', churn_probability: 0.71, arr: 480000, industry: 'Telecommunications' },
    { id: 'c-04', name: 'Apex Logistics LLC', region: 'North America', tier: 'Mid-Market', health_score: 61, risk_level: 'MEDIUM', churn_probability: 0.38, arr: 180000, industry: 'Logistics' },
    { id: 'c-05', name: 'Horizon Retail EU', region: 'Europe', tier: 'Growth', health_score: 73, risk_level: 'MEDIUM', churn_probability: 0.28, arr: 125000, industry: 'Retail' },
    { id: 'c-06', name: 'HealthSync Systems', region: 'North America', tier: 'Enterprise', health_score: 89, risk_level: 'LOW', churn_probability: 0.12, arr: 540000, industry: 'Healthcare' },
    { id: 'c-07', name: 'CloudScale Technologies', region: 'Asia-Pacific', tier: 'Growth', health_score: 94, risk_level: 'LOW', churn_probability: 0.08, arr: 95000, industry: 'Technology' },
    { id: 'c-08', name: 'Sterling Bank PLC', region: 'Europe', tier: 'Enterprise', health_score: 88, risk_level: 'LOW', churn_probability: 0.14, arr: 620000, industry: 'Banking' },
    { id: 'c-09', name: 'Beacon Insurance', region: 'North America', tier: 'Enterprise', health_score: 82, risk_level: 'LOW', churn_probability: 0.15, arr: 310000, industry: 'Insurance' },
    { id: 'c-10', name: 'Nordic Media Group', region: 'Europe', tier: 'Mid-Market', health_score: 77, risk_level: 'LOW', churn_probability: 0.21, arr: 165000, industry: 'Media' },
  ],
}

export const MOCK_INCIDENTS = {
  total: 5,
  page: 1,
  page_size: 20,
  items: [
    { id: 'inc-01', incident_number: 'INC-2026-001', title: 'Database Connection Pool Starvation', severity: 'critical', category: 'Database', status: 'resolved', sla_breached: false, downtime_minutes: 18, created_at: '2026-10-24T09:12:00Z' },
    { id: 'inc-02', incident_number: 'INC-2026-002', title: 'EU API Gateway Authentication Timeouts', severity: 'high', category: 'Network', status: 'open', sla_breached: true, downtime_minutes: 45, created_at: '2026-10-25T14:30:00Z' },
    { id: 'inc-03', incident_number: 'INC-2026-003', title: 'Batch Ingestion Worker Memory Exception', severity: 'high', category: 'Ingestion', status: 'resolved', sla_breached: false, downtime_minutes: 12, created_at: '2026-10-26T03:00:00Z' },
    { id: 'inc-04', incident_number: 'INC-2026-004', title: 'Storage Volume IOPS Throttling', severity: 'medium', category: 'Storage', status: 'open', sla_breached: false, downtime_minutes: 0, created_at: '2026-10-26T19:45:00Z' },
    { id: 'inc-05', incident_number: 'INC-2026-005', title: 'Customer Webhook Delivery Retries Stalled', severity: 'low', category: 'Integration', status: 'open', sla_breached: true, downtime_minutes: 30, created_at: '2026-10-27T07:15:00Z' },
  ],
}

export const MOCK_ANOMALIES = {
  total: 4,
  page: 1,
  page_size: 20,
  items: [
    { id: 'anom-01', metric_name: 'Database Query Latency (p99)', observed_value: 4820.0, expected_value: 450.0, deviation_pct: 971.1, detection_method: 'isolation_forest', severity: 'CRITICAL', is_resolved: false, possible_causes: ['Unindexed ledger queries', 'Connection pool starvation'], detected_at: '2026-10-27T08:00:00Z' },
    { id: 'anom-02', metric_name: 'Hourly Support Ticket Volume', observed_value: 48.0, expected_value: 12.0, deviation_pct: 300.0, detection_method: 'zscore', severity: 'HIGH', is_resolved: false, possible_causes: ['EU cluster authentication outage', 'Client SDK version mismatch'], detected_at: '2026-10-27T05:00:00Z' },
    { id: 'anom-03', metric_name: 'Document Ingestion Failure Rate', observed_value: 14.8, expected_value: 1.2, deviation_pct: 1133.3, detection_method: 'rolling_average', severity: 'HIGH', is_resolved: true, possible_causes: ['Corrupted TIFF upload batch', 'Worker memory constraint'], detected_at: '2026-10-26T22:00:00Z' },
    { id: 'anom-04', metric_name: 'Average Customer Sentiment Score', observed_value: -0.42, expected_value: 0.65, deviation_pct: -164.6, detection_method: 'zscore', severity: 'MEDIUM', is_resolved: false, possible_causes: ['Recent downtime impact on Q3 NPS scores'], detected_at: '2026-10-26T18:00:00Z' },
  ],
}

export const MOCK_DATA_QUALITY_SUMMARY = {
  avg_overall_score: 92.8,
  avg_completeness_score: 94.7,
  avg_validity_score: 96.5,
  avg_consistency_score: 90.1,
  avg_uniqueness_score: 90.1,
  avg_timeliness_score: 93.4,
  total_records_assessed: 21060,
  total_invalid_records: 99,
  total_duplicate_records: 26,
}

export const MOCK_DATA_QUALITY_REPORTS = [
  { id: 'dq-01', dataset_name: 'Customer Support Tickets Export', overall_score: 94.2, completeness_score: 96.0, validity_score: 98.0, consistency_score: 92.5, uniqueness_score: 90.5, total_records: 1240, invalid_records: 18, duplicate_records: 6, report_date: '2026-10-26T12:00:00Z' },
  { id: 'dq-02', dataset_name: 'Contract Legal Terms Extraction', overall_score: 87.5, completeness_score: 89.0, validity_score: 94.0, consistency_score: 82.0, uniqueness_score: 85.0, total_records: 480, invalid_records: 24, duplicate_records: 12, report_date: '2026-10-26T12:00:00Z' },
  { id: 'dq-03', dataset_name: 'Telemetry & Incident Logs', overall_score: 98.6, completeness_score: 99.2, validity_score: 99.0, consistency_score: 97.8, uniqueness_score: 98.5, total_records: 18450, invalid_records: 42, duplicate_records: 0, report_date: '2026-10-26T12:00:00Z' },
  { id: 'dq-04', dataset_name: 'Customer Feedback & NPS Surveys', overall_score: 91.0, completeness_score: 94.5, validity_score: 95.0, consistency_score: 88.0, uniqueness_score: 86.5, total_records: 890, invalid_records: 15, duplicate_records: 8, report_date: '2026-10-26T12:00:00Z' },
]

export const MOCK_REVIEW_QUEUE = {
  total: 4,
  page: 1,
  page_size: 20,
  items: [
    { id: 'rq-01', item_type: 'low_confidence_extraction', title: 'Contract penalty clause value extraction ambiguity', description: "Extracted monetary penalty clause from 'retailgiant_expansion_contract_draft.pdf' has 65% confidence.", confidence: 0.65, status: 'pending', priority: 'high', created_at: '2026-10-26T10:00:00Z' },
    { id: 'rq-02', item_type: 'entity_resolution', title: "Customer canonical mapping: 'RetailGiant DE' vs 'RetailGiant Inc'", description: 'Fuzzy name match score 0.72 requires analyst confirmation for master customer ID.', confidence: 0.72, status: 'pending', priority: 'medium', created_at: '2026-10-26T11:30:00Z' },
    { id: 'rq-03', item_type: 'data_quality', title: 'Missing required field: SLA resolution time in Ticket #10486', description: 'Ticket imported without resolution timestamp; auto-fill suggested from incident #INC-2026-003.', confidence: 0.81, status: 'pending', priority: 'low', created_at: '2026-10-26T14:15:00Z' },
    { id: 'rq-04', item_type: 'low_confidence_extraction', title: "Product classification for 'Custom Enterprise API Connector'", description: "Model suggested 'Enterprise Analytics Suite' with 58% confidence.", confidence: 0.58, status: 'pending', priority: 'medium', created_at: '2026-10-27T09:00:00Z' },
  ],
}

export const MOCK_DOCUMENTS = {
  total: 6,
  page: 1,
  page_size: 20,
  items: [
    { id: 'doc-01', filename: 'retailgiant_expansion_contract_2026.pdf', domain: 'contracts', file_size_bytes: 2450000, status: 'processed', created_at: '2026-10-24T10:00:00Z' },
    { id: 'doc-02', filename: 'q3_customer_support_transcripts.csv', domain: 'tickets', file_size_bytes: 8500000, status: 'processed', created_at: '2026-10-25T11:20:00Z' },
    { id: 'doc-03', filename: 'october_telemetry_incidents.json', domain: 'incidents', file_size_bytes: 1200000, status: 'processed', created_at: '2026-10-26T08:15:00Z' },
    { id: 'doc-04', filename: 'annual_customer_nps_survey.xlsx', domain: 'surveys', file_size_bytes: 3400000, status: 'processed', created_at: '2026-10-26T16:45:00Z' },
    { id: 'doc-05', filename: 'eu_region_service_health_log.txt', domain: 'operations', file_size_bytes: 980000, status: 'processed', created_at: '2026-10-27T04:30:00Z' },
    { id: 'doc-06', filename: 'fintech_global_service_agreement.docx', domain: 'contracts', file_size_bytes: 1800000, status: 'processed', created_at: '2026-10-27T08:00:00Z' },
  ],
}

export const MOCK_JOBS = {
  total: 6,
  page: 1,
  page_size: 20,
  items: [
    { id: 'job-01', job_type: 'full_pipeline', status: 'completed', progress: 100, created_at: '2026-10-24T10:05:00Z', completed_at: '2026-10-24T10:06:12Z' },
    { id: 'job-02', job_type: 'entity_resolution', status: 'completed', progress: 100, created_at: '2026-10-25T11:25:00Z', completed_at: '2026-10-25T11:26:05Z' },
    { id: 'job-03', job_type: 'sentiment_analysis', status: 'completed', progress: 100, created_at: '2026-10-26T08:20:00Z', completed_at: '2026-10-26T08:21:40Z' },
    { id: 'job-04', job_type: 'anomaly_detection', status: 'completed', progress: 100, created_at: '2026-10-26T16:50:00Z', completed_at: '2026-10-26T16:50:55Z' },
    { id: 'job-05', job_type: 'data_quality_audit', status: 'completed', progress: 100, created_at: '2026-10-27T04:35:00Z', completed_at: '2026-10-27T04:36:10Z' },
    { id: 'job-06', job_type: 'full_pipeline', status: 'completed', progress: 100, created_at: '2026-10-27T08:05:00Z', completed_at: '2026-10-27T08:06:22Z' },
  ],
}

export const MOCK_SETTINGS_SYSTEM = {
  app_name: 'Enterprise Intelligence Platform',
  ai_provider: 'mock',
  max_file_size_mb: 100,
  allowed_extensions: ['pdf', 'docx', 'txt', 'csv', 'xlsx', 'xls', 'json'],
  job_backend: 'memory',
  enable_ml_models: true,
  cors_origins: ['https://*.vercel.app', 'http://localhost:5173'],
}

export const MOCK_SETTINGS_AI = {
  provider: 'Mock AI Engine (Offline / Demo Mode)',
  model_version: 'v1.0-embedded',
  available: true,
}

export const MOCK_HEALTH = {
  status: 'ok',
  database: 'connected (demo mode)',
  env: 'demo',
  version: '1.0.0',
}
