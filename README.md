# Enterprise Intelligence Platform (EIP)

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-v4-38B2AC.svg)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1.svg)](https://www.postgresql.org/)
[![Tableau Ready](https://img.shields.io/badge/Tableau-Ready-E97627.svg)](https://www.tableau.com/)

An end-to-end, AI-powered enterprise analytics and document intelligence platform. The system ingests multi-format unstructured and semi-structured documents (PDF, DOCX, CSV, Excel, TXT), classifies them by domain, extracts structured business facts into a PostgreSQL star-schema data warehouse, generates predictive customer health & churn scores, monitors IT operational incidents and SLA breaches, detects anomalies, and provides a rich executive web interface along with a star-schema model ready for **Tableau BI** visualization.

---

## Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │        Source Data & Documents         │
                      │   (PDF, DOCX, CSV, XLSX, Surveys, TXT) │
                      └───────────────────┬────────────────────┘
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │    Ingestion & Extraction Pipeline     │
                      │  • SHA-256 Hash Deduplication          │
                      │  • Domain Classification Engine        │
                      │  • AI/LLM Entity Extraction (Mock/API) │
                      │  • Human-in-the-Loop Review Queue      │
                      └───────────────────┬────────────────────┘
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │    PostgreSQL Data Warehouse (Star)    │
                      │  • Dimensions: Customer, Product, etc. │
                      │  • Facts: Tickets, Incidents, Feedback │
                      │  • Analytics: Health Scores, Sentiment │
                      └──────────────┬──────────────────┬──────┘
                                     │                  │
                ┌────────────────────┴───┐          ┌───┴───────────────────┐
                │                        │          │                       │
                ▼                        ▼          ▼                       ▼
    ┌──────────────────────┐ ┌────────────────────┐ ┌────────────────────────┐
    │  FastAPI Backend API │ │ Vite/React 19 Web  │ │ Tableau Desktop/Server │
    │  • REST Endpoints    │ │ • Executive KPIs   │ │ • Executive Scorecard  │
    │  • NL Query Engine   │ │ • Customer 360     │ │ • Churn Risk Matrix    │
    │  • JWT RBAC Security │ │ • Incident Monitor │ │ • SLA Breach Heatmap   │
    └──────────────────────┘ └────────────────────┘ └────────────────────────┘
```

---

## Key Features

### 1. Document Ingestion & AI Extraction (`/upload`, `/processing`)
* Supports PDF, DOCX, CSV, XLSX, and TXT files with SHA-256 cryptographic hashing to prevent duplicate uploads.
* Automatic domain classification: `customer_intelligence`, `it_operations`, `document_contract`.
* Extracted structured entities (amounts, dates, customer names, root causes, sentiment) land in staging with provenance tracking.

### 2. Human-in-the-Loop Review Queue (`/review`)
* Low-confidence extractions or conflicting entities are automatically routed to a review queue.
* Analysts can **Approve**, **Reject**, or **Edit** extracted records before they commit to core dimension/fact tables.

### 3. Customer Intelligence & Churn Predictor (`/customers`)
* Complete Customer 360 view for enterprise accounts ($95K – $1.2M ARR).
* Dynamic health scores (0–100) and risk levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
* Churn probability tracking based on ticket frequency, SLA breaches, and NPS sentiment.

### 4. Operations & Incident Management (`/incidents`)
* IT service incident tracking across severity tiers (`P1` to `P4`).
* Root cause categorization, downtime duration, affected user impact, and SLA breach metrics.
* Service reliability scoring (0–100%) for core infrastructure components.

### 5. Automated AI Business Insights & Anomalies (`/insights`, `/anomalies`)
* Executive-ready narratives detailing:
  * **What happened**
  * **Why it matters** (financial impact estimation)
  * **Recommended actions**
* Statistical anomaly detection for metric deviations (query latency spikes, ticket volume surges).

### 6. Natural Language Query Engine (`/query`)
* Ask analytical questions in plain English (e.g., *"Which customers are at high risk of churn?"*, *"Show P1 incidents this month"*).

### 7. Data Quality & Governance (`/data-quality`)
* Automated assessment across completeness, validity, consistency, and uniqueness dimensions.
* Full data lineage and provenance tracking linking dimensional facts back to raw source files.

### 8. Tableau BI Star Schema Ready
* Pre-modeled dimension and fact tables designed for immediate drag-and-drop analysis in Tableau Desktop or Server.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, TanStack Query, Lucide Icons, Recharts, Zustand |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (Async), Asyncpg, Pydantic v2, JWT, Bcrypt |
| **Database** | PostgreSQL 15+ (Relational tables + JSONB semi-structured staging) |
| **Job Queue** | In-memory asynchronous queue (development) / Redis (production) |
| **BI Integration** | Tableau Desktop, Tableau Server, Tableau Cloud (native PostgreSQL driver) |

---

## Repository Structure

```
enterprise-intelligence-platform/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST route handlers (auth, customers, incidents, insights, etc.)
│   │   ├── core/            # Config, security (JWT/Bcrypt), structured logging
│   │   ├── database/        # Async engine & session management
│   │   ├── extraction/      # Entity extraction & AI providers (Mock, Gemini, OpenAI)
│   │   ├── ingestion/       # Multi-format parsers (PDF, CSV, Word, Excel)
│   │   ├── models/          # SQLAlchemy star schema models (User, Document, Core, Analytics)
│   │   ├── schemas/         # Pydantic validation schemas
│   │   └── tasks/           # Background job queue
│   ├── scripts/
│   │   ├── init_db.py       # Table creation & demo user initialization
│   │   └── seed_demo_data.py# Full realistic enterprise data seeder
│   └── requirements.txt     # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # UI layout, Navbar, Sidebar, ProtectedRoute
│   │   ├── pages/           # Dashboard, Customers, Incidents, Upload, Review, etc.
│   │   ├── services/        # Axios API client with automatic JWT bearer handling
│   │   ├── stores/          # Zustand authentication & state management
│   │   └── index.css        # Tailwind CSS v4 design tokens & theme
│   ├── package.json         # Frontend dependencies & scripts
│   └── vite.config.ts       # Vite build & development proxy configuration
├── tableau/                 # Tableau views, calculations, and connection templates
├── start.ps1                # One-click Windows PowerShell quick-start launcher
├── docker-compose.yml       # Docker container orchestration (Postgres, Redis, Backend, Frontend)
└── .env                     # Local configuration & environment variables
```

---

## Quick Start Guide

### Prerequisites
1. **Python**: 3.11 or higher
2. **Node.js**: v18 or higher (with npm)
3. **PostgreSQL**: 15 or higher running locally (or via Docker)

---

### Step 1: Environment Configuration
Copy `.env.example` to `.env` (or configure `.env` in the root folder):

```ini
# Application
APP_ENV=development
APP_DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production-min-32chars
JWT_SECRET=dev-jwt-secret-change-in-production-min-32chars

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/tableau
DATABASE_SYNC_URL=postgresql://postgres:your_password@localhost:5432/tableau
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=tableau

# AI Provider (mock = no key needed, gemini = set GEMINI_API_KEY)
AI_PROVIDER=mock
GEMINI_API_KEY=
```

---

### Step 2: Initialize & Seed the Database
From the `backend` folder:

```powershell
cd backend
python -m pip install -r requirements.txt

# Create all tables and seed rich enterprise demo data
python scripts/seed_demo_data.py --reset
```

> **Note**: `seed_demo_data.py` populates:
> * 3 Demo Users (Admin, Analyst, Viewer)
> * 10 Enterprise Customer Accounts (Health Scores, Risk Levels, Contract Values)
> * 5 Products & 5 Infrastructure Services
> * 6 Ingested Documents & Processing Jobs
> * 8 Support Tickets with SLA & Sentiment Scores
> * 5 Operational Incident Postmortems (P1 to P3)
> * 12 Months of Sentiment Trend History
> * 4 Strategic AI Insights & 4 Detected Anomalies
> * 4 Data Quality Reports & 4 Human-in-the-Loop Review Items

---

### Step 3: Run the Application

#### Option A: Quick-Start Script (Windows)
From the project root:
```powershell
.\start.ps1
```

#### Option B: Manual Start (Two Terminals)

**Terminal 1 — Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```powershell
cd frontend
npm install
npm run dev
```

---

### Step 4: Access the Platform

* **Web Application**: [http://localhost:5173](http://localhost:5173)
* **Interactive API Docs (Swagger)**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
* **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

#### Default Demo Credentials
| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@eip.local` | `Admin@12345` | Full system access, review queue actions, document uploads |
| **Analyst** | `analyst@eip.local` | `Analyst@12345` | Analytics, review queue approve/reject, exports |
| **Viewer** | `viewer@eip.local` | `Viewer@12345` | Read-only dashboards and reports |

---

## Connecting Tableau to the Platform

Tableau connects directly to the PostgreSQL database for rich data visualization.

### Connection Parameters
* **Connector**: PostgreSQL
* **Server**: `localhost` *(or `127.0.0.1`)*
* **Port**: `5432`
* **Database**: `tableau` *(or your configured `POSTGRES_DB`)*
* **Username**: `postgres`
* **Password**: `your_password`

### Recommended Tableau Data Model (Star Schema)
Drag and link the following tables in Tableau's Data Source tab:

* **Fact Tables**:
  * `fact_ticket`: Ticket counts, resolution hours, response hours, sentiment score, SLA breach flags.
  * `fact_incident`: Incident counts, downtime minutes, affected users, financial impact.
  * `fact_feedback`: CSAT ratings (1–5), NPS scores (0–10), sentiment score.
  * `fact_contract`: Contract value (ARR), renewal dates.
* **Dimension Tables**:
  * `dim_customer`: Customer name, company, industry, region, tier, health score, churn risk score, risk level.
  * `dim_service`: Service name, service type, owner team, reliability score.
  * `dim_product`: Product name, category.
  * `dim_employee`: Support & engineering assignees, department, location.
* **Pre-Computed Analytics Tables**:
  * `analytics_sentiment`: 12-month historical breakdown (`positive_pct`, `neutral_pct`, `negative_pct`).
  * `analytics_customer_health`: Health trends and contributing churn factors.
  * `analytics_data_quality`: Dataset completeness, validity, and uniqueness metrics.

---

## Core API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT access token |
| `GET` | `/api/v1/analytics/overview` | Executive KPI overview (Customers, Tickets, Incidents, Insights) |
| `GET` | `/api/v1/analytics/sentiment-trend` | 12-month aggregated customer sentiment trends |
| `GET` | `/api/v1/customers` | Paginated customer list with health & risk filters |
| `GET` | `/api/v1/incidents` | Operational incident log with severity & SLA filters |
| `POST`| `/api/v1/documents/upload` | Multipart file upload with deduplication & parsing |
| `GET` | `/api/v1/jobs` | Background pipeline job statuses |
| `GET` | `/api/v1/insights` | Strategic AI-generated insights and recommendations |
| `GET` | `/api/v1/anomalies` | Detected statistical metric anomalies |
| `GET` | `/api/v1/review` | Human-in-the-loop review queue items |
| `POST`| `/api/v1/review/{id}/action` | Approve, reject, or edit an extraction record |
| `POST`| `/api/v1/query` | Natural language analytical query processing |
| `GET` | `/health` | System health check (DB connectivity, AI provider, version) |

---

## License
MIT License. Created for enterprise intelligence, analytics, and business intelligence reporting.
