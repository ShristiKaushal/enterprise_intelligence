"""
FastAPI application entry point.
"""
from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.database.session import check_db_connection

configure_logging()
logger = get_logger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info(
        "Starting Enterprise Intelligence Platform",
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
        ai_provider=settings.AI_PROVIDER,
    )

    db_ok = await check_db_connection()
    if not db_ok:
        logger.warning("Database not reachable at startup — some features may be unavailable")
    else:
        logger.info("Database connection verified")
        try:
            from app.database.session import init_db_tables_and_users
            await init_db_tables_and_users()
        except Exception as e:
            logger.error("Failed to auto-create tables on startup", error=str(e))

    from app.tasks.queue import task_queue
    await task_queue.start()
    logger.info("Task queue started")

    yield

    await task_queue.stop()
    logger.info("Enterprise Intelligence Platform shutting down")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Unstructured Data Intelligence Platform API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
import re as _re

_CORS_ALLOW_REGEX = _re.compile(
    r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    r"|^https://[\w-]+\.vercel\.app$"
    r"|^https://[\w-]+\.railway\.app$"
)


class PermissiveCORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware that injects Access-Control headers on EVERY response,
    including 4xx/5xx, so browser errors don't masquerade as CORS failures."""

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "")
        allowed = (
            origin in settings.CORS_ORIGINS
            or bool(_CORS_ALLOW_REGEX.match(origin))
        )

        # Preflight
        if request.method == "OPTIONS":
            req_headers = request.headers.get("access-control-request-headers", "*")
            allow_origin = origin if allowed else (origin or "*")
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": allow_origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": req_headers or "*",
                    "Access-Control-Max-Age": "86400",
                },
            )

        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            logger.error("Unhandled exception in request", error=str(exc))
            detail = str(exc) if (settings.APP_DEBUG or settings.APP_ENV != "production") else "Internal server error"
            response = JSONResponse(
                status_code=500,
                content={"detail": detail},
            )

        if allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response


app.add_middleware(PermissiveCORSMiddleware)


# ── Global 500 handler (adds CORS headers) ────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in settings.CORS_ORIGINS or bool(_CORS_ALLOW_REGEX.match(origin)):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    detail = str(exc) if (settings.APP_DEBUG or settings.APP_ENV != "production") else "Internal server error"
    return JSONResponse(
        status_code=500,
        content={"detail": detail},
        headers=headers,
    )


# ── Request ID middleware ─────────────────────────────────────────────────────
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    import structlog
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration:.3f}s"

    logger.info(
        "HTTP request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 1),
    )
    return response


# ── Health endpoints ──────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    db_ok = await check_db_connection()
    db_target = settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "not_configured"
    return {
        "status": "healthy" if db_ok else "degraded",
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "ai_provider": settings.AI_PROVIDER,
        "database": "connected" if db_ok else "unreachable",
        "database_target": db_target,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }


# ── Router registration (safe — missing modules fall back to stub) ─────────────

API_PREFIX = "/api/v1"


def _stub_router(prefix: str, tag: str) -> APIRouter:
    """Return a stub router that responds 501 for all paths."""
    r = APIRouter()

    @r.get("", tags=[tag])
    async def _not_implemented():
        return {"detail": f"{tag} API coming soon", "status": 501}

    return r


def _safe_include(router_module: str, attr: str, prefix: str, tag: str) -> None:
    """Import a router module safely; fall back to stub on ImportError."""
    try:
        import importlib
        mod = importlib.import_module(router_module)
        router = getattr(mod, attr)
        app.include_router(router, prefix=f"{API_PREFIX}/{prefix}", tags=[tag])
        logger.debug("Router registered", module=router_module, prefix=prefix)
    except (ImportError, AttributeError) as e:
        logger.warning(
            "Router not available — using stub",
            module=router_module,
            prefix=prefix,
            error=str(e),
        )
        stub = _stub_router(prefix, tag)
        app.include_router(stub, prefix=f"{API_PREFIX}/{prefix}", tags=[tag])


# Always-available routers
from app.api.v1.auth import router as _auth_router
app.include_router(_auth_router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])

from app.api.v1.documents import router as _docs_router
app.include_router(_docs_router, prefix=f"{API_PREFIX}/documents", tags=["Documents"])

# Lazy / progressive routers
_safe_include("app.api.v1.processing", "router", "jobs", "Processing Jobs")
_safe_include("app.api.v1.customers", "router", "customers", "Customers")
_safe_include("app.api.v1.incidents", "router", "incidents", "Incidents")
_safe_include("app.api.v1.analytics", "router", "analytics", "Analytics")
_safe_include("app.api.v1.insights", "router", "insights", "Insights")
_safe_include("app.api.v1.anomalies", "router", "anomalies", "Anomalies")
_safe_include("app.api.v1.data_quality", "router", "data-quality", "Data Quality")
_safe_include("app.api.v1.query", "router", "query", "NL Query")
_safe_include("app.api.v1.review", "router", "review", "Review Queue")
_safe_include("app.api.v1.settings", "router", "settings", "Settings")
