"""
AI Provider abstraction — supports Mock, Gemini, OpenAI, and Ollama.
All providers return the same ExtractionResult schema.
"""
from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SourceReference:
    document_id: str
    page: Optional[int] = None
    text_span: Optional[str] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None


@dataclass
class ExtractionField:
    """A single extracted field with confidence and provenance."""
    field: str
    value: Any
    confidence: float
    source_reference: Optional[SourceReference] = None
    extraction_method: str = "unknown"
    model_version: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "value": self.value,
            "confidence": self.confidence,
            "source_reference": {
                "document_id": self.source_reference.document_id if self.source_reference else None,
                "page": self.source_reference.page if self.source_reference else None,
                "text_span": self.source_reference.text_span if self.source_reference else None,
                "char_start": self.source_reference.char_start if self.source_reference else None,
                "char_end": self.source_reference.char_end if self.source_reference else None,
            } if self.source_reference else None,
            "extraction_method": self.extraction_method,
            "model_version": self.model_version,
        }


@dataclass
class ExtractionResult:
    """Complete result of processing one document."""
    document_id: str
    fields: list[ExtractionField] = field(default_factory=list)
    entities: list[dict] = field(default_factory=list)
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    topics: list[str] = field(default_factory=list)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    summary: Optional[str] = None
    key_phrases: list[str] = field(default_factory=list)
    overall_confidence: float = 0.0
    extraction_method: str = "unknown"
    model_version: Optional[str] = None
    raw_response: Optional[str] = None

    def get_field(self, name: str) -> Optional[ExtractionField]:
        return next((f for f in self.fields if f.field == name), None)

    def get_value(self, name: str, default: Any = None) -> Any:
        f = self.get_field(name)
        return f.value if f else default


class AIProvider(abc.ABC):
    """Abstract base for all AI providers."""

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @property
    @abc.abstractmethod
    def model_version(self) -> str: ...

    @abc.abstractmethod
    async def extract_entities(
        self,
        text: str,
        document_id: str,
        domain: str,
        context: Optional[dict] = None,
    ) -> ExtractionResult: ...

    @abc.abstractmethod
    async def classify_document(
        self,
        text: str,
        document_id: str,
        domain: str,
    ) -> ExtractionResult: ...

    @abc.abstractmethod
    async def analyze_sentiment(
        self,
        text: str,
        document_id: str,
    ) -> ExtractionResult: ...

    @abc.abstractmethod
    async def extract_topics(
        self,
        text: str,
        document_id: str,
    ) -> list[str]: ...

    @abc.abstractmethod
    async def generate_insight_narrative(
        self,
        insight_data: dict,
    ) -> str: ...

    @abc.abstractmethod
    async def is_available(self) -> bool: ...
