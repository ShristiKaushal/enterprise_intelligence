"""
Incidents router.
"""
from __future__ import annotations
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.core import FactIncident
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class IncidentRead(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    incident_number: str
    title: str
    severity: Optional[str] = None
    status: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    occurred_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    downtime_minutes: Optional[float] = None
    resolution_time_hours: Optional[float] = None
    sla_breached: bool
    root_cause: Optional[str] = None
    root_cause_category: Optional[str] = None
    extraction_confidence: Optional[float] = None
    created_at: datetime

class IncidentList(BaseModel):
    items: list[IncidentRead]
    total: int
    page: int
    page_size: int

@router.get("", response_model=IncidentList)
async def list_incidents(
    page: int = 1,
    page_size: int = 20,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    sla_breached: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(FactIncident).order_by(desc(FactIncident.created_at))
    if severity:
        q = q.where(FactIncident.severity == severity)
    if status:
        q = q.where(FactIncident.status == status)
    if sla_breached is not None:
        q = q.where(FactIncident.sla_breached == sla_breached)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.offset((page - 1) * page_size).limit(page_size))
    return IncidentList(
        items=[IncidentRead.model_validate(i) for i in result.scalars().all()],
        total=total, page=page, page_size=page_size,
    )

@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(
    incident_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FactIncident).where(FactIncident.id == incident_id))
    inc = result.scalar_one_or_none()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc
