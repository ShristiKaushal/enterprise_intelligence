"""
Document ingestion handlers for all supported file formats.
Each handler returns a standardized IngestionResult.
"""
from __future__ import annotations

import abc
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PageContent:
    page_number: int
    text: str
    tables: list[list[list[str]]] = field(default_factory=list)


@dataclass
class IngestionResult:
    """Standardized output from any ingestion handler."""
    file_type: str
    filename: str
    total_pages: int
    total_words: int
    pages: list[PageContent]
    full_text: str
    metadata: dict
    tables: list[dict] = field(default_factory=list)  # for CSV/Excel
    raw_rows: list[dict] = field(default_factory=list)  # for tabular data
    column_stats: dict = field(default_factory=dict)
    error: Optional[str] = None


class BaseIngestionHandler(abc.ABC):
    """Abstract base for file ingestion handlers."""

    @property
    @abc.abstractmethod
    def supported_extensions(self) -> list[str]: ...

    @abc.abstractmethod
    async def ingest(self, file_path: Path) -> IngestionResult: ...

    def _count_words(self, text: str) -> int:
        return len(text.split())
