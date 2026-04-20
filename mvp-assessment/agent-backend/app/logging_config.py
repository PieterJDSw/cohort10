from __future__ import annotations

import contextvars
import json
import logging
from datetime import datetime, timezone
from logging.config import dictConfig
from typing import Any

from app.config import settings

_log_context: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "log_context", default={}
)
_reserved_fields = set(logging.makeLogRecord({}).__dict__.keys())


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def bind_log_context(**values: Any) -> None:
    context = dict(_log_context.get())
    context.update({key: value for key, value in values.items() if value is not None})
    _log_context.set(context)


def clear_log_context() -> None:
    _log_context.set({})


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": _utc_timestamp(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        context = getattr(record, "context", None) or {}
        if context:
            payload["context"] = context

        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _reserved_fields
            and key not in {"message", "asctime", "context"}
        }
        if extra_fields:
            payload["extra"] = extra_fields

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str, ensure_ascii=True)


def _context_record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
    record = _default_record_factory(*args, **kwargs)
    record.context = dict(_log_context.get())
    return record


def configure_logging() -> None:
    formatter_name = settings.log_format if settings.log_format in {"json", "plain"} else "json"
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "app.logging_config.JsonFormatter",
                },
                "plain": {
                    "format": (
                        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
                    ),
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": formatter_name,
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {
                "level": settings.log_level,
                "handlers": ["default"],
            },
            "loggers": {
                "uvicorn": {"level": settings.log_level, "handlers": ["default"], "propagate": False},
                "uvicorn.error": {"level": settings.log_level, "handlers": ["default"], "propagate": False},
                "uvicorn.access": {"level": settings.log_level, "handlers": ["default"], "propagate": False},
                "strands": {
                    "level": settings.strands_log_level,
                    "handlers": ["default"],
                    "propagate": False,
                },
            },
        }
    )
    logging.setLogRecordFactory(_context_record_factory)


_default_record_factory = logging.getLogRecordFactory()
