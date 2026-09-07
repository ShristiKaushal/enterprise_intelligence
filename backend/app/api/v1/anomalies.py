"""Anomalies router."""
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.analytics import AnomalyRecord
from app.models.user import User

router = APIRouter()

@router.get("")
async def list_anomalies(
    page: int = 1, page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnomalyRecord).order_by(desc(AnomalyRecord.detected_at))
        .offset((page - 1) * page_size).limit(page_size)
    )
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id), "metric_name": r.metric_name, "severity": r.severity,
            "observed_value": r.observed_value, "expected_value": r.expected_value,
            "deviation_pct": r.deviation_pct, "detection_method": r.detection_method,
            "detected_at": r.detected_at, "is_resolved": r.is_resolved,
            "possible_causes": r.possible_causes,
        }
        for r in rows
    ]
