from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge, Histogram, generate_latest

registry = CollectorRegistry()

http_requests_total = Counter(
    "assessment_http_requests_total",
    "Total HTTP requests processed by the API.",
    labelnames=("method", "path", "status_code"),
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "assessment_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    labelnames=("method", "path"),
    registry=registry,
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

http_requests_in_progress = Gauge(
    "assessment_http_requests_in_progress",
    "Current number of in-flight HTTP requests.",
    registry=registry,
)

question_evaluation_total = Counter(
    "assessment_question_evaluations_total",
    "Total completed question evaluations.",
    labelnames=("question_type", "source"),
    registry=registry,
)

question_evaluation_duration_seconds = Histogram(
    "assessment_question_evaluation_duration_seconds",
    "Question evaluation duration in seconds.",
    labelnames=("question_type",),
    registry=registry,
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
)

session_finalization_total = Counter(
    "assessment_session_finalizations_total",
    "Total completed session finalizations.",
    labelnames=("recommendation",),
    registry=registry,
)

session_finalization_duration_seconds = Histogram(
    "assessment_session_finalization_duration_seconds",
    "Session finalization duration in seconds.",
    registry=registry,
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
)

llm_requests_total = Counter(
    "assessment_llm_requests_total",
    "Total LLM requests made by the assessment backend.",
    labelnames=("operation", "status"),
    registry=registry,
)

agent_jobs_total = Counter(
    "assessment_agent_jobs_total",
    "Total agent-backend jobs processed from RabbitMQ.",
    labelnames=("job_type", "status"),
    registry=registry,
)

agent_job_duration_seconds = Histogram(
    "assessment_agent_job_duration_seconds",
    "Duration of agent-backend jobs processed from RabbitMQ.",
    labelnames=("job_type",),
    registry=registry,
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
)

strands_tokens_total = Counter(
    "assessment_strands_tokens_total",
    "Total Strands tokens consumed by agent executions.",
    labelnames=("agent_name",),
    registry=registry,
)

strands_duration_seconds = Histogram(
    "assessment_strands_duration_seconds",
    "Total Strands agent execution duration in seconds.",
    labelnames=("agent_name",),
    registry=registry,
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
)


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(registry), CONTENT_TYPE_LATEST


@contextmanager
def measure_question_evaluation(question_type: str) -> Iterator[None]:
    start = perf_counter()
    try:
        yield
    finally:
        question_evaluation_duration_seconds.labels(question_type=question_type).observe(
            perf_counter() - start
        )


@contextmanager
def measure_session_finalization() -> Iterator[None]:
    start = perf_counter()
    try:
        yield
    finally:
        session_finalization_duration_seconds.observe(perf_counter() - start)
