from __future__ import annotations

from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.api.routes import ai, candidates, dashboard, results, sessions, submissions
from app.bootstrap import bootstrap_application
from app.config import settings
from app.logging_config import bind_log_context, clear_log_context, configure_logging, get_logger
from app.metrics import (
    http_request_duration_seconds,
    http_requests_in_progress,
    http_requests_total,
    metrics_payload,
)

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("application_starting", extra={"app_name": settings.app_name})
    bootstrap_application()
    yield
    logger.info("application_stopped", extra={"app_name": settings.app_name})


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://frontend:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(submissions.router, prefix="/api/sessions", tags=["submissions"])
app.include_router(ai.router, prefix="/api/sessions", tags=["ai"])
app.include_router(results.router, prefix="/api/sessions", tags=["results"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.middleware("http")
async def add_request_logging(request: Request, call_next) -> Response:
    request_id = request.headers.get("x-request-id") or str(uuid4())
    start = perf_counter()
    http_requests_in_progress.inc()
    bind_log_context(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )
    logger.info("request_started")
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((perf_counter() - start) * 1000, 2)
        route_path = request.scope.get("route").path if request.scope.get("route") else request.url.path
        http_request_duration_seconds.labels(request.method, route_path).observe(
            perf_counter() - start
        )
        http_requests_total.labels(request.method, route_path, "500").inc()
        http_requests_in_progress.dec()
        logger.exception("request_failed", extra={"duration_ms": duration_ms})
        clear_log_context()
        raise

    duration_ms = round((perf_counter() - start) * 1000, 2)
    route_path = request.scope.get("route").path if request.scope.get("route") else request.url.path
    http_request_duration_seconds.labels(request.method, route_path).observe(
        perf_counter() - start
    )
    http_requests_total.labels(request.method, route_path, str(response.status_code)).inc()
    http_requests_in_progress.dec()
    response.headers["x-request-id"] = request_id
    logger.info(
        "request_completed",
        extra={"status_code": response.status_code, "duration_ms": duration_ms},
    )
    clear_log_context()
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)
