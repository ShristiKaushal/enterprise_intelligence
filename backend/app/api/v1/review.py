"""Review queue router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timezone
from app.api.v1.auth import get_current_user, require_role
from app.database.session import get_db
from app.models.core import ReviewQueueItem
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ReviewAction(BaseModel):
    action: str  # approved | rejected | edited | ignored
    resolution_note: Optional[str] = None
    edited_value: Optional[dict] = None

@router.get("")
async def list_review_items(
    page: int = 1, page_size: int = 20, status: str = "pending",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(ReviewQueueItem).where(ReviewQueueItem.status == status)\
        .order_by(desc(ReviewQueueItem.created_at))
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.offset((page - 1) * page_size).limit(page_size))
    items = result.scalars().all()
    return {"items": [
        {"id": str(i.id), "item_type": i.item_type, "title": i.title,
         "description": i.description, "confidence": i.confidence,
         "status": i.status, "priority": i.priority, "created_at": i.created_at}
        for i in items
    ], "total": total}

@router.post("/{item_id}/action")
async def review_action(
    item_id: uuid.UUID,
    action: ReviewAction,
    current_user: User = Depends(require_role("analyst")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ReviewQueueItem).where(ReviewQueueItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")
    if action.action not in ["approved", "rejected", "edited", "ignored"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    item.status = action.action
    item.reviewed_by_id = current_user.id
    item.reviewed_at = datetime.now(timezone.utc)
    item.resolution_note = action.resolution_note
    return {"status": action.action, "item_id": str(item_id)}
