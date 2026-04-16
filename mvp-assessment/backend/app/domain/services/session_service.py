from __future__ import annotations

from sqlalchemy.orm import Session

from app.crew.flow import finalize_session
from app.db import utc_now
from app.domain.repositories.candidate_repo import CandidateRepository
from app.domain.repositories.session_repo import SessionRepository
from app.domain.services.question_service import QuestionService
from app.logging_config import get_logger

logger = get_logger(__name__)


class SessionService:
    def __init__(self) -> None:
        self.candidate_repo = CandidateRepository()
        self.session_repo = SessionRepository()
        self.question_service = QuestionService()

    def create_candidate_and_session(self, db: Session, full_name: str):
        candidate = self.candidate_repo.create_candidate(db, full_name)
        session = self.session_repo.create_session(db, candidate.id, utc_now())
        self.question_service.build_default_question_plan(db, session.id)
        db.commit()
        db.refresh(session)
        logger.info(
            "session_created",
            extra={"candidate_id": candidate.id, "session_id": session.id},
        )
        return candidate, session

    def get_session_summary(self, db: Session, session_id: str) -> dict:
        session = self.session_repo.fetch_session(db, session_id)
        if not session:
            raise ValueError("Session not found")
        ordered = sorted(session.session_questions, key=lambda item: item.sequence_no)
        current = next(
            (item for item in ordered if item.status in {"active", "answered"}),
            None,
        )
        return {
            "session_id": session.id,
            "candidate_id": session.candidate_id,
            "candidate_name": session.candidate.full_name,
            "status": session.status,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "total_questions": len(ordered),
            "current_sequence": current.sequence_no if current else len(ordered),
        }

    def get_current_question(self, db: Session, session_id: str) -> dict | None:
        current, total = self.question_service.get_active_session_question(db, session_id)
        if not current:
            return None
        return {
            "session_question_id": current.id,
            "question_id": current.question_id,
            "type": current.question.type,
            "title": current.question.title,
            "prompt": current.question.prompt,
            "difficulty": current.question.difficulty,
            "sequence_no": current.sequence_no,
            "total_questions": total,
            "rubric": current.question.rubric_json,
            "metadata": current.question.metadata_json,
        }

    def advance_session(self, db: Session, session_id: str) -> dict | None:
        session = self.session_repo.fetch_session(db, session_id)
        if not session:
            raise ValueError("Session not found")
        ordered = sorted(session.session_questions, key=lambda item: item.sequence_no)
        current = next((item for item in ordered if item.status in {"active", "answered"}), None)
        if current:
            current.status = "completed"
        next_question = next((item for item in ordered if item.status == "pending"), None)
        if next_question:
            next_question.status = "active"
        db.commit()
        logger.info(
            "session_advanced",
            extra={
                "session_id": session_id,
                "next_session_question_id": next_question.id if next_question else None,
            },
        )
        return self.get_current_question(db, session_id)

    def finish_session(self, db: Session, session_id: str) -> dict:
        session = self.session_repo.fetch_session(db, session_id)
        if not session:
            raise ValueError("Session not found")
        logger.info("session_finish_started", extra={"session_id": session_id})
        for item in session.session_questions:
            if item.status in {"active", "answered"}:
                item.status = "completed"
        session.status = "submitted"
        db.flush()
        report = finalize_session(db, session_id)
        session.status = "scored"
        session.completed_at = utc_now()
        db.commit()
        logger.info(
            "session_finish_completed",
            extra={
                "session_id": session_id,
                "recommendation": report.get("recommendation"),
                "overall_score": report.get("overall_score"),
            },
        )
        return report
