"""
Insights router — the showpiece endpoint.
"""
from __future__ import annotations
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.analytics import BusinessInsight
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class InsightRead(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    insight_type: str
    title: str
    description: str
    what_happened: Optional[str] = None
    why_it_matters: Optional[str] = None
    recommended_action: Optional[str] = None
    severity: str
    priority_score: float
    confidence: float
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    entity_name: Optional[str] = None
    metric_name: Optional[str] = None
    current_value: Optional[float] = None
    baseline_value: Optional[float] = None
    change_pct: Optional[float] = None
    evidence: Optional[list] = None
    contributing_factors: Optional[list] = None
    financial_impact_estimate: Optional[float] = None
    affected_population: Optional[int] = None
    status: str
    generated_by: str
    is_cross_domain: bool
    created_at: datetime

class InsightList(BaseModel):
    items: list[InsightRead]
    total: int
    page: int
    page_size: int

@router.get("", response_model=InsightList)
async def list_insights(
    page: int = 1,
    page_size: int = 20,
    severity: Optional[str] = None,
    insight_type: Optional[str] = None,
    status: Optional[str] = "active",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(BusinessInsight).order_by(
        desc(BusinessInsight.priority_score),
        desc(BusinessInsight.created_at),
    )
    if severity:
        q = q.where(BusinessInsight.severity == severity.upper())
    if insight_type:
        q = q.where(BusinessInsight.insight_type == insight_type)
    if status:
        q = q.where(BusinessInsight.status == status)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.offset((page - 1) * page_size).limit(page_size))
    return InsightList(
        items=[InsightRead.model_validate(i) for i in result.scalars().all()],
        total=total, page=page, page_size=page_size,
    )

@router.get("/{insight_id}", response_model=InsightRead)
async def get_insight(
    insight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BusinessInsight).where(BusinessInsight.id == insight_id))
    ins = result.scalar_one_or_none()
    if not ins:
        raise HTTPException(status_code=404, detail="Insight not found")
    return ins

@router.patch("/{insight_id}/acknowledge")
async def acknowledge_insight(
    insight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import timezone
    result = await db.execute(select(BusinessInsight).where(BusinessInsight.id == insight_id))
    ins = result.scalar_one_or_none()
    if not ins:
        raise HTTPException(status_code=404, detail="Insight not found")
    ins.status = "acknowledged"
    ins.acknowledged_by_id = current_user.id
    ins.acknowledged_at = datetime.now(timezone.utc)
    return {"status": "acknowledged"}
