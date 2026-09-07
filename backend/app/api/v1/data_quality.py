"""Data quality router."""
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.analytics import DataQualityReport
from app.models.user import User

router = APIRouter()

@router.get("")
async def list_quality_reports(
    page: int = 1, page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DataQualityReport).order_by(desc(DataQualityReport.report_date))
        .offset((page - 1) * page_size).limit(page_size)
    )
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "dataset_name": r.dataset_name,
            "report_date": r.report_date,
            "overall_score": r.overall_score,
            "completeness_score": r.completeness_score,
            "validity_score": r.validity_score,
            "consistency_score": r.consistency_score,
            "uniqueness_score": r.uniqueness_score,
            "total_records": r.total_records,
            "invalid_records": r.invalid_records,
            "duplicate_records": r.duplicate_records,
        }
        for r in rows
    ]

@router.get("/summary")
async def quality_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import func
    result = await db.execute(
        select(
            func.avg(DataQualityReport.overall_score).label("avg_overall"),
            func.avg(DataQualityReport.completeness_score).label("avg_completeness"),
            func.avg(DataQualityReport.validity_score).label("avg_validity"),
            func.sum(DataQualityReport.total_records).label("total_records"),
            func.sum(DataQualityReport.invalid_records).label("total_invalid"),
            func.sum(DataQualityReport.duplicate_records).label("total_duplicates"),
        )
    )
    row = result.one()
    return {
        "avg_overall_score": round(row.avg_overall or 0, 1),
        "avg_completeness_score": round(row.avg_completeness or 0, 1),
        "avg_validity_score": round(row.avg_validity or 0, 1),
        "total_records_assessed": row.total_records or 0,
        "total_invalid_records": row.total_invalid or 0,
        "total_duplicate_records": row.total_duplicates or 0,
    }
