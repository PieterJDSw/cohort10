from __future__ import annotations

import json
import threading
import time
from time import perf_counter
from typing import Any, Callable

import pika

from app.config import settings
from app.crew.flow import evaluate_question, finalize_session
from app.db import SessionLocal, utc_now
from app.logging_config import bind_log_context, clear_log_context, get_logger
from app.messaging import declare_topology, publish_event
from app.metrics import agent_job_duration_seconds, agent_jobs_total
from app.models.session import TestSession
from app.models.session_question import SessionQuestion

logger = get_logger(__name__)

_threads: list[threading.Thread] = []
IN_FLIGHT_EVALUATION_STATUSES = {"evaluation_queued", "evaluating"}


def _lookup_with_retries(model, identifier: str, *, attempts: int = 3, delay_seconds: float = 1.0):
    db = SessionLocal()
    try:
        for attempt in range(1, attempts + 1):
            record = db.get(model, identifier)
            if record is not None:
                return record
            if attempt < attempts:
                db.rollback()
                time.sleep(delay_seconds)
        return None
    finally:
        db.close()


def _release_synthesis_if_ready(session_id: str) -> bool:
    db = SessionLocal()
    try:
        session = db.get(TestSession, session_id)
        if session is None or session.status != "synthesis_requested":
            return False

        if any(
            item.status in IN_FLIGHT_EVALUATION_STATUSES for item in session.session_questions
        ):
            return False

        session.status = "synthesis_queued"
        db.flush()
        published = publish_event(
            settings.rabbitmq_synthesis_queue,
            {
                "event_type": "session_synthesis_requested",
                "published_at": utc_now().isoformat(),
                "session_id": session_id,
            },
        )
        if not published:
            raise ValueError("Unable to publish synthesis request")
        db.commit()
        logger.info("synthesis_released", extra={"session_id": session_id})
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _mark_evaluation_failed(session_question_id: str) -> None:
    db = SessionLocal()
    try:
        session_question = db.get(SessionQuestion, session_question_id)
        if session_question is None:
            return

        session_question.status = "evaluation_failed"
        session = session_question.session
        if session is not None and session.status == "synthesis_requested":
            session.status = "synthesis_failed"
            session.completed_at = utc_now()
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _process_evaluate(payload: dict[str, Any]) -> None:
    session_question_id = str(payload.get("session_question_id") or "").strip()
    if not session_question_id:
        raise ValueError("evaluate payload missing session_question_id")

    session_question = _lookup_with_retries(SessionQuestion, session_question_id)
    if session_question is None:
        raise ValueError(f"session_question not found: {session_question_id}")

    db = SessionLocal()
    try:
        live_session_question = db.get(SessionQuestion, session_question_id)
        if live_session_question is None:
            raise ValueError(f"session_question not found: {session_question_id}")

        live_session_question.status = "evaluating"
        db.commit()

        try:
            evaluate_question(
                db,
                session_question_id,
                force=bool(payload.get("force", True)),
                publish_events=False,
                publish_dead_letters=False,
            )
            db.commit()
        except Exception:
            db.rollback()
            _mark_evaluation_failed(session_question_id)
            raise
    finally:
        db.close()

    _release_synthesis_if_ready(str(payload.get("session_id") or session_question.session_id))


def _process_synthesis(payload: dict[str, Any]) -> None:
    session_id = str(payload.get("session_id") or "").strip()
    if not session_id:
        raise ValueError("synthesis payload missing session_id")

    session = _lookup_with_retries(TestSession, session_id)
    if session is None:
        raise ValueError(f"session not found: {session_id}")

    status_db = SessionLocal()
    try:
        live_session = status_db.get(TestSession, session_id)
        if live_session is None:
            raise ValueError(f"session not found: {session_id}")

        live_session.status = "synthesizing"
        status_db.commit()
    finally:
        status_db.close()

    db = SessionLocal()
    try:
        live_session = db.get(TestSession, session_id)
        if live_session is None:
            raise ValueError(f"session not found: {session_id}")

        finalize_session(
            db,
            session_id,
            publish_events=False,
            publish_dead_letters=False,
        )

        live_session.status = "scored"
        live_session.completed_at = utc_now()
        db.commit()
    except Exception:
        db.rollback()
        failure_db = SessionLocal()
        try:
            failed_session = failure_db.get(TestSession, session_id)
            if failed_session is not None:
                failed_session.status = "synthesis_failed"
                failure_db.commit()
        finally:
            failure_db.close()
        raise
    finally:
        db.close()


def _handle_message(
    *,
    job_type: str,
    handler: Callable[[dict[str, Any]], None],
    channel: pika.adapters.blocking_connection.BlockingChannel,
    method,
    body: bytes,
) -> None:
    start = perf_counter()
    payload = json.loads(body.decode("utf-8"))
    bind_log_context(
        job_type=job_type,
        session_id=payload.get("session_id"),
        session_question_id=payload.get("session_question_id"),
    )
    logger.info("agent_job_started", extra={"job_type": job_type})
    try:
        handler(payload)
    except Exception:
        agent_jobs_total.labels(job_type=job_type, status="failure").inc()
        logger.exception("agent_job_failed", extra={"job_type": job_type})
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        raise
    else:
        duration = perf_counter() - start
        agent_jobs_total.labels(job_type=job_type, status="success").inc()
        agent_job_duration_seconds.labels(job_type=job_type).observe(duration)
        logger.info(
            "agent_job_completed",
            extra={"job_type": job_type, "duration_ms": round(duration * 1000, 2)},
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)
    finally:
        clear_log_context()


def _consumer_loop(job_type: str, queue_name: str, handler: Callable[[dict[str, Any]], None]) -> None:
    while True:
        connection: pika.BlockingConnection | None = None
        try:
            connection = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
            channel = connection.channel()
            declare_topology(channel)
            channel.basic_qos(prefetch_count=1)

            def callback(ch, method, properties, body):
                _handle_message(
                    job_type=job_type,
                    handler=handler,
                    channel=ch,
                    method=method,
                    body=body,
                )

            channel.basic_consume(queue=queue_name, on_message_callback=callback)
            logger.info(
                "agent_consumer_started",
                extra={"job_type": job_type, "queue_name": queue_name},
            )
            channel.start_consuming()
        except Exception:
            logger.exception("agent_consumer_crashed", extra={"job_type": job_type, "queue_name": queue_name})
            time.sleep(5)
        finally:
            if connection and connection.is_open:
                connection.close()


def start_consumers() -> None:
    if _threads:
        return

    mappings = [
        ("evaluate", f"assessment.{settings.rabbitmq_evaluate_queue}", _process_evaluate),
        ("synthesis", f"assessment.{settings.rabbitmq_synthesis_queue}", _process_synthesis),
    ]

    for job_type, queue_name, handler in mappings:
        thread = threading.Thread(
            target=_consumer_loop,
            args=(job_type, queue_name, handler),
            daemon=True,
            name=f"{job_type}-consumer",
        )
        thread.start()
        _threads.append(thread)
