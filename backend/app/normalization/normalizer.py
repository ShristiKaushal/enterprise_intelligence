"""
Text normalization and cleaning pipeline.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Optional


class TextNormalizer:
    """Cleans and normalizes raw text extracted from documents."""

    # Common abbreviation expansions
    ABBREVIATIONS = {
        "vpn": "VPN",
        "sla": "SLA",
        "api": "API",
        "ui": "UI",
        "ux": "UX",
        "db": "database",
        "mgr": "manager",
        "dept": "department",
        "corp": "Corporation",
        "ltd": "Limited",
        "inc": "Incorporated",
        "pvt": "Private",
        "llc": "LLC",
    }

    def normalize_text(self, text: str) -> str:
        """Full text normalization pipeline."""
        if not text:
            return ""
        text = self._normalize_unicode(text)
        text = self._fix_whitespace(text)
        text = self._fix_line_breaks(text)
        return text.strip()

    def normalize_entity_name(self, name: str) -> str:
        """Normalize an entity name for matching/resolution."""
        if not name:
            return ""
        # Unicode normalize
        name = unicodedata.normalize("NFKD", name)
        name = name.encode("ascii", "ignore").decode("ascii")
        # Lower case
        name = name.lower()
        # Remove punctuation
        name = re.sub(r"[.,\/#!$%\^&\*;:{}=\-_`~()]", " ", name)
        # Remove legal suffixes
        legal_suffixes = [
            r"\bltd\b", r"\bllc\b", r"\binc\b", r"\bcorp\b", r"\bco\b",
            r"\bpvt\b", r"\blimited\b", r"\bcorporation\b", r"\bincorporated\b",
            r"\bplc\b", r"\bsa\b",
        ]
        for suffix in legal_suffixes:
            name = re.sub(suffix, "", name, flags=re.IGNORECASE)
        # Collapse whitespace
        name = re.sub(r"\s+", " ", name).strip()
        return name

    def normalize_date(self, date_str: str) -> Optional[str]:
        """Try to parse and normalize a date string to ISO format."""
        if not date_str:
            return None
        formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
            "%m-%d-%Y", "%B %d, %Y", "%b %d, %Y", "%d %B %Y",
            "%d %b %Y", "%Y/%m/%d",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def normalize_currency(self, value_str: str) -> Optional[dict]:
        """Parse currency strings into amount and currency code."""
        if not value_str:
            return None
        # Map symbols to codes
        symbol_map = {"$": "USD", "£": "GBP", "€": "EUR", "₹": "INR"}
        currency = "USD"
        for sym, code in symbol_map.items():
            if sym in value_str:
                currency = code
                break
        # Check for explicit codes
        for code in ["USD", "EUR", "GBP", "INR", "AUD", "CAD"]:
            if code in value_str.upper():
                currency = code
                break

        # Extract numeric part
        numeric = re.sub(r"[^\d.,]", "", value_str)
        numeric = numeric.replace(",", "")
        try:
            amount = float(numeric)
            return {"amount": amount, "currency": currency}
        except ValueError:
            return None

    def normalize_severity(self, severity: str) -> str:
        """Normalize severity to standard levels."""
        s = severity.lower().strip()
        mapping = {
            "p1": "critical", "priority 1": "critical", "sev1": "critical",
            "p2": "high", "priority 2": "high", "sev2": "high",
            "p3": "medium", "priority 3": "medium", "sev3": "medium",
            "p4": "low", "priority 4": "low", "sev4": "low",
            "urgent": "critical", "blocker": "critical",
            "major": "high", "critical": "critical",
            "moderate": "medium", "normal": "medium",
            "minor": "low", "trivial": "low",
        }
        return mapping.get(s, s if s in ["critical", "high", "medium", "low"] else "medium")

    def _normalize_unicode(self, text: str) -> str:
        return unicodedata.normalize("NFKD", text)

    def _fix_whitespace(self, text: str) -> str:
        # Normalize all whitespace to single spaces (preserve newlines)
        text = re.sub(r"[ \t]+", " ", text)
        return text

    def _fix_line_breaks(self, text: str) -> str:
        # Normalize CRLF
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse 3+ newlines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text


class IssueNormalizer:
    """
    Maps raw issue descriptions to canonical categories using taxonomy.
    """

    TAXONOMY = {
        "NETWORK": {
            "VPN": ["vpn", "remote access", "tunnel", "unable to connect to vpn", "vpn down"],
            "DNS": ["dns", "name resolution", "domain lookup"],
            "CONNECTIVITY": ["network down", "no internet", "connectivity issue", "packet loss"],
            "FIREWALL": ["firewall", "blocked", "port blocked"],
        },
        "APPLICATION": {
            "AUTHENTICATION": ["login", "password", "sso", "auth", "credentials", "mfa", "2fa"],
            "PERFORMANCE": ["slow", "lag", "timeout", "response time", "latency"],
            "CRASH": ["crash", "blue screen", "bsod", "application crash", "freeze"],
            "AVAILABILITY": ["down", "outage", "unavailable", "not accessible"],
        },
        "HARDWARE": {
            "PRINTER": ["printer", "print", "printing"],
            "DEVICE": ["laptop", "desktop", "workstation", "device"],
            "PERIPHERAL": ["keyboard", "mouse", "monitor", "headset"],
        },
        "DATA": {
            "BACKUP": ["backup", "restore", "recovery"],
            "STORAGE": ["storage", "disk full", "disk space", "quota"],
            "CORRUPTION": ["corrupt", "data loss", "missing data"],
        },
        "BILLING": {
            "INVOICE": ["invoice", "billing", "payment"],
            "REFUND": ["refund", "credit"],
            "SUBSCRIPTION": ["subscription", "renewal", "license"],
        },
        "SECURITY": {
            "BREACH": ["breach", "hack", "unauthorized", "intrusion"],
            "VULNERABILITY": ["vulnerability", "cve", "patch", "exploit"],
            "ACCESS": ["access denied", "permission", "unauthorized access"],
        },
    }

    def classify(self, text: str) -> tuple[str, str, float]:
        """
        Returns (category, subcategory, confidence).
        """
        text_lower = text.lower()
        best_cat = "GENERAL"
        best_sub = "OTHER"
        best_score = 0
        best_conf = 0.4

        for category, subcategories in self.TAXONOMY.items():
            for subcategory, patterns in subcategories.items():
                matches = sum(1 for p in patterns if p in text_lower)
                if matches > best_score:
                    best_score = matches
                    best_cat = category
                    best_sub = subcategory
                    best_conf = min(0.95, 0.65 + matches * 0.1)

        return best_cat, best_sub, best_conf


# Singletons
text_normalizer = TextNormalizer()
issue_normalizer = IssueNormalizer()
