"""
Entity Resolution Engine.
Resolves raw entity mentions to canonical entities using:
1. Exact matching
2. Normalized string matching
3. Fuzzy matching (RapidFuzz)
4. Optional embedding similarity
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Optional

from rapidfuzz import fuzz, process

from app.normalization.normalizer import text_normalizer
from app.core.logging import get_logger

logger = get_logger(__name__)

# Confidence thresholds
EXACT_MATCH_CONF = 1.0
NORMALIZED_MATCH_CONF = 0.95
FUZZY_HIGH_CONF = 0.90
FUZZY_MEDIUM_CONF = 0.75
FUZZY_LOW_CONF = 0.60

FUZZY_HIGH_THRESHOLD = 95
FUZZY_MEDIUM_THRESHOLD = 85
FUZZY_LOW_THRESHOLD = 70
REVIEW_THRESHOLD = 60


@dataclass
class EntityCandidate:
    canonical_id: str
    canonical_name: str
    normalized_name: str
    aliases: list[str] = field(default_factory=list)


@dataclass
class ResolutionDecision:
    raw_value: str
    entity_type: str
    canonical_id: str
    canonical_name: str
    confidence: float
    resolution_method: str
    is_new_entity: bool
    requires_review: bool
    score: float = 0.0


class EntityResolver:
    """
    In-memory entity resolver. In production, backs to PostgreSQL.
    """

    def __init__(self) -> None:
        # entity_type -> list of candidates
        self._registry: dict[str, list[EntityCandidate]] = {}

    def _normalize(self, name: str) -> str:
        return text_normalizer.normalize_entity_name(name)

    def register(
        self,
        entity_type: str,
        canonical_id: str,
        canonical_name: str,
        aliases: Optional[list[str]] = None,
    ) -> None:
        if entity_type not in self._registry:
            self._registry[entity_type] = []
        candidate = EntityCandidate(
            canonical_id=canonical_id,
            canonical_name=canonical_name,
            normalized_name=self._normalize(canonical_name),
            aliases=[self._normalize(a) for a in (aliases or [])],
        )
        self._registry[entity_type].append(candidate)

    def resolve(self, raw_value: str, entity_type: str) -> ResolutionDecision:
        """Resolve a raw entity mention to its canonical form."""
        candidates = self._registry.get(entity_type, [])
        normalized_input = self._normalize(raw_value)

        if not candidates:
            # No known entities of this type — it's new
            new_id = self._generate_id(entity_type, raw_value)
            decision = ResolutionDecision(
                raw_value=raw_value,
                entity_type=entity_type,
                canonical_id=new_id,
                canonical_name=raw_value,
                confidence=0.5,
                resolution_method="new_entity",
                is_new_entity=True,
                requires_review=False,
            )
            self._auto_register(entity_type, decision)
            return decision

        # 1. Exact match on canonical name
        for c in candidates:
            if c.canonical_name.lower() == raw_value.lower():
                return ResolutionDecision(
                    raw_value=raw_value,
                    entity_type=entity_type,
                    canonical_id=c.canonical_id,
                    canonical_name=c.canonical_name,
                    confidence=EXACT_MATCH_CONF,
                    resolution_method="exact",
                    is_new_entity=False,
                    requires_review=False,
                )

        # 2. Normalized match
        for c in candidates:
            if c.normalized_name == normalized_input or normalized_input in c.aliases:
                return ResolutionDecision(
                    raw_value=raw_value,
                    entity_type=entity_type,
                    canonical_id=c.canonical_id,
                    canonical_name=c.canonical_name,
                    confidence=NORMALIZED_MATCH_CONF,
                    resolution_method="normalized",
                    is_new_entity=False,
                    requires_review=False,
                )

        # 3. Fuzzy matching
        all_names = {c.normalized_name: c for c in candidates}
        # Also include aliases
        for c in candidates:
            for alias in c.aliases:
                all_names[alias] = c

        if all_names:
            best_match, score, _ = process.extractOne(
                normalized_input,
                list(all_names.keys()),
                scorer=fuzz.token_sort_ratio,
            )
            matched_candidate = all_names[best_match]

            if score >= FUZZY_HIGH_THRESHOLD:
                return ResolutionDecision(
                    raw_value=raw_value, entity_type=entity_type,
                    canonical_id=matched_candidate.canonical_id,
                    canonical_name=matched_candidate.canonical_name,
                    confidence=FUZZY_HIGH_CONF,
                    resolution_method="fuzzy",
                    is_new_entity=False,
                    requires_review=False,
                    score=score,
                )
            elif score >= FUZZY_MEDIUM_THRESHOLD:
                return ResolutionDecision(
                    raw_value=raw_value, entity_type=entity_type,
                    canonical_id=matched_candidate.canonical_id,
                    canonical_name=matched_candidate.canonical_name,
                    confidence=FUZZY_MEDIUM_CONF,
                    resolution_method="fuzzy",
                    is_new_entity=False,
                    requires_review=False,
                    score=score,
                )
            elif score >= FUZZY_LOW_THRESHOLD:
                return ResolutionDecision(
                    raw_value=raw_value, entity_type=entity_type,
                    canonical_id=matched_candidate.canonical_id,
                    canonical_name=matched_candidate.canonical_name,
                    confidence=FUZZY_LOW_CONF,
                    resolution_method="fuzzy",
                    is_new_entity=False,
                    requires_review=True,  # Low confidence → human review
                    score=score,
                )
            elif score >= REVIEW_THRESHOLD:
                # Possible match but needs review
                return ResolutionDecision(
                    raw_value=raw_value, entity_type=entity_type,
                    canonical_id=matched_candidate.canonical_id,
                    canonical_name=matched_candidate.canonical_name,
                    confidence=0.45,
                    resolution_method="fuzzy_uncertain",
                    is_new_entity=False,
                    requires_review=True,
                    score=score,
                )

        # 4. New entity
        new_id = self._generate_id(entity_type, raw_value)
        decision = ResolutionDecision(
            raw_value=raw_value,
            entity_type=entity_type,
            canonical_id=new_id,
            canonical_name=raw_value,
            confidence=0.5,
            resolution_method="new_entity",
            is_new_entity=True,
            requires_review=False,
        )
        self._auto_register(entity_type, decision)
        return decision

    def _generate_id(self, entity_type: str, name: str) -> str:
        prefix_map = {
            "customer": "CUST",
            "company": "COMP",
            "service": "SVC",
            "product": "PROD",
            "employee": "EMP",
            "location": "LOC",
        }
        prefix = prefix_map.get(entity_type, "ENT")
        # Use first 8 chars of UUID for uniqueness
        uid = str(uuid.uuid4()).replace("-", "")[:8].upper()
        return f"{prefix}_{uid}"

    def _auto_register(self, entity_type: str, decision: ResolutionDecision) -> None:
        self.register(
            entity_type=entity_type,
            canonical_id=decision.canonical_id,
            canonical_name=decision.canonical_name,
        )


# Singleton resolver (pre-loaded with common entities on startup)
entity_resolver = EntityResolver()
