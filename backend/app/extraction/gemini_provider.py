"""
GeminiProvider — Google Gemini Flash extraction with structured JSON output.
"""
from __future__ import annotations

import json
from typing import Optional

from app.extraction.base import (
    AIProvider,
    ExtractionField,
    ExtractionResult,
    SourceReference,
)
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

EXTRACTION_PROMPT = """
You are an enterprise data extraction system. Extract structured information from the following text.

Domain: {domain}
Document ID: {document_id}

TEXT:
{text}

Return ONLY valid JSON matching this schema:
{{
  "entities": [
    {{"type": "string", "value": "string", "confidence": 0.0-1.0}}
  ],
  "sentiment": "positive|negative|neutral",
  "sentiment_score": 0.0-1.0,
  "severity": "critical|high|medium|low|none",
  "category": "string",
  "subcategory": "string",
  "topics": ["string"],
  "key_phrases": ["string"],
  "summary": "string (max 200 chars)",
  "fields": [
    {{"field": "string", "value": "any", "confidence": 0.0-1.0, "text_span": "string|null"}}
  ]
}}

Rules:
- Only extract information explicitly present in the text
- Never invent values
- Set confidence based on how clearly the information appears in text
- For missing fields, omit them rather than guessing
"""

INSIGHT_NARRATIVE_PROMPT = """
You are a business intelligence assistant. Generate a professional, factual narrative for this insight.

Insight data:
{insight_json}

Rules:
- Stick strictly to the evidence provided
- Do not invent data points
- Label predictions clearly as "estimated" or "predicted"
- Keep it concise (3-5 sentences)
- Use business language

Return only the narrative text, no JSON.
"""


class GeminiProvider(AIProvider):
    """Google Gemini Flash provider with structured JSON output."""

    def __init__(self) -> None:
        self._client = None
        self._initialized = False

    def _get_client(self):
        if not self._initialized:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._client = genai.GenerativeModel(settings.GEMINI_MODEL)
                self._initialized = True
                logger.info("Gemini provider initialized", model=settings.GEMINI_MODEL)
            except Exception as e:
                logger.error("Failed to initialize Gemini", error=str(e))
                raise
        return self._client

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model_version(self) -> str:
        return settings.GEMINI_MODEL

    async def _call_gemini(self, prompt: str) -> str:
        """Make an async call to Gemini (runs in thread pool)."""
        import asyncio
        import functools
        client = self._get_client()
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            functools.partial(client.generate_content, prompt)
        )
        return response.text

    def _parse_extraction_response(self, raw: str, document_id: str, text: str) -> dict:
        """Parse JSON response from Gemini, with fallback."""
        # Strip markdown code fences if present
        clean = raw.strip()
        if clean.startswith("```"):
            clean = "\n".join(clean.split("\n")[1:-1])
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Try to find JSON object in response
            import re
            match = re.search(r'\{.*\}', clean, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
        logger.warning("Could not parse Gemini JSON response", document_id=document_id)
        return {}

    async def extract_entities(
        self,
        text: str,
        document_id: str,
        domain: str,
        context: Optional[dict] = None,
    ) -> ExtractionResult:
        prompt = EXTRACTION_PROMPT.format(
            domain=domain,
            document_id=document_id,
            text=text[:4000],  # Token limit
        )

        try:
            raw = await self._call_gemini(prompt)
            parsed = self._parse_extraction_response(raw, document_id, text)
        except Exception as e:
            logger.error("Gemini extraction failed", error=str(e), document_id=document_id)
            # Fallback to mock
            from app.extraction.mock_provider import MockProvider
            fallback = MockProvider()
            return await fallback.extract_entities(text, document_id, domain, context)

        ref = SourceReference(
            document_id=document_id,
            page=1,
            text_span=text[:200],
        )

        fields = []
        for f_data in parsed.get("fields", []):
            span = f_data.get("text_span")
            char_start = text.find(span) if span else None
            fields.append(ExtractionField(
                field=f_data.get("field", "unknown"),
                value=f_data.get("value"),
                confidence=float(f_data.get("confidence", 0.7)),
                source_reference=SourceReference(
                    document_id=document_id,
                    page=1,
                    text_span=span,
                    char_start=char_start,
                    char_end=char_start + len(span) if char_start and span else None,
                ),
                extraction_method="gemini",
                model_version=self.model_version,
            ))

        # Add sentiment field if not in fields
        if "sentiment" in parsed:
            fields.append(ExtractionField(
                field="sentiment",
                value=parsed["sentiment"],
                confidence=float(parsed.get("sentiment_score", 0.7)),
                source_reference=ref,
                extraction_method="gemini",
                model_version=self.model_version,
            ))

        entities = [
            {
                "type": e.get("type", "unknown"),
                "value": e.get("value", ""),
                "confidence": float(e.get("confidence", 0.7)),
            }
            for e in parsed.get("entities", [])
        ]

        overall_conf = (
            sum(f.confidence for f in fields) / len(fields) if fields else 0.7
        )

        return ExtractionResult(
            document_id=document_id,
            fields=fields,
            entities=entities,
            sentiment=parsed.get("sentiment"),
            sentiment_score=parsed.get("sentiment_score"),
            topics=parsed.get("topics", []),
            key_phrases=parsed.get("key_phrases", []),
            category=parsed.get("category"),
            subcategory=parsed.get("subcategory"),
            summary=parsed.get("summary"),
            overall_confidence=round(overall_conf, 2),
            extraction_method="gemini",
            model_version=self.model_version,
            raw_response=raw[:1000] if len(raw) > 1000 else raw,
        )

    async def classify_document(
        self, text: str, document_id: str, domain: str
    ) -> ExtractionResult:
        return await self.extract_entities(text, document_id, domain)

    async def analyze_sentiment(self, text: str, document_id: str) -> ExtractionResult:
        prompt = f"""
Analyze the sentiment of this text. Return JSON only:
{{"sentiment": "positive|negative|neutral", "sentiment_score": 0.0-1.0, "confidence": 0.0-1.0}}

TEXT: {text[:2000]}
"""
        try:
            raw = await self._call_gemini(prompt)
            parsed = self._parse_extraction_response(raw, document_id, text)
            sentiment = parsed.get("sentiment", "neutral")
            score = float(parsed.get("sentiment_score", 0.5))
            conf = float(parsed.get("confidence", 0.8))
        except Exception as e:
            logger.error("Gemini sentiment failed", error=str(e))
            sentiment, conf = "neutral", 0.5
            score = 0.5

        return ExtractionResult(
            document_id=document_id,
            fields=[
                ExtractionField(
                    field="sentiment", value=sentiment, confidence=conf,
                    extraction_method="gemini", model_version=self.model_version,
                )
            ],
            sentiment=sentiment,
            sentiment_score=score,
            overall_confidence=conf,
            extraction_method="gemini",
            model_version=self.model_version,
        )

    async def extract_topics(self, text: str, document_id: str) -> list[str]:
        prompt = f"""
Extract the top 5 topics from this text. Return JSON array of strings only.
TEXT: {text[:2000]}
"""
        try:
            raw = await self._call_gemini(prompt)
            clean = raw.strip().strip("```json").strip("```").strip()
            import json
            topics = json.loads(clean)
            return topics[:5] if isinstance(topics, list) else []
        except Exception:
            return []

    async def generate_insight_narrative(self, insight_data: dict) -> str:
        prompt = INSIGHT_NARRATIVE_PROMPT.format(
            insight_json=json.dumps(insight_data, default=str, indent=2)
        )
        try:
            return await self._call_gemini(prompt)
        except Exception as e:
            logger.error("Gemini narrative generation failed", error=str(e))
            return f"{insight_data.get('title', 'Insight detected')}. Review evidence for details."

    async def is_available(self) -> bool:
        if not settings.GEMINI_API_KEY:
            return False
        try:
            client = self._get_client()
            return client is not None
        except Exception:
            return False
