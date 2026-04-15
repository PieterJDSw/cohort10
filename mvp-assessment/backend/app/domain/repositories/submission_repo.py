from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.ai_interaction import AIInteraction
from app.models.evaluator_run import EvaluatorRun
from app.models.session_question import SessionQuestion
from app.models.submission import Submission


class SubmissionRepository:
    def save_text_answer(
        self, db: Session, session_question_id: str, answer: str
    ) -> Submission:
        submission = Submission(
            session_question_id=session_question_id,
            submission_type="text",
            text_answer=answer,
        )
        db.add(submission)
        db.flush()
        return submission

    def save_code_answer(
        self, db: Session, session_question_id: str, code: str, language: str
    ) -> Submission:
        submission = Submission(
            session_question_id=session_question_id,
            submission_type="code",
            code_answer=code,
            language=language,
        )
        db.add(submission)
        db.flush()
        return submission

    def fetch_latest_answer(
        self, db: Session, session_question_id: str, submission_type: str | None = None
    ) -> Submission | None:
        stmt = select(Submission).where(Submission.session_question_id == session_question_id)
        if submission_type:
            stmt = stmt.where(Submission.submission_type == submission_type)
        stmt = stmt.order_by(Submission.created_at.desc())
        return db.scalar(stmt)

    def fetch_submissions(self, db: Session, session_question_id: str) -> list[Submission]:
        stmt = (
            select(Submission)
            .where(Submission.session_question_id == session_question_id)
            .order_by(Submission.created_at.asc())
        )
        return list(db.scalars(stmt))

    def save_ai_interaction(
        self, db: Session, session_question_id: str, user_message: str, ai_response: str
    ) -> AIInteraction:
        interaction = AIInteraction(
            session_question_id=session_question_id,
            user_message=user_message,
            ai_response=ai_response,
        )
        db.add(interaction)
        db.flush()
        return interaction

    def fetch_ai_interactions(
        self, db: Session, session_question_id: str
    ) -> list[AIInteraction]:
        stmt = (
            select(AIInteraction)
            .where(AIInteraction.session_question_id == session_question_id)
            .order_by(AIInteraction.created_at.asc())
        )
        return list(db.scalars(stmt))

    def save_evaluator_output(
        self,
        db: Session,
        session_question_id: str,
        evaluator_type: str,
        source: str,
        output_json: dict,
        raw_output: str | None,
        error_message: str | None,
        confidence: float,
    ) -> EvaluatorRun:
        evaluator_run = EvaluatorRun(
            session_question_id=session_question_id,
            evaluator_type=evaluator_type,
            source=source,
            output_json=output_json,
            raw_output=raw_output,
            error_message=error_message,
            confidence=confidence,
        )
        db.add(evaluator_run)
        db.flush()
        return evaluator_run

    def fetch_evaluator_runs(
        self, db: Session, session_question_id: str
    ) -> list[EvaluatorRun]:
        stmt = (
            select(EvaluatorRun)
            .where(EvaluatorRun.session_question_id == session_question_id)
            .order_by(EvaluatorRun.created_at.asc())
        )
        return list(db.scalars(stmt))

    def fetch_latest_evaluator_run(
        self, db: Session, session_question_id: str
    ) -> EvaluatorRun | None:
        stmt = (
            select(EvaluatorRun)
            .where(EvaluatorRun.session_question_id == session_question_id)
            .order_by(EvaluatorRun.created_at.desc())
        )
        return db.scalar(stmt)

    def clear_evaluator_runs(self, db: Session, session_question_id: str) -> None:
        db.execute(
            delete(EvaluatorRun).where(EvaluatorRun.session_question_id == session_question_id)
        )

    def fetch_session_question(
        self, db: Session, session_question_id: str
    ) -> SessionQuestion | None:
        return db.get(SessionQuestion, session_question_id)
