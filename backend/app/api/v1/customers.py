"""
Customers router.
"""
from __future__ import annotations
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.core import DimCustomer
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class CustomerRead(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    canonical_id: str
    name: str
    company: Optional[str] = None
    region: Optional[str] = None
    tier: Optional[str] = None
    health_score: Optional[float] = None
    risk_level: Optional[str] = None
    churn_risk_score: Optional[float] = None
    contract_value: Optional[float] = None
    is_active: bool
    created_at: datetime

class CustomerList(BaseModel):
    items: list[CustomerRead]
    total: int
    page: int
    page_size: int

@router.get("", response_model=CustomerList)
async def list_customers(
    page: int = 1,
    page_size: int = 20,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(DimCustomer).order_by(desc(DimCustomer.created_at))
    if risk_level:
        q = q.where(DimCustomer.risk_level == risk_level.upper())
    if search:
        q = q.where(DimCustomer.name.ilike(f"%{search}%"))
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.offset((page - 1) * page_size).limit(page_size))
    return CustomerList(
        items=[CustomerRead.model_validate(c) for c in result.scalars().all()],
        total=total, page=page, page_size=page_size,
    )

@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(DimCustomer).where(DimCustomer.id == customer_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    return c
