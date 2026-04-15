from __future__ import annotations

from app.config import settings
from app.migrate import run_migrations
from app.seed_questions import seed_questions_if_empty


def bootstrap_application() -> None:
    if settings.run_migrations_on_startup:
        run_migrations()
    if settings.seed_questions_on_startup:
        seed_questions_if_empty()
