"""
Full document processing pipeline — ingestion → extraction → normalization
→ entity resolution → analytics → insights.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.core.logging import get_logger
from app.database.session import get_db_context
from app.entity_resolution.resolver import entity_resolver
from app.extraction.provider_factory import get_provider
from app.ingestion.handlers import ingestion_registry
from app.models.core import (
    DimCustomer, DimService, FactTicket, FactIncident, FactFeedback,
    EntityResolutionLog, ProvenanceLink, ReviewQueueItem,
)
from app.models.document import ExtractedEntity, ProcessingJob, RawDocument, RawRecord
from app.normalization.normalizer import text_normalizer, issue_normalizer
from app.validation.quality_engine import data_quality_engine

logger = get_logger(__name__)


class DocumentProcessingPipeline:
    """
    End-to-end pipeline for a single document.
    Called by the task queue worker.
    """

    async def run(self, payload: dict) -> None:
        document_id = payload["document_id"]
        job_id = payload["job_id"]
        domain = payload.get("domain", "unknown")

        logger.info("Pipeline starting", document_id=document_id, domain=domain)

        async with get_db_context() as db:
            # Load document
            doc_result = await db.execute(
                select(RawDocument).where(RawDocument.id == uuid.UUID(document_id))
            )
            doc = doc_result.scalar_one_or_none()
            if not doc:
                logger.error("Document not found", document_id=document_id)
                return

            # Load job
            job_result = await db.execute(
                select(ProcessingJob).where(ProcessingJob.id == uuid.UUID(job_id))
            )
            job = job_result.scalar_one_or_none()

            try:
                # ── Step 1: Ingest ────────────────────────────────────────
                await self._update_job(db, job, "running", 5, "Ingesting file")
                doc.status = "processing"
                doc.processing_started_at = datetime.now(timezone.utc)

                handler = ingestion_registry.get_handler(doc.file_type)
                if not handler:
                    raise ValueError(f"No handler for file type: {doc.file_type}")

                ingestion_result = await handler.ingest(Path(doc.storage_path))
                if ingestion_result.error:
                    raise RuntimeError(f"Ingestion error: {ingestion_result.error}")

                doc.page_count = ingestion_result.total_pages
                doc.word_count = ingestion_result.total_words
                doc.doc_metadata = ingestion_result.metadata

                await self._update_job(db, job, "running", 20, "Ingestion complete")
                logger.info(
                    "File ingested",
                    doc_id=document_id,
                    pages=ingestion_result.total_pages,
                    words=ingestion_result.total_words,
                )

                # ── Step 2: Store raw records (CSV/Excel) ─────────────────
                if ingestion_result.raw_rows:
                    for i, row in enumerate(ingestion_result.raw_rows):
                        raw_rec = RawRecord(
                            document_id=uuid.UUID(document_id),
                            row_number=i + 1,
                            raw_data=row,
                        )
                        db.add(raw_rec)
                    await db.flush()
                    logger.info("Raw records stored", count=len(ingestion_result.raw_rows))

                # ── Step 3: AI extraction ─────────────────────────────────
                await self._update_job(db, job, "running", 35, "Running AI extraction")

                provider = get_provider()
                full_text = ingestion_result.full_text[:8000]  # Cap for AI

                extraction = await provider.extract_entities(
                    text=full_text,
                    document_id=document_id,
                    domain=domain,
                )

                doc.extraction_confidence = extraction.overall_confidence

                # ── Step 4: Store extracted entities ──────────────────────
                await self._update_job(db, job, "running", 55, "Storing entities")

                for ef in extraction.fields:
                    entity = ExtractedEntity(
                        document_id=uuid.UUID(document_id),
                        entity_type=ef.field,
                        field_name=ef.field,
                        raw_value=str(ef.value) if ef.value is not None else "",
                        confidence=ef.confidence,
                        extraction_method=ef.extraction_method,
                        model_version=ef.model_version,
                        source_page=ef.source_reference.page if ef.source_reference else None,
                        source_text_span=ef.source_reference.text_span if ef.source_reference else None,
                        char_start=ef.source_reference.char_start if ef.source_reference else None,
                        char_end=ef.source_reference.char_end if ef.source_reference else None,
                        domain=domain,
                        review_status="auto_accepted" if ef.confidence >= 0.75 else "pending_review",
                    )
                    db.add(entity)

                    # Flag low-confidence extractions for human review
                    if ef.confidence < 0.65:
                        review_item = ReviewQueueItem(
                            item_type="low_confidence_extraction",
                            document_id=uuid.UUID(document_id),
                            title=f"Low-confidence extraction: {ef.field}",
                            description=f"Field '{ef.field}' extracted with {ef.confidence:.0%} confidence",
                            current_value={"field": ef.field, "value": str(ef.value)},
                            confidence=ef.confidence,
                            priority="high" if ef.confidence < 0.5 else "medium",
                        )
                        db.add(review_item)

                for ent in extraction.entities:
                    entity = ExtractedEntity(
                        document_id=uuid.UUID(document_id),
                        entity_type=ent["type"],
                        field_name=ent["type"],
                        raw_value=str(ent.get("value", "")),
                        confidence=ent.get("confidence", 0.7),
                        extraction_method=extraction.extraction_method,
                        model_version=extraction.model_version,
                        domain=domain,
                        review_status="auto_accepted",
                    )
                    db.add(entity)

                await db.flush()

                # ── Step 5: Entity resolution + core table population ─────
                await self._update_job(db, job, "running", 70, "Resolving entities")
                await self._resolve_and_populate(db, doc, extraction, domain, document_id)
                await db.flush()

                # ── Step 6: Data quality ──────────────────────────────────
                await self._update_job(db, job, "running", 85, "Computing data quality")
                await self._compute_data_quality(db, doc, ingestion_result, domain, document_id)
                await db.flush()

                # ── Step 7: Done ──────────────────────────────────────────
                doc.status = "completed"
                doc.processing_completed_at = datetime.now(timezone.utc)
                await self._update_job(db, job, "completed", 100, "Pipeline complete",
                    result_summary={
                        "pages": ingestion_result.total_pages,
                        "words": ingestion_result.total_words,
                        "entities_extracted": len(extraction.entities) + len(extraction.fields),
                        "sentiment": extraction.sentiment,
                        "topics": extraction.topics,
                        "confidence": extraction.overall_confidence,
                    })

                logger.info("Pipeline completed successfully", doc_id=document_id)

            except Exception as e:
                import traceback as tb
                logger.error("Pipeline failed", doc_id=document_id, error=str(e))
                doc.status = "failed"
                doc.error_message = str(e)
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    job.error_traceback = tb.format_exc()
                    job.completed_at = datetime.now(timezone.utc)

    async def _update_job(
        self, db, job, status: str, progress: int, step: str,
        result_summary: dict | None = None,
    ) -> None:
        if not job:
            return
        job.status = status
        job.progress = progress
        job.current_step = step
        if status == "running" and not job.started_at:
            job.started_at = datetime.now(timezone.utc)
        if status in ("completed", "failed"):
            job.completed_at = datetime.now(timezone.utc)
            if job.started_at:
                job.duration_seconds = (
                    job.completed_at - job.started_at
                ).total_seconds()
        if result_summary:
            job.result_summary = result_summary
        await db.flush()

    async def _resolve_and_populate(
        self, db, doc: RawDocument, extraction, domain: str, document_id: str
    ) -> None:
        """Resolve entities and populate dimension/fact tables."""

        # Resolve customer entities
        customer_name = extraction.get_value("customer_name") or extraction.get_value("company")
        if not customer_name:
            for ent in extraction.entities:
                if ent["type"] in ("customer", "company"):
                    customer_name = ent["value"]
                    break

        if customer_name:
            decision = entity_resolver.resolve(customer_name, "customer")

            # Log resolution
            db.add(EntityResolutionLog(
                raw_value=customer_name,
                entity_type="customer",
                canonical_id=decision.canonical_id,
                canonical_name=decision.canonical_name,
                resolution_method=decision.resolution_method,
                confidence=decision.confidence,
                is_new_entity=decision.is_new_entity,
                requires_review=decision.requires_review,
                document_id=uuid.UUID(document_id),
            ))

            if decision.requires_review:
                db.add(ReviewQueueItem(
                    item_type="entity_resolution",
                    document_id=uuid.UUID(document_id),
                    title=f"Ambiguous entity: '{customer_name}'",
                    description=f"May match '{decision.canonical_name}' (confidence: {decision.confidence:.0%})",
                    current_value={"raw": customer_name},
                    suggested_value={"canonical_id": decision.canonical_id, "canonical_name": decision.canonical_name},
                    confidence=decision.confidence,
                    priority="medium",
                ))

            # Upsert dim_customer
            existing = await db.execute(
                select(DimCustomer).where(DimCustomer.canonical_id == decision.canonical_id)
            )
            if not existing.scalar_one_or_none():
                db.add(DimCustomer(
                    canonical_id=decision.canonical_id,
                    name=decision.canonical_name,
                    aliases=[customer_name] if customer_name != decision.canonical_name else [],
                    source_document_ids=[document_id],
                    resolution_confidence=decision.confidence,
                    is_active=True,
                ))

        # Populate fact tables based on domain
        if domain == "customer_intelligence":
            await self._populate_ticket(db, doc, extraction, customer_name, document_id)
        elif domain == "it_operations":
            await self._populate_incident(db, doc, extraction, document_id)

        # Always store feedback if sentiment found
        if extraction.sentiment:
            await self._populate_feedback(db, doc, extraction, customer_name, document_id)

    async def _populate_ticket(
        self, db, doc, extraction, customer_name: str | None, document_id: str
    ) -> None:
        """Create a FactTicket from extraction results."""
        ticket_num = extraction.get_value("ticket_number")
        if not ticket_num:
            ticket_num = f"TK-AUTO-{str(uuid.uuid4())[:8].upper()}"

        # Check for existing
        existing = await db.execute(
            select(FactTicket).where(FactTicket.ticket_number == ticket_num)
        )
        if existing.scalar_one_or_none():
            return

        # Get customer FK
        customer = None
        if customer_name:
            decision = entity_resolver.resolve(customer_name, "customer")
            c_res = await db.execute(
                select(DimCustomer).where(DimCustomer.canonical_id == decision.canonical_id)
            )
            customer = c_res.scalar_one_or_none()

        severity_raw = extraction.get_value("severity", "medium")
        category, subcategory, _ = issue_normalizer.classify(
            extraction.full_text if hasattr(extraction, 'full_text') else ""
        )

        ticket = FactTicket(
            ticket_number=ticket_num,
            source_document_id=uuid.UUID(document_id),
            customer_id=customer.id if customer else None,
            title=text_normalizer.normalize_text(
                extraction.get_value("issue_description", doc.original_filename)
            )[:500],
            priority=text_normalizer.normalize_severity(str(severity_raw)),
            severity=text_normalizer.normalize_severity(str(severity_raw)),
            status="open",
            category=category,
            subcategory=subcategory,
            sentiment=extraction.sentiment,
            sentiment_score=extraction.sentiment_score,
            tags=extraction.topics[:5] if extraction.topics else [],
            root_cause_category=subcategory,
            extraction_confidence=extraction.overall_confidence,
        )
        db.add(ticket)

    async def _populate_incident(
        self, db, doc, extraction, document_id: str
    ) -> None:
        """Create a FactIncident from extraction results."""
        inc_num = extraction.get_value("incident_number")
        if not inc_num:
            inc_num = f"INC-AUTO-{str(uuid.uuid4())[:8].upper()}"

        existing = await db.execute(
            select(FactIncident).where(FactIncident.incident_number == inc_num)
        )
        if existing.scalar_one_or_none():
            return

        severity_raw = extraction.get_value("severity", "medium")
        category, subcategory, _ = issue_normalizer.classify(
            extraction.get_value("issue_description", "") or ""
        )
        downtime = extraction.get_value("downtime_minutes")

        incident = FactIncident(
            incident_number=inc_num,
            source_document_id=uuid.UUID(document_id),
            title=text_normalizer.normalize_text(
                extraction.get_value("issue_description", doc.original_filename)
            )[:500],
            severity=text_normalizer.normalize_severity(str(severity_raw)),
            status="open",
            category=category,
            subcategory=subcategory,
            downtime_minutes=float(downtime) if downtime else None,
            root_cause_category=subcategory,
            sla_breached=False,
            extraction_confidence=extraction.overall_confidence,
        )
        db.add(incident)

    async def _populate_feedback(
        self, db, doc, extraction, customer_name: str | None, document_id: str
    ) -> None:
        """Create a FactFeedback entry."""
        customer = None
        if customer_name:
            decision = entity_resolver.resolve(customer_name, "customer")
            c_res = await db.execute(
                select(DimCustomer).where(DimCustomer.canonical_id == decision.canonical_id)
            )
            customer = c_res.scalar_one_or_none()

        feedback = FactFeedback(
            source_document_id=uuid.UUID(document_id),
            customer_id=customer.id if customer else None,
            feedback_type=doc.domain or "document",
            raw_text=(extraction.summary or "")[:2000],
            sentiment=extraction.sentiment,
            sentiment_score=extraction.sentiment_score,
            topics=extraction.topics,
            key_phrases=extraction.key_phrases[:10] if extraction.key_phrases else [],
            extraction_confidence=extraction.overall_confidence,
        )
        db.add(feedback)

    async def _compute_data_quality(
        self, db, doc, ingestion_result, domain: str, document_id: str
    ) -> None:
        from app.models.analytics import DataQualityReport
        records = ingestion_result.raw_rows if ingestion_result.raw_rows else []
        if not records:
            return

        result = data_quality_engine.evaluate(
            records=records,
            dataset_name=doc.original_filename,
            record_type=domain.replace("_intelligence", "").replace("it_", ""),
        )

        db.add(DataQualityReport(
            document_id=uuid.UUID(document_id),
            dataset_name=doc.original_filename,
            report_date=datetime.now(timezone.utc),
            overall_score=result.overall_score,
            completeness_score=result.completeness_score,
            validity_score=result.validity_score,
            consistency_score=result.consistency_score,
            uniqueness_score=result.uniqueness_score,
            total_records=result.total_records,
            valid_records=result.valid_records,
            invalid_records=result.invalid_records,
            duplicate_records=result.duplicate_records,
            missing_critical_fields=result.missing_critical_fields,
            records_requiring_review=result.records_requiring_review,
            issues=result.issues[:20],
        ))
