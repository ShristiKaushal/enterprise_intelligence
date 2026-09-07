"""
Comprehensive Database Seeder for Enterprise Intelligence Platform.
Seeds realistic enterprise data across all tables to test every feature.

Usage:
    cd backend
    python scripts/seed_demo_data.py [--reset]
"""
from __future__ import annotations

import asyncio
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import delete, select
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.security import hash_password
from app.database.session import AsyncSessionLocal, create_all_tables

# Import all models
from app.models.user import User
from app.models.document import RawDocument, RawRecord, ProcessingJob, ExtractedEntity
from app.models.core import (
    DimCustomer, DimProduct, DimService, DimEmployee, DimLocation,
    FactTicket, FactIncident, FactFeedback, FactContract,
    ReviewQueueItem, EntityResolutionLog
)
from app.models.analytics import (
    CustomerHealthScore, ServiceHealthScore, SentimentTrend,
    AnomalyRecord, BusinessInsight, DataQualityReport
)

configure_logging()
logger = get_logger("seed_demo_data")


async def seed_all(reset: bool = False) -> None:
    print("\n" + "=" * 60)
    print("  Enterprise Intelligence Platform — Database Seeder")
    print("=" * 60)

    # 1. Ensure all tables are created
    print("\n[1/10] Verifying database schema & tables...")
    await create_all_tables()
    print("       Tables ready.")

    async with AsyncSessionLocal() as session:
        if reset:
            print("\n[RESET] Clearing existing data...")
            from sqlalchemy import text
            await session.execute(text(
                "TRUNCATE TABLE review_queue, analytics_anomalies, analytics_insights, "
                "analytics_data_quality, analytics_sentiment, analytics_customer_health, "
                "analytics_service_health, fact_feedback, fact_ticket, fact_incident, "
                "fact_contract, entity_resolution_log, stg_extracted_entities, "
                "processing_jobs, raw_records, raw_documents, dim_customer, "
                "dim_product, dim_service, dim_employee, dim_location, users CASCADE;"
            ))
            await session.commit()
            print("       All tables cleared.")

        # 2. Seed Users
        print("\n[2/10] Seeding demo users...")
        users_data = [
            {"email": "admin@eip.local", "username": "admin", "full_name": "Platform Admin", "password": "Admin@12345", "role": "admin"},
            {"email": "analyst@eip.local", "username": "analyst", "full_name": "Data Analyst", "password": "Analyst@12345", "role": "analyst"},
            {"email": "viewer@eip.local", "username": "viewer", "full_name": "Dashboard Viewer", "password": "Viewer@12345", "role": "viewer"},
        ]
        created_users = {}
        for u in users_data:
            res = await session.execute(select(User).where(User.email == u["email"]))
            user = res.scalar_one_or_none()
            if not user:
                user = User(
                    email=u["email"],
                    username=u["username"],
                    full_name=u["full_name"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"],
                    is_active=True,
                    is_verified=True,
                )
                session.add(user)
                await session.flush()
            created_users[u["role"]] = user
        print(f"       {len(created_users)} users ready.")

        # 3. Seed Dimensions
        print("\n[3/10] Seeding core dimensions (Customers, Products, Services, Locations)...")
        now = datetime.now(timezone.utc)

        # Customers
        customers_seed = [
            {"canonical_id": "CUST_001", "name": "Acme Global Enterprise", "company": "Acme Corp", "industry": "Financial Services", "region": "North America", "country": "United States", "tier": "enterprise", "contract_value": 750000.0, "health_score": 42.5, "churn_risk_score": 0.78, "risk_level": "CRITICAL"},
            {"canonical_id": "CUST_002", "name": "TechCorp Solutions Ltd", "company": "TechCorp", "industry": "Software & Technology", "region": "North America", "country": "United States", "tier": "enterprise", "contract_value": 520000.0, "health_score": 88.0, "churn_risk_score": 0.12, "risk_level": "LOW"},
            {"canonical_id": "CUST_003", "name": "FinTech Horizon Bank", "company": "FinTech Horizon", "industry": "Banking", "region": "Europe", "country": "United Kingdom", "tier": "enterprise", "contract_value": 980000.0, "health_score": 58.0, "churn_risk_score": 0.61, "risk_level": "HIGH"},
            {"canonical_id": "CUST_004", "name": "CloudScale Infrastructure", "company": "CloudScale", "industry": "Cloud Computing", "region": "North America", "country": "Canada", "tier": "mid-market", "contract_value": 240000.0, "health_score": 92.5, "churn_risk_score": 0.08, "risk_level": "LOW"},
            {"canonical_id": "CUST_005", "name": "RetailGiant Omnichannel", "company": "RetailGiant Inc", "industry": "Retail & E-commerce", "region": "Europe", "country": "Germany", "tier": "enterprise", "contract_value": 640000.0, "health_score": 51.0, "churn_risk_score": 0.69, "risk_level": "HIGH"},
            {"canonical_id": "CUST_006", "name": "BioHealth Pharmaceuticals", "company": "BioHealth Group", "industry": "Healthcare", "region": "North America", "country": "United States", "tier": "enterprise", "contract_value": 810000.0, "health_score": 79.0, "churn_risk_score": 0.22, "risk_level": "LOW"},
            {"canonical_id": "CUST_007", "name": "MediaStream Entertainment", "company": "MediaStream", "industry": "Digital Media", "region": "Asia-Pacific", "country": "Singapore", "tier": "mid-market", "contract_value": 180000.0, "health_score": 67.0, "churn_risk_score": 0.41, "risk_level": "MEDIUM"},
            {"canonical_id": "CUST_008", "name": "Nexus Global Logistics", "company": "Nexus Logistics", "industry": "Supply Chain", "region": "Europe", "country": "Netherlands", "tier": "enterprise", "contract_value": 430000.0, "health_score": 73.0, "churn_risk_score": 0.28, "risk_level": "MEDIUM"},
            {"canonical_id": "CUST_009", "name": "CyberShield Defense", "company": "CyberShield Inc", "industry": "Cybersecurity", "region": "North America", "country": "United States", "tier": "mid-market", "contract_value": 310000.0, "health_score": 85.0, "churn_risk_score": 0.15, "risk_level": "LOW"},
            {"canonical_id": "CUST_010", "name": "Quantum Dynamics AI", "company": "Quantum AI", "industry": "Artificial Intelligence", "region": "Asia-Pacific", "country": "Japan", "tier": "smb", "contract_value": 95000.0, "health_score": 62.0, "churn_risk_score": 0.45, "risk_level": "MEDIUM"},
        ]
        customers = []
        for c in customers_seed:
            res = await session.execute(select(DimCustomer).where(DimCustomer.canonical_id == c["canonical_id"]))
            cust = res.scalar_one_or_none()
            if not cust:
                cust = DimCustomer(**c, since_date=date(2023, 1, 15), is_active=True)
                session.add(cust)
                await session.flush()
            customers.append(cust)
        print(f"       {len(customers)} customers ready.")

        # Products
        products_seed = [
            {"canonical_id": "PROD_001", "name": "Enterprise Analytics Suite", "category": "Analytics", "subcategory": "BI Platform", "description": "Unified business intelligence and dashboarding engine"},
            {"canonical_id": "PROD_002", "name": "Data Ingestion Pipeline Pro", "category": "Data Engineering", "subcategory": "ETL", "description": "High-throughput multi-format document parser and pipeline"},
            {"canonical_id": "PROD_003", "name": "Identity & Access Shield", "category": "Security", "subcategory": "IAM", "description": "RBAC and SSO federated authentication server"},
            {"canonical_id": "PROD_004", "name": "AI Insight Generation Engine", "category": "AI / ML", "subcategory": "LLM Insights", "description": "Automated anomaly and narrative intelligence module"},
            {"canonical_id": "PROD_005", "name": "Customer 360 Churn Predictor", "category": "Machine Learning", "subcategory": "Predictive Models", "description": "Real-time health score and churn risk evaluator"},
        ]
        products = []
        for p in products_seed:
            res = await session.execute(select(DimProduct).where(DimProduct.canonical_id == p["canonical_id"]))
            prod = res.scalar_one_or_none()
            if not prod:
                prod = DimProduct(**p, is_active=True)
                session.add(prod)
                await session.flush()
            products.append(prod)

        # Services
        services_seed = [
            {"canonical_id": "SRV_001", "name": "Cloud Database Cluster (PostgreSQL)", "service_type": "database", "owner_team": "Data Platform Team", "sla_response_hours": 0.5, "sla_resolution_hours": 2.0, "is_critical": True, "reliability_score": 94.2},
            {"canonical_id": "SRV_002", "name": "Authentication & JWT API Gateway", "service_type": "application", "owner_team": "Security Eng", "sla_response_hours": 0.25, "sla_resolution_hours": 1.0, "is_critical": True, "reliability_score": 99.8},
            {"canonical_id": "SRV_003", "name": "Document Ingestion & OCR Service", "service_type": "application", "owner_team": "AI & Processing", "sla_response_hours": 1.0, "sla_resolution_hours": 4.0, "is_critical": False, "reliability_score": 91.5},
            {"canonical_id": "SRV_004", "name": "Real-Time Streaming Event Bus", "service_type": "infrastructure", "owner_team": "Core Infra", "sla_response_hours": 0.5, "sla_resolution_hours": 2.0, "is_critical": True, "reliability_score": 97.4},
            {"canonical_id": "SRV_005", "name": "Automated Reporting Engine", "service_type": "support", "owner_team": "BI Platform", "sla_response_hours": 2.0, "sla_resolution_hours": 8.0, "is_critical": False, "reliability_score": 98.6},
        ]
        services = []
        for s in services_seed:
            res = await session.execute(select(DimService).where(DimService.canonical_id == s["canonical_id"]))
            srv = res.scalar_one_or_none()
            if not srv:
                srv = DimService(**s, is_active=True)
                session.add(srv)
                await session.flush()
            services.append(srv)

        # Employees
        employees_seed = [
            {"canonical_id": "EMP_001", "name": "Sarah Jenkins", "email": "sarah.jenkins@eip.local", "department": "Technical Support", "role": "Senior Escalations Engineer", "location": "New York"},
            {"canonical_id": "EMP_002", "name": "David Chen", "email": "david.chen@eip.local", "department": "DevOps / SRE", "role": "Lead Site Reliability Engineer", "location": "San Francisco"},
            {"canonical_id": "EMP_003", "name": "Elena Rostova", "email": "elena.r@eip.local", "department": "Data Engineering", "role": "Principal Data Architect", "location": "Frankfurt"},
            {"canonical_id": "EMP_004", "name": "Marcus Vance", "email": "marcus.v@eip.local", "department": "Customer Success", "role": "Enterprise Account Director", "location": "London"},
        ]
        employees = []
        for e in employees_seed:
            res = await session.execute(select(DimEmployee).where(DimEmployee.canonical_id == e["canonical_id"]))
            emp = res.scalar_one_or_none()
            if not emp:
                emp = DimEmployee(**e, is_active=True)
                session.add(emp)
                await session.flush()
            employees.append(emp)

        # Locations
        locations_seed = [
            {"canonical_id": "LOC_US_EAST", "name": "US-East (N. Virginia)", "city": "Ashburn", "state": "VA", "country": "United States", "region": "North America"},
            {"canonical_id": "LOC_EU_CENTRAL", "name": "EU-Central (Frankfurt)", "city": "Frankfurt", "state": "Hesse", "country": "Germany", "region": "Europe"},
            {"canonical_id": "LOC_AP_SOUTHEAST", "name": "AP-Southeast (Singapore)", "city": "Singapore", "state": "Singapore", "country": "Singapore", "region": "Asia-Pacific"},
        ]
        locations = []
        for l in locations_seed:
            res = await session.execute(select(DimLocation).where(DimLocation.canonical_id == l["canonical_id"]))
            loc = res.scalar_one_or_none()
            if not loc:
                loc = DimLocation(**l)
                session.add(loc)
                await session.flush()
            locations.append(loc)

        # 4. Seed Raw Documents & Processing Jobs
        print("\n[4/10] Seeding sample documents & ingestion pipeline jobs...")
        docs_seed = [
            {"filename": "acme_q3_service_review.pdf", "original_filename": "acme_q3_service_review.pdf", "file_type": "pdf", "file_size_bytes": 2450000, "file_hash": "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0", "storage_path": "uploads/acme_q3_service_review.pdf", "domain": "customer_intelligence", "status": "completed", "page_count": 14, "word_count": 4200, "extraction_confidence": 0.94},
            {"filename": "eu_db_incident_postmortem_aug2026.docx", "original_filename": "eu_db_incident_postmortem_aug2026.docx", "file_type": "docx", "file_size_bytes": 840000, "file_hash": "b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef01", "storage_path": "uploads/eu_db_incident_postmortem_aug2026.docx", "domain": "it_operations", "status": "completed", "page_count": 6, "word_count": 1850, "extraction_confidence": 0.89},
            {"filename": "fintech_horizon_master_sla_agreement.pdf", "original_filename": "fintech_horizon_master_sla_agreement.pdf", "file_type": "pdf", "file_size_bytes": 3890000, "file_hash": "c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef012", "storage_path": "uploads/fintech_horizon_master_sla_agreement.pdf", "domain": "document_contract", "status": "completed", "page_count": 32, "word_count": 11500, "extraction_confidence": 0.96},
            {"filename": "august_2026_customer_nps_survey_raw.csv", "original_filename": "august_2026_customer_nps_survey_raw.csv", "file_type": "csv", "file_size_bytes": 512000, "file_hash": "d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0123", "storage_path": "uploads/august_2026_customer_nps_survey_raw.csv", "domain": "customer_intelligence", "status": "completed", "page_count": 1, "word_count": 8900, "extraction_confidence": 0.98},
            {"filename": "support_tickets_dump_week36.xlsx", "original_filename": "support_tickets_dump_week36.xlsx", "file_type": "xlsx", "file_size_bytes": 1120000, "file_hash": "e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef01234", "storage_path": "uploads/support_tickets_dump_week36.xlsx", "domain": "it_operations", "status": "completed", "page_count": 3, "word_count": 6400, "extraction_confidence": 0.92},
            {"filename": "retailgiant_expansion_contract_draft.pdf", "original_filename": "retailgiant_expansion_contract_draft.pdf", "file_type": "pdf", "file_size_bytes": 1780000, "file_hash": "f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef012345", "storage_path": "uploads/retailgiant_expansion_contract_draft.pdf", "domain": "document_contract", "status": "review_required", "page_count": 18, "word_count": 5200, "extraction_confidence": 0.65},
        ]
        documents = []
        for d in docs_seed:
            res = await session.execute(select(RawDocument).where(RawDocument.file_hash == d["file_hash"]))
            doc = res.scalar_one_or_none()
            if not doc:
                doc = RawDocument(**d, uploaded_by_id=created_users["admin"].id)
                session.add(doc)
                await session.flush()
                # Create processing job for it
                job = ProcessingJob(
                    document_id=doc.id,
                    job_type="full_pipeline",
                    status="completed" if doc.status == "completed" else "review_required",
                    progress=100 if doc.status == "completed" else 75,
                    current_step="finished" if doc.status == "completed" else "entity_resolution_validation",
                    started_at=now - timedelta(hours=2),
                    completed_at=now - timedelta(hours=1, minutes=45),
                    duration_seconds=15.4,
                    triggered_by_id=created_users["admin"].id,
                )
                session.add(job)
            documents.append(doc)
        print(f"       {len(documents)} documents & processing jobs ready.")

        # 5. Seed Support Tickets
        print("\n[5/10] Seeding Fact Tickets & SLA metrics...")
        tickets_seed = [
            {"ticket_id": "TCK-10482", "title": "Database query timeout during peak checkout hours", "customer": customers[0], "service": services[0], "priority": "critical", "status": "open", "sla_response_breached": False, "sla_resolution_breached": True, "resolution_time_hours": 8.5, "sentiment": "negative", "sentiment_score": -0.82, "root_cause": "Unindexed foreign key on transaction ledger"},
            {"ticket_id": "TCK-10483", "title": "JWT refresh token expiration misconfigured in EU region", "customer": customers[2], "service": services[1], "priority": "high", "status": "resolved", "sla_response_breached": False, "sla_resolution_breached": False, "resolution_time_hours": 1.2, "sentiment": "neutral", "sentiment_score": 0.05, "root_cause": "Nginx clock drift on node 3"},
            {"ticket_id": "TCK-10484", "title": "High memory consumption on batch document upload", "customer": customers[4], "service": services[2], "priority": "high", "status": "open", "sla_response_breached": True, "sla_resolution_breached": True, "resolution_time_hours": 14.0, "sentiment": "negative", "sentiment_score": -0.75, "root_cause": "PDF parser holding byte stream in heap"},
            {"ticket_id": "TCK-10485", "title": "Request for SSO SAML 2.0 integration documentation", "customer": customers[1], "service": services[1], "priority": "low", "status": "closed", "sla_response_breached": False, "sla_resolution_breached": False, "resolution_time_hours": 2.5, "sentiment": "positive", "sentiment_score": 0.88, "root_cause": "Configuration guidance provided"},
            {"ticket_id": "TCK-10486", "title": "Event bus consumer lag reaching 15,000 messages", "customer": customers[0], "service": services[3], "priority": "critical", "status": "in_progress", "sla_response_breached": False, "sla_resolution_breached": False, "resolution_time_hours": None, "sentiment": "negative", "sentiment_score": -0.65, "root_cause": "Under-provisioned partition consumers"},
            {"ticket_id": "TCK-10487", "title": "Automated weekly CSV export failing with HTTP 504", "customer": customers[6], "service": services[4], "priority": "medium", "status": "resolved", "sla_response_breached": False, "sla_resolution_breached": False, "resolution_time_hours": 4.1, "sentiment": "neutral", "sentiment_score": -0.10, "root_cause": "Query execution time limit adjusted to 120s"},
            {"ticket_id": "TCK-10488", "title": "Recurring connection pool exhaustion on primary DB", "customer": customers[2], "service": services[0], "priority": "critical", "status": "open", "sla_response_breached": False, "sla_resolution_breached": True, "resolution_time_hours": 11.2, "sentiment": "negative", "sentiment_score": -0.90, "root_cause": "Leaked async sessions in background tasks"},
            {"ticket_id": "TCK-10489", "title": "Inquiry regarding GDPR data deletion capabilities", "customer": customers[5], "service": services[0], "priority": "low", "status": "closed", "sla_response_breached": False, "sla_resolution_breached": False, "resolution_time_hours": 3.0, "sentiment": "positive", "sentiment_score": 0.70, "root_cause": "Privacy compliance protocol shared"},
        ]
        tickets_count = 0
        for t in tickets_seed:
            res = await session.execute(select(FactTicket).where(FactTicket.title == t["title"]))
            if not res.scalar_one_or_none():
                ticket = FactTicket(
                    ticket_number=t["ticket_id"],
                    title=t["title"],
                    customer_id=t["customer"].id,
                    service_id=t["service"].id,
                    assigned_to_id=employees[0].id,
                    priority=t["priority"],
                    severity=t["priority"],
                    status=t["status"],
                    created_date=now - timedelta(days=2, hours=tickets_count),
                    sla_response_breached=t["sla_response_breached"],
                    sla_resolution_breached=t["sla_resolution_breached"],
                    resolution_time_hours=t["resolution_time_hours"],
                    sentiment=t["sentiment"],
                    sentiment_score=t["sentiment_score"],
                    root_cause=t["root_cause"],
                    extraction_confidence=0.92,
                )
                session.add(ticket)
                tickets_count += 1
        print(f"       {tickets_count} tickets seeded.")

        # 6. Seed Operational Incidents
        print("\n[6/10] Seeding Fact Incidents & Postmortems...")
        incidents_seed = [
            {"incident_number": "INC-2026-001", "title": "Primary PostgreSQL cluster failover degraded query response", "service": services[0], "customer": customers[0], "severity": "P1", "status": "resolved", "downtime_minutes": 47.0, "resolution_time_hours": 1.5, "sla_breached": True, "root_cause": "Hardware memory parity fault on replica master", "root_cause_category": "Infrastructure Failure"},
            {"incident_number": "INC-2026-002", "title": "Token signing key rotation caused temporary auth rejections", "service": services[1], "customer": customers[2], "severity": "P2", "status": "resolved", "downtime_minutes": 18.0, "resolution_time_hours": 0.8, "sla_breached": False, "root_cause": "Key propagation delay across edge gateways", "root_cause_category": "Configuration Error"},
            {"incident_number": "INC-2026-003", "title": "Kafka partition rebalance deadlock stalled event streaming", "service": services[3], "customer": customers[4], "severity": "P1", "status": "open", "downtime_minutes": 85.0, "resolution_time_hours": None, "sla_breached": True, "root_cause": "Zookeeper session timeout during network jitter", "root_cause_category": "Distributed Systems"},
            {"incident_number": "INC-2026-004", "title": "OCR worker memory overflow during large TIFF processing", "service": services[2], "customer": customers[1], "severity": "P3", "status": "resolved", "downtime_minutes": 0.0, "resolution_time_hours": 2.2, "sla_breached": False, "root_cause": "Image decompression bomb threshold exceeded", "root_cause_category": "Application Exception"},
            {"incident_number": "INC-2026-005", "title": "Intermittent packet loss on EU-Central cross-region peering link", "service": services[3], "customer": customers[2], "severity": "P2", "status": "open", "downtime_minutes": 32.0, "resolution_time_hours": None, "sla_breached": True, "root_cause": "ISP transit provider BGP flapping", "root_cause_category": "Network Degradation"},
        ]
        inc_count = 0
        for i in incidents_seed:
            res = await session.execute(select(FactIncident).where(FactIncident.incident_number == i["incident_number"]))
            if not res.scalar_one_or_none():
                inc = FactIncident(
                    incident_number=i["incident_number"],
                    title=i["title"],
                    service_id=i["service"].id,
                    customer_id=i["customer"].id,
                    location_id=locations[0].id,
                    assigned_to_id=employees[1].id,
                    severity=i["severity"],
                    status=i["status"],
                    occurred_at=now - timedelta(days=1, hours=inc_count * 4),
                    resolved_at=now - timedelta(hours=2) if i["status"] == "resolved" else None,
                    downtime_minutes=i["downtime_minutes"],
                    resolution_time_hours=i["resolution_time_hours"],
                    sla_breached=i["sla_breached"],
                    root_cause=i["root_cause"],
                    root_cause_category=i["root_cause_category"],
                    extraction_confidence=0.95,
                )
                session.add(inc)
                inc_count += 1
        print(f"       {inc_count} operational incidents seeded.")

        # 7. Seed Customer Feedback
        print("\n[7/10] Seeding customer feedback & sentiment records...")
        feedback_seed = [
            {"customer": customers[0], "text": "The platform analytics are powerful, but the recent database timeouts during our Black Friday preparation have severely impacted team confidence.", "rating": 2.0, "nps": 3, "sentiment": "negative", "sentiment_score": -0.85},
            {"customer": customers[1], "text": "Super smooth implementation! The API docs and role-based permissions made our enterprise audit a breeze.", "rating": 5.0, "nps": 10, "sentiment": "positive", "sentiment_score": 0.92},
            {"customer": customers[2], "text": "Good core system, but SLA breach resolution takes too long. Need dedicated tier-1 support contact.", "rating": 3.0, "nps": 6, "sentiment": "neutral", "sentiment_score": -0.15},
            {"customer": customers[3], "text": "Outstanding uptime and scalability for our cloud infrastructure. Very pleased with the platform stability.", "rating": 5.0, "nps": 10, "sentiment": "positive", "sentiment_score": 0.95},
            {"customer": customers[4], "text": "Constant ingestion lag on large Excel spreadsheets. Support tickets take more than 24 hours to resolve.", "rating": 2.0, "nps": 4, "sentiment": "negative", "sentiment_score": -0.78},
        ]
        fb_count = 0
        for fb in feedback_seed:
            res = await session.execute(select(FactFeedback).where(FactFeedback.raw_text == fb["text"]))
            if not res.scalar_one_or_none():
                f_record = FactFeedback(
                    customer_id=fb["customer"].id,
                    feedback_type="nps",
                    raw_text=fb["text"],
                    rating=fb["rating"],
                    nps_score=fb["nps"],
                    sentiment=fb["sentiment"],
                    sentiment_score=fb["sentiment_score"],
                    feedback_date=now - timedelta(days=fb_count * 2),
                    extraction_confidence=0.91,
                )
                session.add(f_record)
                fb_count += 1
        print(f"       {fb_count} customer feedback records seeded.")

        # 8. Seed Sentiment Trends & Analytics Scores
        print("\n[8/10] Seeding sentiment trends and customer health scores...")
        # 12 months sentiment trend (aggregate where customer_id is None)
        for month_idx in range(12):
            p_start = now - timedelta(days=(11 - month_idx) * 30)
            res = await session.execute(
                select(SentimentTrend)
                .where(SentimentTrend.customer_id == None)
                .where(SentimentTrend.period_start == p_start)
            )
            if not res.scalar_one_or_none():
                pos = 65.0 + (month_idx % 4) * 3
                neg = 15.0 - (month_idx % 3) * 2
                neu = 100.0 - pos - neg
                trend = SentimentTrend(
                    period_start=p_start,
                    period_end=p_start + timedelta(days=30),
                    period_type="monthly",
                    customer_id=None,
                    total_records=120 + month_idx * 15,
                    positive_count=int(80 + month_idx * 10),
                    neutral_count=int(25 + month_idx * 2),
                    negative_count=int(15 + month_idx * 3),
                    positive_pct=pos,
                    neutral_pct=neu,
                    negative_pct=neg,
                    avg_sentiment_score=0.45 + (month_idx * 0.02),
                )
                session.add(trend)

        # Customer health score snapshots
        for c in customers:
            res = await session.execute(
                select(CustomerHealthScore).where(CustomerHealthScore.customer_id == c.id)
            )
            if not res.scalar_one_or_none():
                chs = CustomerHealthScore(
                    customer_id=c.id,
                    snapshot_date=now,
                    health_score=c.health_score or 70.0,
                    risk_level=c.risk_level or "LOW",
                    trend="DETERIORATING" if c.risk_level in ["CRITICAL", "HIGH"] else "IMPROVING",
                    churn_probability=c.churn_risk_score,
                    ticket_count_30d=8 if c.risk_level == "CRITICAL" else 2,
                    sla_breach_count_30d=3 if c.risk_level == "CRITICAL" else 0,
                    contributing_factors=[
                        {"factor": "Repeated SLA breaches on Database Cluster", "weight": 0.45},
                        {"factor": "Negative sentiment in recent NPS feedback", "weight": 0.35},
                    ] if c.risk_level == "CRITICAL" else [
                        {"factor": "Consistent low ticket frequency", "weight": 0.60},
                    ],
                )
                session.add(chs)

        # 9. Seed Business Insights & Anomalies
        print("\n[9/10] Seeding AI Business Insights & Detected Anomalies...")
        insights_seed = [
            {
                "insight_type": "risk",
                "title": "Critical Churn Risk Alert: Acme Global Enterprise ($750K ARR)",
                "description": "Acme Global health score dropped from 74 to 42.5 following 3 consecutive SLA breaches on the primary database cluster.",
                "what_happened": "Cluster latency spikes exceeded contract SLA thresholds on August 28 and September 4, resulting in executive customer escalation.",
                "why_it_matters": "Contract renewal is scheduled in 68 days. Loss of this enterprise tier account represents a direct $750,000 ARR impact.",
                "recommended_action": "Schedule immediate executive QBR with Account Director Marcus Vance and deploy dedicated DB connection pool allocation.",
                "severity": "CRITICAL",
                "priority_score": 96.5,
                "confidence": 0.94,
                "entity_type": "customer",
                "entity_name": "Acme Global Enterprise",
                "financial_impact_estimate": 750000.0,
                "status": "active",
                "generated_by": "insight_engine",
                "is_cross_domain": True,
            },
            {
                "insight_type": "operational_issue",
                "title": "Cross-Service Correlated Failure: Streaming Bus & Ingestion Worker",
                "description": "Spike in Kafka consumer lag directly precedes OCR document ingestion timeouts across EU-Central region.",
                "what_happened": "Unbuffered message bursts generated heap exhaustion on worker pods, causing cascading HTTP 504 errors.",
                "why_it_matters": "Document processing throughput dropped by 43% during peak business hours for 4 tier-1 customers.",
                "recommended_action": "Enable partition autoscaling on Kafka cluster and increase worker pod memory limit from 2Gi to 4Gi.",
                "severity": "HIGH",
                "priority_score": 88.0,
                "confidence": 0.91,
                "entity_type": "service",
                "entity_name": "Real-Time Streaming Event Bus",
                "financial_impact_estimate": 120000.0,
                "status": "active",
                "generated_by": "anomaly_detector",
                "is_cross_domain": True,
            },
            {
                "insight_type": "opportunity",
                "title": "Expansion Opportunity: CloudScale Infrastructure ($240K -> $480K)",
                "description": "CloudScale usage has grown 180% quarter-over-quarter with 92.5 health score and 0 open escalations.",
                "what_happened": "Tenant consumption reached 92% of tier quota without performance degradation.",
                "why_it_matters": "High willingness to upgrade to Enterprise Tier with multi-region replication add-on.",
                "recommended_action": "Sales engineering team should present multi-region failover proposal before Q4 planning cycle.",
                "severity": "MEDIUM",
                "priority_score": 75.0,
                "confidence": 0.88,
                "entity_type": "customer",
                "entity_name": "CloudScale Infrastructure",
                "financial_impact_estimate": 240000.0,
                "status": "active",
                "generated_by": "insight_engine",
                "is_cross_domain": False,
            },
            {
                "insight_type": "data_quality",
                "title": "Contract Entity Resolution Ambiguity: RetailGiant Subsidiary",
                "description": "Uploaded contract 'retailgiant_expansion_contract_draft.pdf' contains conflicting legal entity names.",
                "what_happened": "Entity resolution engine matched both 'RetailGiant Inc' (CUST_005) and 'RetailGiant Logistics DE' with 65% confidence.",
                "why_it_matters": "Prevents automated contract aggregation and financial reporting in Tableau and executive dashboard.",
                "recommended_action": "Review item in Human-in-the-Loop Review Queue to confirm canonical entity mapping.",
                "severity": "LOW",
                "priority_score": 52.0,
                "confidence": 0.65,
                "entity_type": "document",
                "entity_name": "retailgiant_expansion_contract_draft.pdf",
                "financial_impact_estimate": 0.0,
                "status": "active",
                "generated_by": "rule_engine",
                "is_cross_domain": False,
            },
        ]
        ins_count = 0
        for ins in insights_seed:
            res = await session.execute(select(BusinessInsight).where(BusinessInsight.title == ins["title"]))
            if not res.scalar_one_or_none():
                item = BusinessInsight(**ins)
                session.add(item)
                ins_count += 1
        print(f"       {ins_count} AI business insights seeded.")

        # Anomalies
        anomalies_seed = [
            {"metric_name": "Database Query Latency (p99)", "observed_value": 4820.0, "expected_value": 450.0, "deviation_pct": 971.1, "detection_method": "isolation_forest", "severity": "CRITICAL", "is_resolved": False, "possible_causes": ["Unindexed ledger queries", "Connection pool starvation"]},
            {"metric_name": "Hourly Support Ticket Volume", "observed_value": 48.0, "expected_value": 12.0, "deviation_pct": 300.0, "detection_method": "zscore", "severity": "HIGH", "is_resolved": False, "possible_causes": ["EU cluster authentication outage", "Client SDK version mismatch"]},
            {"metric_name": "Document Ingestion Failure Rate", "observed_value": 14.8, "expected_value": 1.2, "deviation_pct": 1133.3, "detection_method": "rolling_average", "severity": "HIGH", "is_resolved": True, "possible_causes": ["Corrupted TIFF upload batch", "Worker memory constraint"]},
            {"metric_name": "Average Customer Sentiment Score", "observed_value": -0.42, "expected_value": 0.65, "deviation_pct": -164.6, "detection_method": "zscore", "severity": "MEDIUM", "is_resolved": False, "possible_causes": ["Recent downtime impact on Q3 NPS scores"]},
        ]
        anom_count = 0
        for anom in anomalies_seed:
            res = await session.execute(select(AnomalyRecord).where(AnomalyRecord.metric_name == anom["metric_name"]))
            if not res.scalar_one_or_none():
                ar = AnomalyRecord(**anom, detected_at=now - timedelta(hours=anom_count * 3))
                session.add(ar)
                anom_count += 1
        print(f"       {anom_count} anomaly records seeded.")

        # 10. Seed Data Quality & Review Queue
        print("\n[10/10] Seeding Data Quality Reports & Review Queue...")
        dq_seed = [
            {"dataset_name": "Customer Support Tickets Export", "overall_score": 94.2, "completeness_score": 96.0, "validity_score": 98.0, "consistency_score": 92.5, "uniqueness_score": 90.5, "total_records": 1240, "invalid_records": 18, "duplicate_records": 6},
            {"dataset_name": "Contract Legal Terms Extraction", "overall_score": 87.5, "completeness_score": 89.0, "validity_score": 94.0, "consistency_score": 82.0, "uniqueness_score": 85.0, "total_records": 480, "invalid_records": 24, "duplicate_records": 12},
            {"dataset_name": "Telemetry & Incident Logs", "overall_score": 98.6, "completeness_score": 99.2, "validity_score": 99.0, "consistency_score": 97.8, "uniqueness_score": 98.5, "total_records": 18450, "invalid_records": 42, "duplicate_records": 0},
            {"dataset_name": "Customer Feedback & NPS Surveys", "overall_score": 91.0, "completeness_score": 94.5, "validity_score": 95.0, "consistency_score": 88.0, "uniqueness_score": 86.5, "total_records": 890, "invalid_records": 15, "duplicate_records": 8},
        ]
        for dq in dq_seed:
            res = await session.execute(select(DataQualityReport).where(DataQualityReport.dataset_name == dq["dataset_name"]))
            if not res.scalar_one_or_none():
                dqr = DataQualityReport(**dq, report_date=now - timedelta(days=1))
                session.add(dqr)

        # Review queue items
        review_seed = [
            {"item_type": "low_confidence_extraction", "title": "Contract penalty clause value extraction ambiguity", "description": "Extracted monetary penalty clause from 'retailgiant_expansion_contract_draft.pdf' has 65% confidence.", "confidence": 0.65, "status": "pending", "priority": "high"},
            {"item_type": "entity_resolution", "title": "Customer canonical mapping: 'RetailGiant DE' vs 'RetailGiant Inc'", "description": "Fuzzy name match score 0.72 requires analyst confirmation for master customer ID.", "confidence": 0.72, "status": "pending", "priority": "medium"},
            {"item_type": "data_quality", "title": "Missing required field: SLA resolution time in Ticket #10486", "description": "Ticket imported without resolution timestamp; auto-fill suggested from incident #INC-2026-003.", "confidence": 0.81, "status": "pending", "priority": "low"},
            {"item_type": "low_confidence_extraction", "title": "Product classification for 'Custom Enterprise API Connector'", "description": "Model suggested 'Enterprise Analytics Suite' with 58% confidence.", "confidence": 0.58, "status": "pending", "priority": "medium"},
        ]
        for rev in review_seed:
            res = await session.execute(select(ReviewQueueItem).where(ReviewQueueItem.title == rev["title"]))
            if not res.scalar_one_or_none():
                rqi = ReviewQueueItem(**rev)
                session.add(rqi)

        await session.commit()

    print("\n" + "=" * 60)
    print("  [SUCCESS] All platform features successfully seeded!")
    print("=" * 60)
    print("\n  Summary of Seeded Data:")
    print("    - Demo Users:      Admin, Analyst, Viewer")
    print("    - Customers:       10 Enterprise Accounts (with health & churn scores)")
    print("    - Products:        5 Core Product Catalog items")
    print("    - Services:        5 Infrastructure & API Services")
    print("    - Documents:       6 Ingested raw source files across all domains")
    print("    - Support Tickets: 8 Detailed tickets with SLA & sentiment metrics")
    print("    - Incidents:       5 P1-P3 operational incident postmortems")
    print("    - Feedback:        5 Survey & NPS customer records")
    print("    - Sentiment Trend: 12 Months of aggregate trend data for charts")
    print("    - AI Insights:     4 Critical & high-priority executive alerts")
    print("    - Anomalies:       4 Detected metric deviations & root causes")
    print("    - Data Quality:    4 Dataset health & completeness reports")
    print("    - Review Queue:    4 Pending human-in-the-loop review items")
    print("\n  Login credentials:")
    print("    - admin@eip.local   / Admin@12345")
    print("    - analyst@eip.local / Analyst@12345")
    print("    - viewer@eip.local  / Viewer@12345\n")


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    asyncio.run(seed_all(reset=reset_flag))
