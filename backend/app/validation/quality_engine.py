"""
Data Quality Engine — calculates completeness, validity, consistency,
uniqueness, and timeliness scores for any dataset.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class FieldQualityResult:
    field_name: str
    null_count: int
    null_pct: float
    invalid_count: int
    invalid_pct: float
    unique_count: int
    total_count: int
    sample_issues: list[str] = field(default_factory=list)


@dataclass
class DataQualityResult:
    dataset_name: str
    total_records: int
    valid_records: int
    invalid_records: int
    duplicate_records: int
    missing_critical_fields: int
    records_requiring_review: int

    # Scores 0-100
    overall_score: float
    completeness_score: float
    validity_score: float
    consistency_score: float
    uniqueness_score: float
    timeliness_score: float

    issues: list[dict] = field(default_factory=list)
    field_stats: dict[str, FieldQualityResult] = field(default_factory=dict)


CRITICAL_FIELDS = {
    "ticket": ["ticket_number", "customer_name", "priority", "status", "created_date"],
    "incident": ["incident_number", "severity", "occurred_at", "service_name"],
    "feedback": ["raw_text", "feedback_date", "sentiment"],
    "contract": ["contract_number", "start_date", "end_date"],
    "customer": ["name", "email"],
}

# Validation rules per field pattern
VALIDITY_RULES = {
    "email": (r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$", "Invalid email format"),
    "date": (r"^\d{4}-\d{2}-\d{2}", "Invalid date format"),
    "phone": (r"^[+\d\s\-()]{7,15}$", "Invalid phone format"),
    "currency": (r"^\$?[\d,]+\.?\d*$", "Invalid currency format"),
    "priority": (r"^(critical|high|medium|low|p[1-4])$", "Invalid priority value"),
    "sentiment": (r"^(positive|negative|neutral)$", "Invalid sentiment value"),
    "severity": (r"^(critical|high|medium|low|p[1-4])$", "Invalid severity value"),
}


class DataQualityEngine:
    """
    Calculates data quality dimensions from a list of records.
    """

    def evaluate(
        self,
        records: list[dict],
        dataset_name: str = "dataset",
        record_type: str = "ticket",
        critical_fields: Optional[list[str]] = None,
    ) -> DataQualityResult:
        if not records:
            return self._empty_result(dataset_name)

        crit_fields = critical_fields or CRITICAL_FIELDS.get(record_type, [])
        total = len(records)
        issues = []

        # ── Completeness ─────────────────────────────────────────────────────
        missing_critical = 0
        null_counts: dict[str, int] = {}
        all_fields = set()
        for r in records:
            all_fields.update(r.keys())
        for f in all_fields:
            nc = sum(1 for r in records if not r.get(f))
            null_counts[f] = nc
        for f in crit_fields:
            nc = null_counts.get(f, total)
            missing_critical += nc
            if nc > 0:
                issues.append({
                    "type": "missing_critical_field",
                    "field": f,
                    "affected_records": nc,
                    "pct": round(nc / total * 100, 1),
                })

        completeness = max(0.0, 100.0 - (missing_critical / (total * max(len(crit_fields), 1))) * 100)

        # ── Validity ─────────────────────────────────────────────────────────
        invalid_counts = 0
        invalid_records_set = set()
        for i, record in enumerate(records):
            for field_name, value in record.items():
                if value is None:
                    continue
                rule_key = self._get_rule_key(field_name)
                if rule_key and rule_key in VALIDITY_RULES:
                    pattern, msg = VALIDITY_RULES[rule_key]
                    if not re.match(pattern, str(value), re.IGNORECASE):
                        invalid_counts += 1
                        invalid_records_set.add(i)
                        if len(issues) < 50:
                            issues.append({
                                "type": "invalid_value",
                                "field": field_name,
                                "value": str(value)[:50],
                                "message": msg,
                            })

        invalid_records = len(invalid_records_set)
        validity = max(0.0, 100.0 * (1 - invalid_counts / max(total * len(all_fields), 1)))

        # ── Uniqueness (duplicate detection) ─────────────────────────────────
        seen_keys: set[str] = set()
        duplicates = 0
        for record in records:
            # Use first 3 fields as key
            key_fields = list(record.values())[:3]
            key = "|".join(str(v) for v in key_fields if v)
            if key in seen_keys and key:
                duplicates += 1
                if len(issues) < 50:
                    issues.append({
                        "type": "duplicate_record",
                        "key": key[:100],
                        "count": duplicates,
                    })
            seen_keys.add(key)

        uniqueness = max(0.0, 100.0 * (1 - duplicates / total))

        # ── Consistency (cross-field checks) ─────────────────────────────────
        consistency_issues = 0
        for record in records:
            # Check date ordering where applicable
            start = record.get("start_date") or record.get("created_date")
            end = record.get("end_date") or record.get("resolved_date")
            if start and end:
                try:
                    if str(start) > str(end):
                        consistency_issues += 1
                        if len(issues) < 50:
                            issues.append({
                                "type": "date_ordering",
                                "message": f"start_date > end_date: {start} > {end}",
                            })
                except Exception:
                    pass

        consistency = max(0.0, 100.0 * (1 - consistency_issues / total))

        # ── Timeliness ────────────────────────────────────────────────────────
        now = datetime.now(timezone.utc)
        stale_count = 0
        for record in records:
            for date_field in ["created_date", "updated_at", "occurred_at"]:
                val = record.get(date_field)
                if val:
                    try:
                        if isinstance(val, str):
                            # Try parsing
                            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
                                try:
                                    d = datetime.strptime(val[:19], fmt)
                                    # Flag records older than 2 years
                                    if (now - d.replace(tzinfo=timezone.utc)).days > 730:
                                        stale_count += 1
                                    break
                                except ValueError:
                                    pass
                    except Exception:
                        pass
                    break
        timeliness = max(0.0, 100.0 * (1 - stale_count / total))

        # ── Field-level stats ─────────────────────────────────────────────────
        field_stats = {}
        for f in list(all_fields)[:20]:  # Cap at 20 fields for performance
            nc = null_counts.get(f, 0)
            unique_vals = set(r.get(f) for r in records if r.get(f))
            field_stats[f] = FieldQualityResult(
                field_name=f,
                null_count=nc,
                null_pct=round(nc / total * 100, 1),
                invalid_count=0,
                invalid_pct=0.0,
                unique_count=len(unique_vals),
                total_count=total,
            )

        # ── Overall score (weighted) ──────────────────────────────────────────
        overall = (
            completeness * 0.30
            + validity * 0.25
            + uniqueness * 0.20
            + consistency * 0.15
            + timeliness * 0.10
        )

        records_requiring_review = len([
            i for i in invalid_records_set
        ]) + min(duplicates, total)

        return DataQualityResult(
            dataset_name=dataset_name,
            total_records=total,
            valid_records=total - invalid_records,
            invalid_records=invalid_records,
            duplicate_records=duplicates,
            missing_critical_fields=missing_critical,
            records_requiring_review=min(records_requiring_review, total),
            overall_score=round(overall, 1),
            completeness_score=round(completeness, 1),
            validity_score=round(validity, 1),
            consistency_score=round(consistency, 1),
            uniqueness_score=round(uniqueness, 1),
            timeliness_score=round(timeliness, 1),
            issues=issues[:50],
            field_stats=field_stats,
        )

    def _get_rule_key(self, field_name: str) -> Optional[str]:
        field_lower = field_name.lower()
        for key in VALIDITY_RULES:
            if key in field_lower:
                return key
        return None

    def _empty_result(self, dataset_name: str) -> DataQualityResult:
        return DataQualityResult(
            dataset_name=dataset_name,
            total_records=0, valid_records=0, invalid_records=0,
            duplicate_records=0, missing_critical_fields=0, records_requiring_review=0,
            overall_score=0.0, completeness_score=0.0, validity_score=0.0,
            consistency_score=0.0, uniqueness_score=0.0, timeliness_score=0.0,
        )


data_quality_engine = DataQualityEngine()
