"""
Analytics layer models — pre-computed scores and insight records.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey,
    Index, Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class CustomerHealthScore(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analytics_customer_health"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_customer.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Overall
    health_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # LOW | MEDIUM | HIGH | CRITICAL
    trend: Mapped[str] = mapped_column(String(20), nullable=False)  # IMPROVING | STABLE | DETERIORATING

    # Components
    ticket_frequency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sla_compliance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resolution_time_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    incident_frequency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Raw metrics
    ticket_count_30d: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ticket_count_prev_30d: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    incident_count_30d: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sla_breach_count_30d: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    negative_feedback_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_resolution_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ML
    churn_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    churn_model_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    contributing_factors: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    evidence_document_ids: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_customer_health_risk", "risk_level", "snapshot_date"),
    )


class ServiceHealthScore(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analytics_service_health"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_service.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    reliability_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    availability_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    incident_count_30d: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_resolution_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sla_compliance_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    top_root_causes: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


class SentimentTrend(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analytics_sentiment"

    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)  # daily | weekly | monthly

    # Dimensions (nullable = aggregate rows with no specific entity)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_customer.id", ondelete="SET NULL"), nullable=True, index=True
    )
    service_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_service.id", ondelete="SET NULL"), nullable=True, index=True
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dim_product.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Counts
    total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    positive_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    neutral_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    negative_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    positive_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    neutral_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    negative_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    top_topics: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    top_complaints: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


class AnomalyRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analytics_anomalies"

    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    dimension: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    dimension_value: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    observed_value: Mapped[float] = mapped_column(Float, nullable=False)
    expected_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviation_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    detection_method: Mapped[str] = mapped_column(String(100), nullable=False)
    # zscore | iqr | isolation_forest | rolling_average
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # LOW | MEDIUM | HIGH | CRITICAL
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    possible_causes: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class BusinessInsight(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analytics_insights"

    # Identity
    insight_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # risk | opportunity | anomaly | trend | operational_issue | customer_issue |
    # financial_impact | data_quality | recommendation | emerging_issue | root_cause

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    what_happened: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    why_it_matters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Priority & severity
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # CRITICAL | HIGH | MEDIUM | LOW
    priority_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Entity
    entity_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    entity_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metrics
    metric_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    current_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    baseline_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    change_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Evidence
    evidence: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    supporting_record_ids: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    source_document_ids: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    contributing_factors: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Business impact
    financial_impact_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    affected_population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    # active | acknowledged | resolved | dismissed
    acknowledged_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Generation metadata
    generated_by: Mapped[str] = mapped_column(String(100), nullable=False, default="insight_engine")
    # insight_engine | ml_model | anomaly_detector | rule_engine
    is_cross_domain: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_insights_severity_priority", "severity", "priority_score"),
        Index("ix_insights_type_status", "insight_type", "status"),
        Index("ix_insights_entity", "entity_type", "entity_id"),
    )


class DataQualityReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analytics_data_quality"

    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_documents.id"), nullable=True, index=True
    )
    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    report_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Scores (0-100)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    completeness_score: Mapped[float] = mapped_column(Float, nullable=False)
    validity_score: Mapped[float] = mapped_column(Float, nullable=False)
    consistency_score: Mapped[float] = mapped_column(Float, nullable=False)
    uniqueness_score: Mapped[float] = mapped_column(Float, nullable=False)
    timeliness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Counts
    total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    invalid_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    missing_critical_fields: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_requiring_review: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    issues: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    field_stats: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
