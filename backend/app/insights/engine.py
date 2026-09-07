"""
Business Insight Engine — discovers intelligence not explicitly present in source data.

Components:
- TrendDetector
- AnomalyDetector
- RiskScorer
- EmergingIssueDetector
- RootCauseAnalyzer
- BusinessImpactEngine
- InsightPrioritizer
"""
from __future__ import annotations

import math
import statistics
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Data Structures ───────────────────────────────────────────────────────────

@dataclass
class InsightEvidence:
    label: str
    value: Any
    source_type: str  # ticket | incident | feedback | document
    record_id: Optional[str] = None
    document_id: Optional[str] = None


@dataclass
class GeneratedInsight:
    insight_type: str
    title: str
    description: str
    what_happened: str
    why_it_matters: str
    recommended_action: str
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW
    confidence: float
    entity_type: Optional[str]
    entity_id: Optional[str]
    entity_name: Optional[str]
    metric_name: Optional[str]
    current_value: Optional[float]
    baseline_value: Optional[float]
    change_pct: Optional[float]
    evidence: list[InsightEvidence]
    contributing_factors: list[str]
    financial_impact_estimate: Optional[float]
    affected_population: Optional[int]
    priority_score: float
    generated_by: str = "insight_engine"
    is_cross_domain: bool = False

    def to_dict(self) -> dict:
        return {
            "insight_id": str(uuid.uuid4()),
            "insight_type": self.insight_type,
            "title": self.title,
            "description": self.description,
            "what_happened": self.what_happened,
            "why_it_matters": self.why_it_matters,
            "recommended_action": self.recommended_action,
            "severity": self.severity,
            "confidence": round(self.confidence, 2),
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "change_pct": round(self.change_pct, 1) if self.change_pct else None,
            "evidence": [
                {"label": e.label, "value": e.value, "source_type": e.source_type}
                for e in self.evidence
            ],
            "contributing_factors": self.contributing_factors,
            "financial_impact_estimate": self.financial_impact_estimate,
            "affected_population": self.affected_population,
            "priority_score": round(self.priority_score, 2),
            "generated_by": self.generated_by,
            "is_cross_domain": self.is_cross_domain,
        }


# ── Trend Detector ────────────────────────────────────────────────────────────

class TrendDetector:
    """Detects statistically significant trends in time-series data."""

    def detect(
        self,
        series: list[float],
        labels: Optional[list[str]] = None,
        metric_name: str = "metric",
        min_points: int = 3,
    ) -> Optional[dict]:
        if len(series) < min_points:
            return None

        # Linear trend via simple least squares
        n = len(series)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(series) / n

        numerator = sum((x[i] - x_mean) * (series[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return None

        slope = numerator / denominator
        r_squared = 0.0
        try:
            ss_res = sum((series[i] - (y_mean + slope * (x[i] - x_mean))) ** 2 for i in range(n))
            ss_tot = sum((series[i] - y_mean) ** 2 for i in range(n))
            r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        except Exception:
            pass

        pct_change = ((series[-1] - series[0]) / abs(series[0]) * 100) if series[0] != 0 else 0

        direction = "INCREASING" if slope > 0 else "DECREASING"
        if abs(pct_change) < 5:
            direction = "STABLE"

        return {
            "metric_name": metric_name,
            "direction": direction,
            "slope": round(slope, 4),
            "r_squared": round(r_squared, 3),
            "pct_change": round(pct_change, 1),
            "first_value": series[0],
            "last_value": series[-1],
            "confidence": min(0.95, 0.5 + abs(r_squared) * 0.45),
        }


# ── Anomaly Detector ──────────────────────────────────────────────────────────

class AnomalyDetector:
    """Statistical anomaly detection using Z-score and IQR methods."""

    def detect_zscore(
        self,
        values: list[float],
        threshold: float = 2.5,
    ) -> list[dict]:
        if len(values) < 5:
            return []
        try:
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
            if stdev == 0:
                return []
            anomalies = []
            for i, v in enumerate(values):
                z = abs(v - mean) / stdev
                if z >= threshold:
                    anomalies.append({
                        "index": i,
                        "value": v,
                        "expected": round(mean, 2),
                        "z_score": round(z, 2),
                        "deviation_pct": round((v - mean) / abs(mean) * 100 if mean != 0 else 0, 1),
                        "method": "zscore",
                        "severity": "HIGH" if z > 3.5 else "MEDIUM",
                    })
            return anomalies
        except Exception as e:
            logger.warning("Z-score anomaly detection failed", error=str(e))
            return []

    def detect_iqr(self, values: list[float], k: float = 1.5) -> list[dict]:
        if len(values) < 5:
            return []
        try:
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            q1 = sorted_vals[n // 4]
            q3 = sorted_vals[3 * n // 4]
            iqr = q3 - q1
            lower = q1 - k * iqr
            upper = q3 + k * iqr
            median = statistics.median(values)

            anomalies = []
            for i, v in enumerate(values):
                if v < lower or v > upper:
                    anomalies.append({
                        "index": i,
                        "value": v,
                        "expected": round(median, 2),
                        "lower_bound": round(lower, 2),
                        "upper_bound": round(upper, 2),
                        "deviation_pct": round((v - median) / abs(median) * 100 if median != 0 else 0, 1),
                        "method": "iqr",
                        "severity": "HIGH" if (v > upper * 2 or v < lower / 2) else "MEDIUM",
                    })
            return anomalies
        except Exception as e:
            logger.warning("IQR anomaly detection failed", error=str(e))
            return []


# ── Risk Scorer ───────────────────────────────────────────────────────────────

class RiskScorer:
    """
    Calculates customer health and risk scores from operational metrics.

    Health score: 0-100 (100 = perfect health)
    Risk level: LOW | MEDIUM | HIGH | CRITICAL
    """

    def calculate_customer_health(
        self,
        ticket_count_30d: int = 0,
        ticket_count_prev: int = 0,
        incident_count_30d: int = 0,
        sla_breach_count: int = 0,
        negative_sentiment_pct: float = 0.0,  # 0-100
        avg_resolution_hours: float = 0.0,
        avg_rating: Optional[float] = None,  # 1-5
        contract_value: float = 0.0,
    ) -> dict:
        """
        Calculate a composite customer health score.
        Lower score = worse health.
        """
        # ── Ticket frequency component (0-100, inverted) ──────────────────
        # Baseline: ≤2 tickets/month = 100 pts
        ticket_score = max(0, 100 - max(0, ticket_count_30d - 2) * 8)

        # Ticket trend component
        if ticket_count_prev > 0:
            ticket_change_pct = (ticket_count_30d - ticket_count_prev) / ticket_count_prev * 100
        else:
            ticket_change_pct = 0
        trend_penalty = max(0, ticket_change_pct * 0.3)
        ticket_score = max(0, ticket_score - trend_penalty)

        # ── Sentiment component (0-100, inverted) ─────────────────────────
        # 0% negative = 100 pts, 100% negative = 0 pts
        sentiment_score = max(0, 100 - negative_sentiment_pct * 1.2)

        # ── SLA compliance ────────────────────────────────────────────────
        sla_score = max(0, 100 - sla_breach_count * 15)

        # ── Resolution time (0-100) ───────────────────────────────────────
        # <4h = 100 pts, >48h = 0 pts
        if avg_resolution_hours == 0:
            resolution_score = 80  # neutral when no data
        elif avg_resolution_hours <= 4:
            resolution_score = 100
        elif avg_resolution_hours <= 24:
            resolution_score = 100 - (avg_resolution_hours - 4) * 3.3
        else:
            resolution_score = max(0, 100 - avg_resolution_hours * 2)

        # ── Incident component ────────────────────────────────────────────
        incident_score = max(0, 100 - incident_count_30d * 10)

        # ── Rating component ──────────────────────────────────────────────
        if avg_rating is not None:
            rating_score = (avg_rating - 1) / 4 * 100  # Map 1-5 to 0-100
        else:
            rating_score = 70  # Neutral when no data

        # ── Weighted composite ────────────────────────────────────────────
        health_score = (
            ticket_score * 0.25
            + sentiment_score * 0.25
            + sla_score * 0.20
            + resolution_score * 0.15
            + incident_score * 0.10
            + rating_score * 0.05
        )
        health_score = round(max(0, min(100, health_score)), 1)

        # ── Risk level ────────────────────────────────────────────────────
        if health_score >= 75:
            risk_level = "LOW"
        elif health_score >= 55:
            risk_level = "MEDIUM"
        elif health_score >= 35:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        # ── Trend ─────────────────────────────────────────────────────────
        if ticket_change_pct > 20 or negative_sentiment_pct > 40:
            trend = "DETERIORATING"
        elif ticket_change_pct < -10:
            trend = "IMPROVING"
        else:
            trend = "STABLE"

        # ── Revenue at risk ───────────────────────────────────────────────
        if contract_value > 0:
            risk_factor = (100 - health_score) / 100
            revenue_at_risk = contract_value * risk_factor * 0.8
        else:
            revenue_at_risk = None

        return {
            "health_score": health_score,
            "risk_level": risk_level,
            "trend": trend,
            "components": {
                "ticket_frequency": round(ticket_score, 1),
                "sentiment": round(sentiment_score, 1),
                "sla_compliance": round(sla_score, 1),
                "resolution_time": round(resolution_score, 1),
                "incident_frequency": round(incident_score, 1),
                "customer_rating": round(rating_score, 1),
            },
            "ticket_change_pct": round(ticket_change_pct, 1),
            "revenue_at_risk": round(revenue_at_risk, 2) if revenue_at_risk else None,
        }


# ── Emerging Issue Detector ───────────────────────────────────────────────────

class EmergingIssueDetector:
    """
    Detects topics that are rapidly increasing in volume.
    """

    def detect(
        self,
        topic_counts_current: dict[str, int],
        topic_counts_previous: dict[str, int],
        min_current_count: int = 5,
        threshold_pct: float = 100.0,
    ) -> list[dict]:
        """
        Find topics with significant volume increases.
        threshold_pct: minimum % increase to flag (default 100% = doubled)
        """
        emerging = []
        for topic, current_count in topic_counts_current.items():
            if current_count < min_current_count:
                continue
            prev_count = topic_counts_previous.get(topic, 0)
            if prev_count == 0:
                # New topic altogether
                pct_change = 100.0
                is_new = True
            else:
                pct_change = (current_count - prev_count) / prev_count * 100
                is_new = False

            if pct_change >= threshold_pct:
                severity = "CRITICAL" if pct_change > 300 else "HIGH" if pct_change > 150 else "MEDIUM"
                emerging.append({
                    "topic": topic,
                    "current_count": current_count,
                    "previous_count": prev_count,
                    "pct_change": round(pct_change, 1),
                    "is_new_topic": is_new,
                    "severity": severity,
                })

        return sorted(emerging, key=lambda x: x["pct_change"], reverse=True)


# ── Root Cause Analyzer ───────────────────────────────────────────────────────

class RootCauseAnalyzer:
    """
    Groups incidents/issues by category and surfaces recurring patterns.
    """

    def analyze(
        self,
        incidents: list[dict],
        window_days: int = 30,
        min_occurrences: int = 3,
    ) -> list[dict]:
        """
        incidents: list of dicts with keys: category, subcategory, occurred_at, root_cause
        Returns potential root cause hypotheses.
        """
        from collections import Counter, defaultdict

        category_groups: dict[str, list[dict]] = defaultdict(list)
        for inc in incidents:
            cat = f"{inc.get('category', 'UNKNOWN')}/{inc.get('subcategory', 'OTHER')}"
            category_groups[cat].append(inc)

        hypotheses = []
        for category, group in category_groups.items():
            if len(group) < min_occurrences:
                continue

            # Root cause frequency
            root_causes = [i.get("root_cause", "") for i in group if i.get("root_cause")]
            rc_counter = Counter(root_causes)
            most_common_rc = rc_counter.most_common(1)
            top_rc = most_common_rc[0] if most_common_rc else (None, 0)

            # Check for temporal clustering
            dates = []
            for inc in group:
                occ = inc.get("occurred_at")
                if occ:
                    try:
                        if isinstance(occ, str):
                            d = datetime.fromisoformat(occ[:19])
                        else:
                            d = occ
                        dates.append(d)
                    except Exception:
                        pass

            temporal_pattern = None
            if len(dates) >= 3:
                # Check if incidents cluster on weekdays
                weekday_counts = Counter(d.weekday() for d in dates)
                most_common_day = weekday_counts.most_common(1)[0]
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                if most_common_day[1] >= len(dates) * 0.4:
                    temporal_pattern = f"Clustering on {day_names[most_common_day[0]]}s"

            confidence = min(0.90, 0.5 + len(group) * 0.05)
            if top_rc[0] and top_rc[1] >= len(group) * 0.5:
                confidence = min(0.90, confidence + 0.15)

            hypotheses.append({
                "category": category,
                "incident_count": len(group),
                "potential_root_cause": top_rc[0] if top_rc[1] >= 2 else "Undetermined — insufficient evidence",
                "rc_occurrence_count": top_rc[1],
                "rc_pct": round(top_rc[1] / len(group) * 100, 1) if group else 0,
                "temporal_pattern": temporal_pattern,
                "confidence": round(confidence, 2),
                "is_hypothesis": True,  # Always label as hypothesis
            })

        return sorted(hypotheses, key=lambda x: x["incident_count"], reverse=True)


# ── Business Impact Engine ────────────────────────────────────────────────────

class BusinessImpactEngine:
    """
    Translates operational metrics into estimated business impact.
    All outputs are clearly labeled as ESTIMATED.
    """

    # Industry average revenue per transaction (configurable)
    AVG_REVENUE_PER_TXN = 150.0
    AVG_TXN_PER_HOUR = 100.0

    def estimate_downtime_impact(
        self,
        downtime_minutes: float,
        affected_users: int = 100,
        revenue_per_hour: Optional[float] = None,
    ) -> dict:
        """Estimate revenue impact from downtime. ESTIMATED only."""
        hours = downtime_minutes / 60
        rev_per_hour = revenue_per_hour or (self.AVG_TXN_PER_HOUR * self.AVG_REVENUE_PER_TXN)
        estimated_loss = hours * rev_per_hour * (affected_users / 1000)

        return {
            "is_estimated": True,
            "downtime_hours": round(hours, 2),
            "estimated_revenue_loss": round(estimated_loss, 2),
            "assumptions": [
                f"Average revenue per hour: ${rev_per_hour:,.0f}",
                f"Affected users: {affected_users}",
                "Based on industry averages — not actual transaction data",
            ],
        }

    def estimate_sla_penalty(
        self,
        breach_count: int,
        penalty_per_breach: float = 5000.0,
        contract_value: Optional[float] = None,
    ) -> dict:
        """Estimate SLA penalty exposure. ESTIMATED only."""
        direct_penalty = breach_count * penalty_per_breach
        churn_risk_value = (contract_value * 0.6) if contract_value else None

        return {
            "is_estimated": True,
            "breach_count": breach_count,
            "direct_penalty_estimate": round(direct_penalty, 2),
            "churn_risk_value": round(churn_risk_value, 2) if churn_risk_value else None,
            "total_exposure": round(
                direct_penalty + (churn_risk_value or 0), 2
            ),
            "assumptions": [
                f"Assumed penalty per breach: ${penalty_per_breach:,.0f}",
                "Contract-specific terms may differ",
            ],
        }


# ── Insight Prioritizer ───────────────────────────────────────────────────────

class InsightPrioritizer:
    """
    Ranks insights using:
    priority = business_impact × confidence × urgency × affected_population
    """

    SEVERITY_WEIGHTS = {"CRITICAL": 1.0, "HIGH": 0.75, "MEDIUM": 0.5, "LOW": 0.25}
    URGENCY_MAP = {
        "risk": 0.9,
        "anomaly": 0.85,
        "sla_risk": 0.95,
        "emerging_issue": 0.85,
        "customer_issue": 0.80,
        "root_cause": 0.70,
        "trend": 0.60,
        "data_quality": 0.50,
        "opportunity": 0.45,
        "recommendation": 0.40,
    }

    def score(self, insight: GeneratedInsight) -> float:
        business_impact = self.SEVERITY_WEIGHTS.get(insight.severity, 0.5)
        confidence = insight.confidence
        urgency = self.URGENCY_MAP.get(insight.insight_type, 0.5)
        pop_factor = math.log(max(insight.affected_population or 1, 1) + 1) / 10
        pop_factor = min(pop_factor, 1.0)

        # Bonus for financial impact
        fin_bonus = 0.0
        if insight.financial_impact_estimate and insight.financial_impact_estimate > 10000:
            fin_bonus = min(0.2, insight.financial_impact_estimate / 500000)

        raw_score = (business_impact * confidence * urgency * (0.5 + pop_factor * 0.5)) + fin_bonus
        return round(min(1.0, raw_score), 4)

    def prioritize(self, insights: list[GeneratedInsight]) -> list[GeneratedInsight]:
        for insight in insights:
            insight.priority_score = self.score(insight)
        return sorted(insights, key=lambda x: x.priority_score, reverse=True)


# ── Insight Engine (orchestrator) ─────────────────────────────────────────────

class InsightEngine:
    """
    Main insight engine. Orchestrates all detectors and generators.
    """

    def __init__(self) -> None:
        self.trend_detector = TrendDetector()
        self.anomaly_detector = AnomalyDetector()
        self.risk_scorer = RiskScorer()
        self.emerging_issue_detector = EmergingIssueDetector()
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.business_impact_engine = BusinessImpactEngine()
        self.prioritizer = InsightPrioritizer()

    def generate_customer_health_insight(
        self,
        customer_name: str,
        customer_id: str,
        health_data: dict,
        contract_value: float = 0,
    ) -> Optional[GeneratedInsight]:
        """Generate a customer health insight if risk is non-trivial."""
        health = health_data.get("health_score", 100)
        risk = health_data.get("risk_level", "LOW")
        trend = health_data.get("trend", "STABLE")
        components = health_data.get("components", {})

        if risk == "LOW" and trend != "DETERIORATING":
            return None  # No actionable insight

        # Determine severity
        severity_map = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}
        severity = severity_map.get(risk, "MEDIUM")

        # Build evidence
        evidence = []
        ticket_change = health_data.get("ticket_change_pct", 0)
        if abs(ticket_change) > 10:
            evidence.append(InsightEvidence(
                label="Ticket volume change",
                value=f"{ticket_change:+.1f}%",
                source_type="ticket",
            ))

        revenue_at_risk = health_data.get("revenue_at_risk")
        if revenue_at_risk:
            evidence.append(InsightEvidence(
                label="Estimated revenue at risk (ESTIMATED)",
                value=f"${revenue_at_risk:,.0f}",
                source_type="analytics",
            ))

        # Contributing factors
        factors = []
        comp = health_data.get("components", {})
        if comp.get("ticket_frequency", 100) < 50:
            factors.append("High ticket volume")
        if comp.get("sentiment", 100) < 50:
            factors.append("Negative sentiment trend")
        if comp.get("sla_compliance", 100) < 70:
            factors.append("SLA breaches")
        if comp.get("resolution_time", 100) < 50:
            factors.append("Slow resolution times")
        if comp.get("incident_frequency", 100) < 50:
            factors.append("Elevated incident frequency")

        what_happened = (
            f"{customer_name} has a health score of {health}/100 with a '{risk}' risk level. "
            f"The account is {trend.lower()}."
        )
        why_matters = (
            f"Deteriorating customer health indicates increased churn risk. "
        )
        if revenue_at_risk:
            why_matters += f"Estimated ${revenue_at_risk:,.0f} in contract value is at risk. "
        why_matters += "Early intervention is significantly more cost-effective than recovery."

        rec_action = (
            f"Schedule an urgent account review for {customer_name}. "
            f"Address top factors: {', '.join(factors[:3]) if factors else 'review all metrics'}. "
            f"Assign a dedicated customer success manager if not already in place."
        )

        return GeneratedInsight(
            insight_type="risk",
            title=f"Customer Health Deterioration: {customer_name}",
            description=f"{customer_name} shows a health score of {health}/100 — {risk} risk.",
            what_happened=what_happened,
            why_it_matters=why_matters,
            recommended_action=rec_action,
            severity=severity,
            confidence=0.82,
            entity_type="customer",
            entity_id=customer_id,
            entity_name=customer_name,
            metric_name="customer_health_score",
            current_value=health,
            baseline_value=100.0,
            change_pct=health - 100,
            evidence=evidence,
            contributing_factors=factors,
            financial_impact_estimate=revenue_at_risk,
            affected_population=1,
            priority_score=0.0,  # Set by prioritizer
        )

    def generate_emerging_issue_insight(self, emerging: dict) -> GeneratedInsight:
        topic = emerging["topic"].replace("_", " ").title()
        current = emerging["current_count"]
        prev = emerging["previous_count"]
        pct = emerging["pct_change"]
        sev = emerging["severity"]

        return GeneratedInsight(
            insight_type="emerging_issue",
            title=f"Emerging Issue: {topic} Complaints Spike",
            description=(
                f"{topic} complaints have {'increased' if pct > 0 else 'decreased'} by "
                f"{abs(pct):.0f}% compared to the previous period."
            ),
            what_happened=(
                f"Reports mentioning '{topic}' increased from {prev} to {current} records "
                f"— a {pct:.0f}% {'surge' if pct > 100 else 'increase'}."
            ),
            why_it_matters=(
                f"A rapid increase in '{topic}' complaints may indicate a systemic issue "
                f"affecting multiple customers. Left unaddressed, this can escalate to "
                f"SLA breaches and customer churn."
            ),
            recommended_action=(
                f"Immediately investigate the root cause of {topic} complaints. "
                f"Assign an owner and establish a resolution timeline. "
                f"Consider proactive customer communication."
            ),
            severity=sev,
            confidence=0.78,
            entity_type="issue_category",
            entity_id=None,
            entity_name=topic,
            metric_name=f"{topic}_complaint_count",
            current_value=float(current),
            baseline_value=float(prev),
            change_pct=pct,
            evidence=[
                InsightEvidence(label="Current period count", value=current, source_type="ticket"),
                InsightEvidence(label="Previous period count", value=prev, source_type="ticket"),
                InsightEvidence(label="Change", value=f"+{pct:.0f}%", source_type="analytics"),
            ],
            contributing_factors=[f"Spike in {topic}-related reports"],
            financial_impact_estimate=None,
            affected_population=current,
            priority_score=0.0,
            is_cross_domain=False,
        )

    def generate_sla_risk_insight(
        self,
        ticket_id: str,
        customer_name: str,
        priority: str,
        elapsed_hours: float,
        sla_hours: float,
        breach_probability: float,
    ) -> Optional[GeneratedInsight]:
        if breach_probability < 0.5:
            return None

        time_remaining = sla_hours - elapsed_hours
        sev = "CRITICAL" if breach_probability > 0.85 else "HIGH"

        return GeneratedInsight(
            insight_type="sla_risk",
            title=f"SLA Breach Risk: Ticket {ticket_id}",
            description=(
                f"Ticket {ticket_id} for {customer_name} has {breach_probability*100:.0f}% "
                f"probability of SLA breach."
            ),
            what_happened=(
                f"Ticket {ticket_id} (Priority: {priority}) has been open for {elapsed_hours:.1f} hours. "
                f"SLA target is {sla_hours:.0f} hours, leaving {max(0, time_remaining):.1f} hours."
            ),
            why_it_matters=(
                f"An SLA breach for a {priority} ticket from {customer_name} could trigger "
                f"contract penalties and damage the customer relationship."
            ),
            recommended_action=(
                f"Immediately escalate ticket {ticket_id} to a senior engineer. "
                f"Notify {customer_name} proactively and provide an ETA."
            ),
            severity=sev,
            confidence=breach_probability,
            entity_type="ticket",
            entity_id=ticket_id,
            entity_name=ticket_id,
            metric_name="sla_breach_probability",
            current_value=breach_probability * 100,
            baseline_value=0.0,
            change_pct=breach_probability * 100,
            evidence=[
                InsightEvidence(label="Elapsed time", value=f"{elapsed_hours:.1f}h", source_type="ticket"),
                InsightEvidence(label="SLA target", value=f"{sla_hours:.0f}h", source_type="ticket"),
                InsightEvidence(label="Time remaining", value=f"{max(0, time_remaining):.1f}h", source_type="analytics"),
            ],
            contributing_factors=["Extended open time", f"{priority} priority"],
            financial_impact_estimate=None,
            affected_population=1,
            priority_score=0.0,
        )

    def run_full_analysis(
        self,
        customers: list[dict],
        tickets: list[dict],
        incidents: list[dict],
        feedback: list[dict],
    ) -> list[GeneratedInsight]:
        """
        Full insight generation pipeline.
        Returns prioritized list of insights.
        """
        insights: list[GeneratedInsight] = []

        # Customer health insights
        for customer in customers:
            health_result = self.risk_scorer.calculate_customer_health(
                ticket_count_30d=customer.get("ticket_count_30d", 0),
                ticket_count_prev=customer.get("ticket_count_prev_30d", 0),
                incident_count_30d=customer.get("incident_count_30d", 0),
                sla_breach_count=customer.get("sla_breach_count", 0),
                negative_sentiment_pct=customer.get("negative_pct", 0),
                avg_resolution_hours=customer.get("avg_resolution_hours", 0),
                contract_value=customer.get("contract_value", 0),
            )
            insight = self.generate_customer_health_insight(
                customer_name=customer.get("name", "Unknown"),
                customer_id=customer.get("id", ""),
                health_data=health_result,
                contract_value=customer.get("contract_value", 0),
            )
            if insight:
                insights.append(insight)

        # Emerging issue detection
        current_topics: dict[str, int] = {}
        prev_topics: dict[str, int] = {}
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        for ticket in tickets:
            for topic in ticket.get("topics", []):
                created = ticket.get("created_date")
                is_recent = True
                if created:
                    try:
                        d = datetime.fromisoformat(str(created)[:19]).replace(tzinfo=timezone.utc)
                        is_recent = d >= cutoff
                    except Exception:
                        pass
                if is_recent:
                    current_topics[topic] = current_topics.get(topic, 0) + 1
                else:
                    prev_topics[topic] = prev_topics.get(topic, 0) + 1

        emerging = self.emerging_issue_detector.detect(current_topics, prev_topics)
        for e in emerging[:5]:  # Top 5 emerging issues
            insights.append(self.generate_emerging_issue_insight(e))

        # Root cause analysis from incidents
        root_causes = self.root_cause_analyzer.analyze(incidents)
        for rc in root_causes[:3]:
            if rc["confidence"] > 0.6:
                insights.append(GeneratedInsight(
                    insight_type="root_cause",
                    title=f"Recurring Pattern: {rc['category']}",
                    description=(
                        f"{rc['incident_count']} incidents in category {rc['category']} "
                        f"with potential root cause: {rc['potential_root_cause']}"
                    ),
                    what_happened=(
                        f"{rc['incident_count']} incidents have occurred in the "
                        f"'{rc['category']}' category."
                    ),
                    why_it_matters=(
                        f"Recurring incidents in the same category suggest a systemic issue "
                        f"that simple reactive fixes cannot resolve."
                    ),
                    recommended_action=(
                        f"Conduct a root cause analysis session for {rc['category']}. "
                        f"{'Potential hypothesis: ' + rc['potential_root_cause'] if rc['potential_root_cause'] != 'Undetermined' else 'Insufficient evidence for hypothesis — gather more data.'}"
                    ),
                    severity="HIGH" if rc["incident_count"] >= 5 else "MEDIUM",
                    confidence=rc["confidence"],
                    entity_type="incident_category",
                    entity_id=None,
                    entity_name=rc["category"],
                    metric_name="incident_count",
                    current_value=float(rc["incident_count"]),
                    baseline_value=None,
                    change_pct=None,
                    evidence=[
                        InsightEvidence(
                            label="Total incidents",
                            value=rc["incident_count"],
                            source_type="incident",
                        ),
                        InsightEvidence(
                            label="Potential root cause",
                            value=f"{rc['potential_root_cause']} ({rc['rc_pct']}% of incidents) [HYPOTHESIS]",
                            source_type="analytics",
                        ),
                    ],
                    contributing_factors=[rc["potential_root_cause"] or "Unknown"],
                    financial_impact_estimate=None,
                    affected_population=rc["incident_count"],
                    priority_score=0.0,
                ))

        # Prioritize all
        return self.prioritizer.prioritize(insights)


# Singleton
insight_engine = InsightEngine()
