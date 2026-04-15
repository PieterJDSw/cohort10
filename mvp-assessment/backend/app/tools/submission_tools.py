from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.repositories.submission_repo import SubmissionRepository


class LoadSubmissionTool:
    def __init__(self) -> None:
        self.repo = SubmissionRepository()

    def run(self, db: Session, session_question_id: str):
        return self.repo.fetch_submissions(db, session_question_id)
