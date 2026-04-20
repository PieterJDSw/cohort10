from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, new_id


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_question_id: Mapped[str] = mapped_column(
        ForeignKey("session_questions.id"), nullable=False, index=True
    )
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    ai_response: Mapped[str] = mapped_column(Text, nullable=False)

    session_question = relationship("SessionQuestion", back_populates="ai_interactions")
