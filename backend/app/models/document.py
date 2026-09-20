"""
Core data models: Documents, Processing Jobs, Raw Records.
Layer 1 (RAW) and Layer 2 (STAGING) tables.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Float, ForeignKey,
    Index, Integer, String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


# ── RAW LAYER ─────────────────────────────────────────────────────────────────

class RawDocument(Base, UUIDMixin, TimestampMixin):
    """Represents an uploaded source file. Immutable once created."""
    __tablename__ = "raw_documents"

    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf, docx, txt, csv, xlsx
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # SHA-256
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Domain classification
    domain: Mapped[str] = mapped_column(String(100), nullable=False, default="unknown")
    # customer_intelligence | it_operations | document_contract | unknown

    # Processing state
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")
    # uploaded | queued | processing | completed | failed | review_required

    # Metadata extracted from the document
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    doc_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Uploader
    uploaded_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Processing summary
    extraction_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    processing_jobs: Mapped[list["ProcessingJob"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    raw_records: Mapped[list["RawRecord"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    extracted_entities: Mapped[list["ExtractedEntity"]] = relationship(back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_raw_documents_status_domain", "status", "domain"),
    )

    def __repr__(self) -> str:
        return f"<RawDocument {self.original_filename} [{self.status}]>"


class RawRecord(Base, UUIDMixin, TimestampMixin):
    """A single row extracted from a CSV/Excel document."""
    __tablename__ = "raw_records"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False)  # original row as JSON
    normalized_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    data_quality_flags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    document: Mapped["RawDocument"] = relationship(back_populates="raw_records")

    __table_args__ = (
        Index("ix_raw_records_document_row", "document_id", "row_number"),
    )


# ── PROCESSING JOBS ───────────────────────────────────────────────────────────

class ProcessingJob(Base, UUIDMixin, TimestampMixin):
    """Tracks background processing jobs."""
    __tablename__ = "processing_jobs"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # ingestion | extraction | normalization | entity_resolution | analytics | insights

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    # pending | running | completed | failed | cancelled

    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    current_step: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    result_summary: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_traceback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logs: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True, default=list)

    triggered_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    document: Mapped["RawDocument"] = relationship(back_populates="processing_jobs")

    __table_args__ = (
        Index("ix_processing_jobs_status", "status"),
        Index("ix_processing_jobs_document_type", "document_id", "job_type"),
    )


# ── STAGING LAYER ─────────────────────────────────────────────────────────────

class ExtractedEntity(Base, UUIDMixin, TimestampMixin):
    """
    Staging table for all AI-extracted entities with full provenance.
    Every structured fact derived from unstructured data lands here first.
    """
    __tablename__ = "stg_extracted_entities"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    raw_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_records.id", ondelete="SET NULL"), nullable=True
    )

    # Entity details
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # customer | company | person | product | service | location | incident |
    # date | monetary_value | issue | root_cause | sentiment | category | severity

    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    canonical_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # After resolution

    # Confidence & provenance
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    extraction_method: Mapped[str] = mapped_column(String(100), nullable=False)
    # mock | gemini | openai | spacy | textblob | rule_based

    model_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_text_span: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    char_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    char_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Review
    review_status: Mapped[str] = mapped_column(String(50), default="auto_accepted", nullable=False)
    # auto_accepted | pending_review | approved | rejected | edited
    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    domain: Mapped[str] = mapped_column(String(100), nullable=False, default="unknown")

    document: Mapped["RawDocument"] = relationship(back_populates="extracted_entities")

    __table_args__ = (
        Index("ix_stg_entities_type_domain", "entity_type", "domain"),
        Index("ix_stg_entities_document_type", "document_id", "entity_type"),
        Index("ix_stg_entities_confidence", "confidence"),
        Index("ix_stg_entities_review_status", "review_status"),
    )

    def __repr__(self) -> str:
        return f"<ExtractedEntity {self.entity_type}:{self.field_name}={self.raw_value[:30]}>"
