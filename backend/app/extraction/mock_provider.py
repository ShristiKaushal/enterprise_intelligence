"""
MockProvider — deterministic, seed-based AI extraction.
Works 100% locally with no external API calls.
Used for demo and testing.
"""
from __future__ import annotations

import hashlib
import random
import re
from typing import Optional

from app.extraction.base import (
    AIProvider,
    ExtractionField,
    ExtractionResult,
    SourceReference,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Taxonomy ──────────────────────────────────────────────────────────────────

CUSTOMER_PATTERNS = [
    r"(?i)(customer|client|account)[:\s]+([A-Z][a-zA-Z\s&.,'-]+?)(?:\s|,|\.|$)",
    r"(?i)(?:from|by|re:)\s+([A-Z][a-zA-Z\s&.,'-]+?)\s*(?:Ltd|Inc|Corp|LLC|Pvt)?(?:\s|,|\.|$)",
]

SEVERITY_KEYWORDS = {
    "critical": ["critical", "urgent", "emergency", "p1", "down", "outage", "breach"],
    "high": ["high", "major", "p2", "severe", "significant"],
    "medium": ["medium", "moderate", "p3", "normal"],
    "low": ["low", "minor", "p4", "informational"],
}

SENTIMENT_SIGNALS = {
    "positive": [
        "excellent", "great", "good", "happy", "satisfied", "perfect",
        "awesome", "helpful", "fast", "resolved", "thank", "appreciate",
        "impressed", "smooth", "easy",
    ],
    "negative": [
        "terrible", "awful", "bad", "angry", "frustrated", "disappointed",
        "broken", "failed", "worst", "slow", "unacceptable", "outage",
        "down", "useless", "crash", "error", "not working",
    ],
    "neutral": [],
}

TOPIC_PATTERNS = {
    "vpn": ["vpn", "remote access", "virtual private", "tunnel"],
    "authentication": ["login", "password", "auth", "sso", "credentials", "mfa", "2fa"],
    "performance": ["slow", "latency", "performance", "lag", "timeout", "response time"],
    "availability": ["down", "outage", "unavailable", "offline", "not working", "crash"],
    "billing": ["invoice", "billing", "payment", "charge", "refund", "subscription"],
    "onboarding": ["setup", "install", "onboard", "configuration", "configure"],
    "data_loss": ["lost data", "data loss", "missing data", "deleted"],
    "security": ["hack", "breach", "vulnerability", "unauthorized", "security"],
    "network": ["network", "connectivity", "connection", "internet", "bandwidth"],
    "email": ["email", "mail", "inbox", "outlook", "exchange"],
}

CUSTOMER_DOMAIN_FIELDS = [
    "customer_name", "customer_email", "product", "service",
    "issue_description", "priority", "sentiment",
    "resolution_status", "ticket_number",
]

OPERATIONS_DOMAIN_FIELDS = [
    "incident_id", "service_name", "severity", "root_cause",
    "affected_systems", "resolution_time", "assigned_to", "downtime_minutes",
]

CONTRACT_DOMAIN_FIELDS = [
    "contract_number", "party_name", "start_date", "end_date",
    "contract_value", "payment_terms", "renewal_clause", "sla_terms",
]


class MockProvider(AIProvider):
    """
    Deterministic mock AI provider.
    Uses text analysis heuristics to simulate LLM extraction.
    All outputs are reproducible given the same input.
    """

    @property
    def name(self) -> str:
        return "mock"

    @property
    def model_version(self) -> str:
        return "mock-v1.0"

    def _get_seed(self, text: str) -> int:
        """Create a stable seed from text hash for reproducibility."""
        return int(hashlib.md5(text[:200].encode()).hexdigest(), 16) % (2**31)

    def _extract_sentiment(self, text: str) -> tuple[str, float]:
        text_lower = text.lower()
        pos = sum(1 for w in SENTIMENT_SIGNALS["positive"] if w in text_lower)
        neg = sum(1 for w in SENTIMENT_SIGNALS["negative"] if w in text_lower)

        total = pos + neg
        if total == 0:
            return "neutral", 0.5

        pos_ratio = pos / total
        if pos_ratio > 0.6:
            confidence = min(0.95, 0.6 + pos_ratio * 0.35)
            return "positive", round(confidence, 2)
        elif pos_ratio < 0.4:
            confidence = min(0.95, 0.6 + (1 - pos_ratio) * 0.35)
            return "negative", round(confidence, 2)
        else:
            return "neutral", 0.65

    def _detect_severity(self, text: str) -> tuple[str, float]:
        text_lower = text.lower()
        for level, keywords in SEVERITY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return level, 0.82
        return "medium", 0.55

    def _extract_topics(self, text: str) -> list[str]:
        text_lower = text.lower()
        found = []
        for topic, patterns in TOPIC_PATTERNS.items():
            if any(p in text_lower for p in patterns):
                found.append(topic)
        return found[:5]

    def _extract_customer_name(self, text: str) -> Optional[str]:
        for pattern in CUSTOMER_PATTERNS:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                name = groups[-1].strip().rstrip(".,")
                if 2 < len(name) < 100:
                    return name
        return None

    def _extract_dates(self, text: str) -> list[str]:
        date_patterns = [
            r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
            r"\d{4}[/-]\d{1,2}[/-]\d{1,2}",
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}",
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        return list(set(dates))[:5]

    def _extract_monetary_values(self, text: str) -> list[str]:
        pattern = r"(?:USD|EUR|GBP|INR|\$|£|€)?\s*[\d,]+(?:\.\d{2})?(?:\s*(?:USD|EUR|GBP|INR|million|billion|thousand|k|M|B))?"
        return re.findall(pattern, text)[:5]

    async def extract_entities(
        self,
        text: str,
        document_id: str,
        domain: str,
        context: Optional[dict] = None,
    ) -> ExtractionResult:
        rng = random.Random(self._get_seed(text))
        sentiment, sent_conf = self._extract_sentiment(text)
        severity, sev_conf = self._detect_severity(text)
        topics = self._extract_topics(text)
        customer = self._extract_customer_name(text)
        dates = self._extract_dates(text)
        monetary = self._extract_monetary_values(text)

        ref = SourceReference(
            document_id=document_id,
            page=1,
            text_span=text[:200] if len(text) > 200 else text,
            char_start=0,
            char_end=min(200, len(text)),
        )

        fields: list[ExtractionField] = [
            ExtractionField(
                field="sentiment",
                value=sentiment,
                confidence=sent_conf,
                source_reference=ref,
                extraction_method="mock",
                model_version=self.model_version,
            ),
            ExtractionField(
                field="severity",
                value=severity,
                confidence=sev_conf,
                source_reference=ref,
                extraction_method="mock",
                model_version=self.model_version,
            ),
            ExtractionField(
                field="topics",
                value=topics,
                confidence=0.75 if topics else 0.3,
                source_reference=ref,
                extraction_method="mock",
                model_version=self.model_version,
            ),
        ]

        entities = []
        if customer:
            entities.append({
                "type": "customer",
                "value": customer,
                "confidence": rng.uniform(0.70, 0.92),
            })
        for d in dates:
            entities.append({"type": "date", "value": d, "confidence": 0.90})
        for m in monetary:
            entities.append({"type": "monetary_value", "value": m, "confidence": 0.85})

        # Domain-specific extraction
        if domain == "customer_intelligence":
            fields.extend(self._extract_customer_fields(text, document_id, rng))
        elif domain == "it_operations":
            fields.extend(self._extract_ops_fields(text, document_id, rng))
        elif domain == "document_contract":
            fields.extend(self._extract_contract_fields(text, document_id, rng))

        # Summary
        summary = text[:300].strip().replace("\n", " ") + ("..." if len(text) > 300 else "")

        overall_conf = sum(f.confidence for f in fields) / max(len(fields), 1)

        return ExtractionResult(
            document_id=document_id,
            fields=fields,
            entities=entities,
            sentiment=sentiment,
            sentiment_score=rng.uniform(0.2, 0.8) if sentiment == "neutral" else (
                rng.uniform(0.6, 0.95) if sentiment == "positive" else rng.uniform(0.05, 0.4)
            ),
            topics=topics,
            key_phrases=self._extract_key_phrases(text),
            summary=summary,
            overall_confidence=round(overall_conf, 2),
            extraction_method="mock",
            model_version=self.model_version,
        )

    def _extract_customer_fields(
        self, text: str, document_id: str, rng: random.Random
    ) -> list[ExtractionField]:
        ref = SourceReference(document_id=document_id, page=1, text_span=text[:100])
        fields = []
        # Try to extract ticket number
        ticket_match = re.search(r"(?:ticket|case|ref)[:\s#]+([A-Z0-9\-]+)", text, re.IGNORECASE)
        if ticket_match:
            fields.append(ExtractionField(
                field="ticket_number", value=ticket_match.group(1),
                confidence=0.95, source_reference=ref, extraction_method="mock",
            ))
        # Email
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
        if email_match:
            fields.append(ExtractionField(
                field="customer_email", value=email_match.group(),
                confidence=0.98, source_reference=ref, extraction_method="mock",
            ))
        return fields

    def _extract_ops_fields(
        self, text: str, document_id: str, rng: random.Random
    ) -> list[ExtractionField]:
        ref = SourceReference(document_id=document_id, page=1, text_span=text[:100])
        fields = []
        # Incident number
        inc_match = re.search(r"(?:INC|incident|ticket)[:\s#]+([A-Z0-9\-]+)", text, re.IGNORECASE)
        if inc_match:
            fields.append(ExtractionField(
                field="incident_number", value=inc_match.group(1),
                confidence=0.95, source_reference=ref, extraction_method="mock",
            ))
        # Downtime
        dt_match = re.search(r"(\d+)\s*(?:min(?:utes?)?|hours?)\s*(?:of)?\s*(?:down|outage)", text, re.IGNORECASE)
        if dt_match:
            fields.append(ExtractionField(
                field="downtime_minutes",
                value=int(dt_match.group(1)) * (60 if "hour" in dt_match.group(0).lower() else 1),
                confidence=0.88, source_reference=ref, extraction_method="mock",
            ))
        return fields

    def _extract_contract_fields(
        self, text: str, document_id: str, rng: random.Random
    ) -> list[ExtractionField]:
        ref = SourceReference(document_id=document_id, page=1, text_span=text[:100])
        fields = []
        # Contract number
        cn_match = re.search(r"(?:contract|agreement|ref)[:\s#]+([A-Z0-9\-\/]+)", text, re.IGNORECASE)
        if cn_match:
            fields.append(ExtractionField(
                field="contract_number", value=cn_match.group(1),
                confidence=0.93, source_reference=ref, extraction_method="mock",
            ))
        return fields

    def _extract_key_phrases(self, text: str) -> list[str]:
        words = re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text)
        return list(set(words))[:10]

    async def classify_document(
        self, text: str, document_id: str, domain: str
    ) -> ExtractionResult:
        severity, conf = self._detect_severity(text)
        topics = self._extract_topics(text)

        category = "general"
        if topics:
            category = topics[0]

        return ExtractionResult(
            document_id=document_id,
            fields=[
                ExtractionField(
                    field="category", value=category, confidence=0.78,
                    extraction_method="mock", model_version=self.model_version,
                ),
                ExtractionField(
                    field="severity", value=severity, confidence=conf,
                    extraction_method="mock", model_version=self.model_version,
                ),
            ],
            category=category,
            overall_confidence=0.78,
            extraction_method="mock",
            model_version=self.model_version,
        )

    async def analyze_sentiment(self, text: str, document_id: str) -> ExtractionResult:
        sentiment, conf = self._extract_sentiment(text)
        rng = random.Random(self._get_seed(text))
        score_map = {
            "positive": rng.uniform(0.65, 0.95),
            "negative": rng.uniform(0.05, 0.35),
            "neutral": rng.uniform(0.4, 0.6),
        }
        return ExtractionResult(
            document_id=document_id,
            fields=[
                ExtractionField(
                    field="sentiment", value=sentiment, confidence=conf,
                    extraction_method="mock", model_version=self.model_version,
                ),
            ],
            sentiment=sentiment,
            sentiment_score=round(score_map[sentiment], 3),
            overall_confidence=conf,
            extraction_method="mock",
            model_version=self.model_version,
        )

    async def extract_topics(self, text: str, document_id: str) -> list[str]:
        return self._extract_topics(text)

    async def generate_insight_narrative(self, insight_data: dict) -> str:
        title = insight_data.get("title", "Issue detected")
        entity = insight_data.get("entity_name", "Unknown entity")
        metric = insight_data.get("metric_name", "")
        change = insight_data.get("change_pct", 0)

        direction = "increased" if change and change > 0 else "decreased"
        return (
            f"{entity} shows {title.lower()}. "
            f"The {metric} has {direction} by {abs(change or 0):.1f}% "
            f"based on analysis of available records. "
            f"[Generated by MockProvider — deterministic simulation]"
        )

    async def is_available(self) -> bool:
        return True
