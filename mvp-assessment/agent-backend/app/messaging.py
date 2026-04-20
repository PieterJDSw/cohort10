from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pika

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _queue_name(name: str) -> str:
    return f"assessment.{name}"


def _declare_topology(channel: pika.adapters.blocking_connection.BlockingChannel) -> None:
    channel.exchange_declare(
        exchange=settings.rabbitmq_exchange,
        exchange_type="direct",
        durable=True,
    )
    channel.exchange_declare(
        exchange=settings.rabbitmq_dead_letter_exchange,
        exchange_type="direct",
        durable=True,
    )

    channel.queue_declare(queue=_queue_name(settings.rabbitmq_dead_letter_queue), durable=True)
    channel.queue_bind(
        exchange=settings.rabbitmq_dead_letter_exchange,
        queue=_queue_name(settings.rabbitmq_dead_letter_queue),
        routing_key=settings.rabbitmq_dead_letter_queue,
    )

    for queue_name in (
        settings.rabbitmq_evaluate_queue,
        settings.rabbitmq_synthesis_queue,
    ):
        channel.queue_declare(
            queue=_queue_name(queue_name),
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.rabbitmq_dead_letter_exchange,
                "x-dead-letter-routing-key": settings.rabbitmq_dead_letter_queue,
            },
        )
        channel.queue_bind(
            exchange=settings.rabbitmq_exchange,
            queue=_queue_name(queue_name),
            routing_key=queue_name,
        )


def declare_topology(channel: pika.adapters.blocking_connection.BlockingChannel) -> None:
    _declare_topology(channel)


def _message_properties(message_type: str) -> pika.BasicProperties:
    return pika.BasicProperties(
        content_type="application/json",
        delivery_mode=2,
        type=message_type,
        timestamp=int(datetime.now(timezone.utc).timestamp()),
    )


def publish_event(queue_name: str, payload: dict[str, Any]) -> bool:
    if not settings.rabbitmq_enabled:
        return False

    connection: pika.BlockingConnection | None = None
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
        channel = connection.channel()
        _declare_topology(channel)
        channel.basic_publish(
            exchange=settings.rabbitmq_exchange,
            routing_key=queue_name,
            body=json.dumps(payload, default=str, ensure_ascii=True),
            properties=_message_properties(queue_name),
        )
        return True
    except Exception:
        logger.exception(
            "rabbitmq_publish_failed",
            extra={"queue_name": queue_name, "payload_type": payload.get("event_type")},
        )
        return False
    finally:
        if connection and connection.is_open:
            connection.close()


def publish_dead_letter(reason: str, payload: dict[str, Any]) -> bool:
    if not settings.rabbitmq_enabled:
        return False

    envelope = {
        "event_type": "dead_letter",
        "failed_at": _utc_timestamp(),
        "reason": reason,
        "payload": payload,
    }

    connection: pika.BlockingConnection | None = None
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
        channel = connection.channel()
        _declare_topology(channel)
        channel.basic_publish(
            exchange=settings.rabbitmq_dead_letter_exchange,
            routing_key=settings.rabbitmq_dead_letter_queue,
            body=json.dumps(envelope, default=str, ensure_ascii=True),
            properties=_message_properties("dead_letter"),
        )
        return True
    except Exception:
        logger.exception(
            "rabbitmq_dead_letter_publish_failed",
            extra={"reason": reason, "payload_type": payload.get("event_type")},
        )
        return False
    finally:
        if connection and connection.is_open:
            connection.close()
