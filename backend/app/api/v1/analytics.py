"""
Analytics overview router.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.core import DimCustomer, FactTicket, FactIncident
from app.models.analytics import BusinessInsight, CustomerHealthScore
from app.models.user import User

router = APIRouter()

@router.get("/overview")
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Executive KPI overview."""
    total_customers = (await db.execute(select(func.count()).select_from(DimCustomer))).scalar_one()
    total_tickets = (await db.execute(select(func.count()).select_from(FactTicket))).scalar_one()
    open_tickets = (await db.execute(
        select(func.count()).select_from(FactTicket).where(FactTicket.status == "open")
    )).scalar_one()
    total_incidents = (await db.execute(select(func.count()).select_from(FactIncident))).scalar_one()
    open_incidents = (await db.execute(
        select(func.count()).select_from(FactIncident).where(FactIncident.status == "open")
    )).scalar_one()
    sla_breaches = (await db.execute(
        select(func.count()).select_from(FactIncident).where(FactIncident.sla_breached == True)
    )).scalar_one()
    critical_insights = (await db.execute(
        select(func.count()).select_from(BusinessInsight)
        .where(BusinessInsight.severity == "CRITICAL", BusinessInsight.status == "active")
    )).scalar_one()
    high_risk_customers = (await db.execute(
        select(func.count()).select_from(DimCustomer)
        .where(DimCustomer.risk_level.in_(["HIGH", "CRITICAL"]))
    )).scalar_one()

    return {
        "total_customers": total_customers,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "sla_breaches": sla_breaches,
        "critical_insights": critical_insights,
        "high_risk_customers": high_risk_customers,
    }

@router.get("/sentiment-trend")
async def get_sentiment_trend(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.analytics import SentimentTrend
    result = await db.execute(
        select(SentimentTrend)
        .where(SentimentTrend.customer_id == None)
        .order_by(SentimentTrend.period_start.desc())
        .limit(12)
    )
    rows = result.scalars().all()
    return [
        {
            "period": r.period_start.strftime("%Y-%m") if r.period_start else None,
            "positive_pct": r.positive_pct,
            "neutral_pct": r.neutral_pct,
            "negative_pct": r.negative_pct,
            "total_records": r.total_records,
        }
        for r in reversed(rows)
    ]

@router.get("/customer-health-distribution")
async def get_health_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DimCustomer.risk_level, func.count().label("count"))
        .group_by(DimCustomer.risk_level)
    )
    return [{"risk_level": r or "UNKNOWN", "count": c} for r, c in result.all()]
