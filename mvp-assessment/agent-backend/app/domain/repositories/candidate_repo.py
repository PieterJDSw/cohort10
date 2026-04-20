from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate import Candidate


class CandidateRepository:
    def create_candidate(self, db: Session, full_name: str) -> Candidate:
        candidate = Candidate(full_name=full_name.strip())
        db.add(candidate)
        db.flush()
        return candidate

    def fetch_candidate(self, db: Session, candidate_id: str) -> Candidate | None:
        return db.scalar(select(Candidate).where(Candidate.id == candidate_id))
