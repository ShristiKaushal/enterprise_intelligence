"""
Schemas for documents, processing jobs, etc.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel


class DocumentRead(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    original_filename: str
    file_type: str
    file_size_bytes: int
    domain: str
    status: str
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    extraction_confidence: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None


class DocumentList(BaseModel):
    items: List[DocumentRead]
    total: int
    page: int
    page_size: int


class ProcessRequest(BaseModel):
    job_type: Optional[str] = "full_pipeline"
    force_reprocess: bool = False


class JobRead(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    document_id: UUID
    job_type: str
    status: str
    progress: int
    current_step: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result_summary: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
