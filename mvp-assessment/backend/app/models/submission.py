from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, new_id


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_question_id: Mapped[str] = mapped_column(
        ForeignKey("session_questions.id"), nullable=False, index=True
    )
    submission_type: Mapped[str] = mapped_column(String(32), nullable=False)
    text_answer: Mapped[str | None] = mapped_column(Text)
    code_answer: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(32))

    session_question = relationship("SessionQuestion", back_populates="submissions")
