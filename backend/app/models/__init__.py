"""
Models package — import all models here so Alembic can discover them.
"""
from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.user import User
from app.models.document import RawDocument, RawRecord, ProcessingJob, ExtractedEntity
from app.models.core import (
    DimCustomer, DimProduct, DimService, DimEmployee, DimLocation,
    FactTicket, FactIncident, FactFeedback, FactContract,
    EntityResolutionLog, ProvenanceLink, AuditLog, ReviewQueueItem,
)
from app.models.analytics import (
    CustomerHealthScore, ServiceHealthScore, SentimentTrend,
    AnomalyRecord, BusinessInsight, DataQualityReport,
)

__all__ = [
    "Base",
    "User",
    "RawDocument", "RawRecord", "ProcessingJob", "ExtractedEntity",
    "DimCustomer", "DimProduct", "DimService", "DimEmployee", "DimLocation",
    "FactTicket", "FactIncident", "FactFeedback", "FactContract",
    "EntityResolutionLog", "ProvenanceLink", "AuditLog", "ReviewQueueItem",
    "CustomerHealthScore", "ServiceHealthScore", "SentimentTrend",
    "AnomalyRecord", "BusinessInsight", "DataQualityReport",
]
