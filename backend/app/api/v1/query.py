"""
Natural-language query router.
Safe intent-based SQL — never executes raw LLM-generated SQL directly.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from pydantic import BaseModel
import re

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

# ── Intent templates (safe, parameterized) ────────────────────────────────────
INTENT_PATTERNS = [
    {
        "pattern": r"(highest|most|top).*(support|risk|churn)",
        "intent": "top_risk_customers",
        "description": "Customers with highest support risk",
    },
    {
        "pattern": r"(incident|incidents).*(last|previous).*(month|week)",
        "intent": "recent_incidents",
        "description": "Recent incidents summary",
    },
    {
        "pattern": r"(sentiment|worsening|negative).*(service|product)",
        "intent": "negative_sentiment_services",
        "description": "Services with worsening sentiment",
    },
    {
        "pattern": r"(sla|breach|breaches).*(negative|sentiment)",
        "intent": "sla_and_sentiment",
        "description": "Customers with SLA breaches and negative sentiment",
    },
    {
        "pattern": r"(overview|summary|kpi|status)",
        "intent": "overview",
        "description": "Platform overview",
    },
]

async def _execute_intent(intent: str, db: AsyncSession) -> dict:
    """Execute a predefined safe query for the given intent."""
    if intent == "top_risk_customers":
        from app.models.core import DimCustomer
        result = await db.execute(
            select(DimCustomer.canonical_id, DimCustomer.name, DimCustomer.risk_level,
                   DimCustomer.health_score, DimCustomer.churn_risk_score)
            .where(DimCustomer.risk_level.in_(["HIGH", "CRITICAL"]))
            .order_by(DimCustomer.health_score.asc())
            .limit(10)
        )
        rows = result.all()
        return {
            "intent": intent,
            "results": [
                {"id": r[0], "name": r[1], "risk_level": r[2],
                 "health_score": r[3], "churn_risk": r[4]}
                for r in rows
            ],
            "explanation": f"Found {len(rows)} high/critical risk customers ordered by health score.",
        }

    elif intent == "recent_incidents":
        from app.models.core import FactIncident
        from datetime import datetime, timedelta, timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        result = await db.execute(
            select(func.count(), FactIncident.severity)
            .where(FactIncident.occurred_at >= cutoff)
            .group_by(FactIncident.severity)
        )
        rows = result.all()
        return {
            "intent": intent,
            "results": [{"count": r[0], "severity": r[1]} for r in rows],
            "explanation": "Incident counts by severity for the past 30 days.",
        }

    elif intent == "negative_sentiment_services":
        from app.models.analytics import SentimentTrend
        result = await db.execute(
            select(SentimentTrend)
            .where(SentimentTrend.service_id.isnot(None))
            .order_by(SentimentTrend.negative_pct.desc())
            .limit(10)
        )
        rows = result.scalars().all()
        return {
            "intent": intent,
            "results": [
                {"service_id": str(r.service_id), "negative_pct": r.negative_pct,
                 "period": str(r.period_start)}
                for r in rows
            ],
            "explanation": "Services ranked by negative sentiment percentage.",
        }

    elif intent == "overview":
        from app.models.core import DimCustomer, FactTicket, FactIncident
        from app.models.analytics import BusinessInsight
        cust = (await db.execute(select(func.count()).select_from(DimCustomer))).scalar_one()
        tickets = (await db.execute(select(func.count()).select_from(FactTicket))).scalar_one()
        incidents = (await db.execute(select(func.count()).select_from(FactIncident))).scalar_one()
        insights = (await db.execute(
            select(func.count()).select_from(BusinessInsight)
            .where(BusinessInsight.status == "active")
        )).scalar_one()
        return {
            "intent": intent,
            "results": {
                "customers": cust, "tickets": tickets,
                "incidents": incidents, "active_insights": insights,
            },
            "explanation": "Platform-wide overview metrics.",
        }

    return {"intent": intent, "results": [], "explanation": "No data available for this query."}


@router.post("")
async def natural_language_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Translate a natural-language question into a safe, pre-defined query.
    LLM output is NEVER executed directly against the database.
    """
    question = request.question.lower().strip()

    # Match intent
    matched_intent = None
    matched_description = None
    for template in INTENT_PATTERNS:
        if re.search(template["pattern"], question, re.IGNORECASE):
            matched_intent = template["intent"]
            matched_description = template["description"]
            break

    if not matched_intent:
        return {
            "question": request.question,
            "intent": "unknown",
            "results": [],
            "explanation": (
                "I could not map this question to a safe query template. "
                "Supported questions: top risk customers, recent incidents, "
                "services with worsening sentiment, SLA breaches, overview."
            ),
            "supported_questions": [t["description"] for t in INTENT_PATTERNS],
        }

    result = await _execute_intent(matched_intent, db)
    return {
        "question": request.question,
        "matched_description": matched_description,
        **result,
    }
