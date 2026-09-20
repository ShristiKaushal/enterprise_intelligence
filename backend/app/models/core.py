"""
Core dimension and fact tables (CORE layer).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey,
    Index, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


# ── DIMENSIONS ────────────────────────────────────────────────────────────────

class DimCustomer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "dim_customer"

    canonical_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    # e.g. CUST_001
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    aliases: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)  # other names seen
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # enterprise | mid-market | smb
    contract_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    since_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    source_document_ids: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    resolution_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Derived health (updated by analytics engine)
    health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    churn_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # LOW | MEDIUM | HIGH | CRITICAL

    __table_args__ = (
        Index("ix_dim_customer_risk", "risk_level"),
    )


class DimProduct(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "dim_product"

    canonical_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    aliases: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class DimService(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "dim_service"

    canonical_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    aliases: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    service_type: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # network | application | database | infrastructure | support | cloud
    owner_team: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    sla_response_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sla_resolution_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Derived
    reliability_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class DimEmployee(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "dim_employee"

    canonical_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class DimLocation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "dim_location"

    canonical_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


# ── FACT TABLES ───────────────────────────────────────────────────────────────

class FactTicket(Base, UUIDMixin, TimestampMixin):
    """Support / help-desk tickets."""
    __tablename__ = "fact_ticket"

    ticket_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id"), nullable=True
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_customer.id"), nullable=True, index=True
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_product.id"), nullable=True
    )
    service_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_service.id"), nullable=True
    )
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_employee.id"), nullable=True
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # critical | high | medium | low
    severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Dates
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    first_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # SLA
    sla_response_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sla_resolution_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    response_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resolution_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sla_response_breached: Mapped[bool] = mapped_column(Boolean, default=False)
    sla_resolution_breached: Mapped[bool] = mapped_column(Boolean, default=False)

    # AI-derived
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause_category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    extraction_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_fact_ticket_customer_date", "customer_id", "created_date"),
        Index("ix_fact_ticket_status_priority", "status", "priority"),
        Index("ix_fact_ticket_sla_breach", "sla_resolution_breached"),
    )


class FactIncident(Base, UUIDMixin, TimestampMixin):
    """IT/Operations incident records."""
    __tablename__ = "fact_incident"

    incident_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id"), nullable=True
    )
    service_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_service.id"), nullable=True, index=True
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_customer.id"), nullable=True, index=True
    )
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_location.id"), nullable=True
    )
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_employee.id"), nullable=True
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # P1 | P2 | P3 | P4
    priority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Dates & duration
    occurred_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    detected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    downtime_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resolution_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False)

    # AI-derived
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause_category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    affected_systems: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    affected_users_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    business_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extraction_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_fact_incident_service_date", "service_id", "occurred_at"),
        Index("ix_fact_incident_severity", "severity"),
        Index("ix_fact_incident_customer", "customer_id"),
    )


class FactFeedback(Base, UUIDMixin, TimestampMixin):
    """Customer reviews, feedback, and survey responses."""
    __tablename__ = "fact_feedback"

    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id"), nullable=True
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_customer.id"), nullable=True, index=True
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_product.id"), nullable=True
    )
    service_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_service.id"), nullable=True
    )

    feedback_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # review | email | survey | support_comment | social | nps

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 1-5 or 1-10
    nps_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-10

    # AI-derived
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    topics: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    key_phrases: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    complaint_categories: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    extraction_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    feedback_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    author_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    __table_args__ = (
        Index("ix_fact_feedback_customer_date", "customer_id", "feedback_date"),
        Index("ix_fact_feedback_sentiment", "sentiment"),
    )


class FactContract(Base, UUIDMixin, TimestampMixin):
    """Contract and agreement records."""
    __tablename__ = "fact_contract"

    contract_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id"), nullable=True
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_customer.id"), nullable=True, index=True
    )

    contract_type: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Dates
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    signed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    renewal_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Financial
    total_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    penalty_clause_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI-derived
    key_obligations: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    sla_terms: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    risk_indicators: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    auto_renewal: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    extraction_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


# ── ENTITY RESOLUTION LOG ────────────────────────────────────────────────────

class EntityResolutionLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "entity_resolution_log"

    raw_value: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    canonical_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    canonical_name: Mapped[str] = mapped_column(Text, nullable=False)
    resolution_method: Mapped[str] = mapped_column(String(100), nullable=False)
    # exact | normalized | fuzzy | embedding | manual
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    is_new_entity: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_review: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id"), nullable=True
    )

    __table_args__ = (
        Index("ix_erl_entity_type_canonical", "entity_type", "canonical_id"),
    )


# ── PROVENANCE LINKS ─────────────────────────────────────────────────────────

class ProvenanceLink(Base, UUIDMixin, TimestampMixin):
    """Traces any analytics/insight record back to source documents & spans."""
    __tablename__ = "provenance_links"

    # Source end
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_text_span: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    char_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    char_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Target end (polymorphic by table name + id)
    target_table: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    link_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # extracted_entity | derived_fact | analytics_result | insight

    __table_args__ = (
        Index("ix_provenance_target", "target_table", "target_id"),
        Index("ix_provenance_source", "source_document_id"),
    )


# ── AUDIT LOG ────────────────────────────────────────────────────────────────

class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_log"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    previous_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        Index("ix_audit_log_user_action", "user_id", "action"),
        Index("ix_audit_log_resource", "resource_type", "resource_id"),
    )


# ── REVIEW QUEUE ─────────────────────────────────────────────────────────────

class ReviewQueueItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "review_queue"

    item_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # low_confidence_extraction | entity_resolution | data_quality | conflicting_info
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    entity_table: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    suggested_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    # pending | approved | rejected | edited | ignored
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)

    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_review_queue_status_priority", "status", "priority"),
    )
