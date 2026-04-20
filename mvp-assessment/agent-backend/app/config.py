from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


@dataclass(slots=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "MVP Assessment")
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://assessment_user:assessment_pass@localhost:5432/assessment_db",
    )
    llm_api_key: str = os.getenv("OPENAI_API_KEY", "local-vllm")
    llm_base_url: str = os.getenv("OPENAI_API_BASE", "http://localhost:8001/v1")
    model_name: str = os.getenv("MODEL_NAME", "google/gemma-4-E2B-it")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    run_migrations_on_startup: bool = os.getenv(
        "RUN_MIGRATIONS_ON_STARTUP", "true"
    ).lower() in {"1", "true", "yes", "on"}
    seed_questions_on_startup: bool = os.getenv(
        "SEED_QUESTIONS_ON_STARTUP", "true"
    ).lower() in {"1", "true", "yes", "on"}
    llm_enabled: bool = os.getenv("LLM_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    llm_tool_use_enabled: bool = os.getenv("LLM_TOOL_USE_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format: str = os.getenv("LOG_FORMAT", "json").lower()
    strands_log_level: str = os.getenv("STRANDS_LOG_LEVEL", "INFO").upper()
    rabbitmq_enabled: bool = os.getenv("RABBITMQ_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    rabbitmq_url: str = os.getenv(
        "RABBITMQ_URL", "amqp://assessment:assessment@rabbitmq:5672/%2f"
    )
    rabbitmq_exchange: str = os.getenv("RABBITMQ_EXCHANGE", "assessment.events")
    rabbitmq_dead_letter_exchange: str = os.getenv(
        "RABBITMQ_DEAD_LETTER_EXCHANGE", "assessment.events.dlx"
    )
    rabbitmq_evaluate_queue: str = os.getenv("RABBITMQ_EVALUATE_QUEUE", "evaluate")
    rabbitmq_synthesis_queue: str = os.getenv("RABBITMQ_SYNTHESIS_QUEUE", "synthesis")
    rabbitmq_dead_letter_queue: str = os.getenv(
        "RABBITMQ_DEAD_LETTER_QUEUE", "dead_letter"
    )


settings = Settings()
