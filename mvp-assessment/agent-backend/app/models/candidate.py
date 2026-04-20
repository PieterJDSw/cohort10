from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, new_id


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    sessions = relationship("TestSession", back_populates="candidate")
