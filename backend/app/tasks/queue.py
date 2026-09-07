"""
In-process async task queue for local development.
Redis+Celery adapter ready for production.
"""
from __future__ import annotations

import asyncio
import traceback
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class InMemoryTaskQueue:
    """
    Simple asyncio-based task queue.
    Runs tasks in the background within the same process.
    Replace with Redis+Celery for production scale.

    NOTE: _queue is created lazily inside `start()` to avoid
    'no running event loop' errors when the instance is constructed
    at module import time (before uvicorn's event loop starts).
    """

    def __init__(self) -> None:
        self._queue: Optional[asyncio.Queue] = None  # created lazily in start()
        self._handlers: Dict[str, Callable] = {}
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

    def register(self, task_name: str, handler: Callable) -> None:
        self._handlers[task_name] = handler
        logger.debug("Task handler registered", task=task_name)

    async def enqueue(self, task_name: str, payload: dict) -> str:
        if self._queue is None:
            # Queue not started yet — create it now (we're inside an event loop)
            self._queue = asyncio.Queue()
        task_id = f"{task_name}_{datetime.now(timezone.utc).timestamp()}"
        await self._queue.put({"id": task_id, "name": task_name, "payload": payload})
        logger.info("Task enqueued", task_id=task_id, task_name=task_name)
        return task_id

    async def start(self) -> None:
        """Call from FastAPI lifespan — creates the queue inside the event loop."""
        self._queue = asyncio.Queue()
        self._running = True
        # Register all available handlers
        _register_handlers(self)
        self._worker_task = asyncio.create_task(self._worker())
        logger.info("Task queue worker started")

    async def stop(self) -> None:
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Task queue worker stopped")

    async def _worker(self) -> None:
        while self._running:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._execute(task)
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Task worker error", error=str(e))

    async def _execute(self, task: dict) -> None:
        task_id = task["id"]
        task_name = task["name"]
        payload = task["payload"]

        handler = self._handlers.get(task_name)
        if not handler:
            logger.warning("No handler for task", task_name=task_name)
            return

        logger.info("Executing task", task_id=task_id, task_name=task_name)
        try:
            await handler(payload)
            logger.info("Task completed", task_id=task_id)
        except Exception as e:
            logger.error(
                "Task failed",
                task_id=task_id,
                task_name=task_name,
                error=str(e),
                traceback=traceback.format_exc(),
            )


def _register_handlers(queue: InMemoryTaskQueue) -> None:
    """
    Register all task handlers. Each handler is imported lazily
    so missing pipeline modules don't break startup.
    """
    # Document processing pipeline
    try:
        from app.pipelines.document_pipeline import DocumentProcessingPipeline
        pipeline = DocumentProcessingPipeline()
        queue.register("process_document", pipeline.run)
        logger.info("Registered handler: process_document")
    except ImportError:
        logger.warning(
            "DocumentProcessingPipeline not available — 'process_document' task will be a no-op"
        )
        async def _noop_process(payload: dict) -> None:
            logger.warning("process_document handler not implemented yet", payload=payload)
        queue.register("process_document", _noop_process)

    # Analytics refresh
    try:
        from app.pipelines.analytics_pipeline import AnalyticsPipeline
        analytics = AnalyticsPipeline()
        queue.register("refresh_analytics", analytics.run)
        logger.info("Registered handler: refresh_analytics")
    except ImportError:
        async def _noop_analytics(payload: dict) -> None:
            logger.warning("refresh_analytics handler not implemented yet", payload=payload)
        queue.register("refresh_analytics", _noop_analytics)

    # Insight generation
    try:
        from app.pipelines.insight_pipeline import InsightPipeline
        insight = InsightPipeline()
        queue.register("generate_insights", insight.run)
        logger.info("Registered handler: generate_insights")
    except ImportError:
        async def _noop_insights(payload: dict) -> None:
            logger.warning("generate_insights handler not implemented yet", payload=payload)
        queue.register("generate_insights", _noop_insights)


# Singleton — queue created here but .start() must be called inside event loop
task_queue = InMemoryTaskQueue()
