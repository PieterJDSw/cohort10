from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, new_id


class TestSession(Base):
    __tablename__ = "test_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), default="in_progress", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    candidate = relationship("Candidate", back_populates="sessions")
    session_questions = relationship(
        "SessionQuestion", back_populates="session", cascade="all, delete-orphan"
    )
    dimension_scores = relationship(
        "DimensionScore", back_populates="session", cascade="all, delete-orphan"
    )
    final_report = relationship(
        "FinalReport", back_populates="session", cascade="all, delete-orphan", uselist=False
    )
