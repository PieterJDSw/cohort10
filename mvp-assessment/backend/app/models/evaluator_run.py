from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, new_id


class EvaluatorRun(Base):
    __tablename__ = "evaluator_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_question_id: Mapped[str] = mapped_column(
        ForeignKey("session_questions.id"), nullable=False, index=True
    )
    evaluator_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="fallback")
    output_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    raw_output: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    session_question = relationship("SessionQuestion", back_populates="evaluator_runs")
