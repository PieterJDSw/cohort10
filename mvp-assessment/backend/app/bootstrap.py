from __future__ import annotations

from app.config import settings
from app.logging_config import get_logger
from app.migrate import run_migrations
from app.seed_questions import seed_questions_if_empty

logger = get_logger(__name__)


def bootstrap_application() -> None:
    if settings.run_migrations_on_startup:
        logger.info("bootstrap_run_migrations")
        run_migrations()
    if settings.seed_questions_on_startup:
        logger.info("bootstrap_seed_questions")
        seed_questions_if_empty()
