from __future__ import annotations

from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.responses import Response

from app.bootstrap import bootstrap_application
from app.config import settings
from app.consumer import start_consumers
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
    logger.info("agent_backend_starting", extra={"app_name": settings.app_name})
    bootstrap_application()
    start_consumers()
    yield
    logger.info("agent_backend_stopped", extra={"app_name": settings.app_name})


app = FastAPI(title=settings.app_name, lifespan=lifespan)


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
        duration = perf_counter() - start
        route_path = request.scope.get("route").path if request.scope.get("route") else request.url.path
        http_request_duration_seconds.labels(request.method, route_path).observe(duration)
        http_requests_total.labels(request.method, route_path, "500").inc()
        http_requests_in_progress.dec()
        logger.exception("request_failed", extra={"duration_ms": round(duration * 1000, 2)})
        clear_log_context()
        raise

    duration = perf_counter() - start
    route_path = request.scope.get("route").path if request.scope.get("route") else request.url.path
    http_request_duration_seconds.labels(request.method, route_path).observe(duration)
    http_requests_total.labels(request.method, route_path, str(response.status_code)).inc()
    http_requests_in_progress.dec()
    response.headers["x-request-id"] = request_id
    logger.info(
        "request_completed",
        extra={"status_code": response.status_code, "duration_ms": round(duration * 1000, 2)},
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

