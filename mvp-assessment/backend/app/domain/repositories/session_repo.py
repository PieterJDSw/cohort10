from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.session import TestSession
from app.models.session_question import SessionQuestion


class SessionRepository:
    def create_session(
        self, db: Session, candidate_id: str, started_at: datetime
    ) -> TestSession:
        session = TestSession(candidate_id=candidate_id, started_at=started_at)
        db.add(session)
        db.flush()
        return session

    def fetch_session(self, db: Session, session_id: str) -> TestSession | None:
        stmt = (
            select(TestSession)
            .options(
                joinedload(TestSession.candidate),
                joinedload(TestSession.session_questions).joinedload(
                    SessionQuestion.question
                ),
                joinedload(TestSession.final_report),
                joinedload(TestSession.dimension_scores),
            )
            .where(TestSession.id == session_id)
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    def fetch_session_for_audit(self, db: Session, session_id: str) -> TestSession | None:
        stmt = (
            select(TestSession)
            .options(
                joinedload(TestSession.candidate),
                joinedload(TestSession.final_report),
                joinedload(TestSession.dimension_scores),
                joinedload(TestSession.session_questions).joinedload(SessionQuestion.question),
                joinedload(TestSession.session_questions).joinedload(SessionQuestion.submissions),
                joinedload(TestSession.session_questions).joinedload(
                    SessionQuestion.ai_interactions
                ),
                joinedload(TestSession.session_questions).joinedload(
                    SessionQuestion.evaluator_runs
                ),
            )
            .where(TestSession.id == session_id)
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    def update_session_status(
        self,
        db: Session,
        session: TestSession,
        status: str,
        completed_at: datetime | None = None,
    ) -> TestSession:
        session.status = status
        session.completed_at = completed_at
        db.add(session)
        db.flush()
        return session

    def list_sessions(self, db: Session) -> list[TestSession]:
        stmt = (
            select(TestSession)
            .options(
                joinedload(TestSession.candidate),
                joinedload(TestSession.final_report),
                joinedload(TestSession.dimension_scores),
            )
            .order_by(TestSession.started_at.desc())
        )
        return list(db.scalars(stmt).unique())
