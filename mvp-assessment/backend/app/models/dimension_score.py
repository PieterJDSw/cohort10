from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, new_id


class DimensionScore(Base):
    __tablename__ = "dimension_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("test_sessions.id"), nullable=False, index=True
    )
    dimension_name: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    session = relationship("TestSession", back_populates="dimension_scores")
