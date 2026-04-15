from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, new_id


class SessionQuestion(Base):
    __tablename__ = "session_questions"
    __table_args__ = (UniqueConstraint("session_id", "sequence_no", name="uq_session_sequence"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("test_sessions.id"), nullable=False, index=True
    )
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id"), nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)

    session = relationship("TestSession", back_populates="session_questions")
    question = relationship("Question", back_populates="session_questions")
    submissions = relationship(
        "Submission", back_populates="session_question", cascade="all, delete-orphan"
    )
    ai_interactions = relationship(
        "AIInteraction", back_populates="session_question", cascade="all, delete-orphan"
    )
    evaluator_runs = relationship(
        "EvaluatorRun", back_populates="session_question", cascade="all, delete-orphan"
    )
