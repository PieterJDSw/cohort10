from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from app.config import settings


def build_alembic_config() -> Config:
    backend_dir = Path(__file__).resolve().parents[1]
    config = Config()
    config.set_main_option("script_location", str(backend_dir / "app" / "migrations"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


def run_migrations() -> None:
    command.upgrade(build_alembic_config(), "head")
