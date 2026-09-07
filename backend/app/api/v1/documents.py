"""
Documents API — upload, list, get, process.
"""
from __future__ import annotations

import hashlib
import shutil
import uuid
from pathlib import Path
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user, require_role
from app.core.config import settings
from app.database.session import get_db
from app.models.document import RawDocument, ProcessingJob
from app.models.user import User
from app.schemas.documents import DocumentRead, DocumentList, ProcessRequest
from app.tasks.queue import task_queue
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/upload", response_model=DocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    domain: str = Form(default="unknown"),
    current_user: User = Depends(require_role("analyst")),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document for processing."""
    # Validate extension
    ext = Path(file.filename or "").suffix.lstrip(".").lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{ext}' not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Read file
    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Compute hash
    file_hash = hashlib.sha256(content).hexdigest()

    # Check duplicate
    result = await db.execute(select(RawDocument).where(RawDocument.file_hash == file_hash))
    existing = result.scalar_one_or_none()
    if existing:
        logger.info("Duplicate file upload detected", hash=file_hash, existing_id=str(existing.id))
        return existing

    # Save file
    doc_id = uuid.uuid4()
    safe_filename = f"{doc_id}.{ext}"
    storage_path = settings.upload_path / safe_filename
    storage_path.write_bytes(content)

    # Create DB record
    doc = RawDocument(
        id=doc_id,
        filename=safe_filename,
        original_filename=file.filename or "unknown",
        file_type=ext,
        file_size_bytes=len(content),
        file_hash=file_hash,
        storage_path=str(storage_path),
        domain=domain,
        status="uploaded",
        uploaded_by_id=current_user.id,
    )
    db.add(doc)
    await db.flush()

    # Queue processing job
    job = ProcessingJob(
        document_id=doc_id,
        job_type="full_pipeline",
        status="pending",
        triggered_by_id=current_user.id,
    )
    db.add(job)
    await db.flush()

    # Submit to task queue
    await task_queue.enqueue("process_document", {
        "document_id": str(doc_id),
        "job_id": str(job.id),
        "domain": domain,
    })

    logger.info(
        "Document uploaded",
        doc_id=str(doc_id),
        filename=file.filename,
        domain=domain,
        size_kb=len(content) // 1024,
    )
    return doc


@router.get("", response_model=DocumentList)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    domain: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(RawDocument).order_by(RawDocument.created_at.desc())
    if domain:
        q = q.where(RawDocument.domain == domain)
    if status:
        q = q.where(RawDocument.status == status)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    docs = result.scalars().all()

    return DocumentList(
        items=[DocumentRead.model_validate(d) for d in docs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{doc_id}", response_model=DocumentRead)
async def get_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RawDocument).where(RawDocument.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/{doc_id}/process")
async def trigger_processing(
    doc_id: uuid.UUID,
    request: ProcessRequest,
    current_user: User = Depends(require_role("analyst")),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger processing for an existing document."""
    result = await db.execute(select(RawDocument).where(RawDocument.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    job = ProcessingJob(
        document_id=doc_id,
        job_type=request.job_type or "full_pipeline",
        status="pending",
        triggered_by_id=current_user.id,
    )
    db.add(job)
    await db.flush()

    await task_queue.enqueue("process_document", {
        "document_id": str(doc_id),
        "job_id": str(job.id),
        "domain": doc.domain,
    })

    return {"job_id": str(job.id), "status": "queued"}
