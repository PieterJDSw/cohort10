from __future__ import annotations

from typing import Any

from strands import tool
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.domain.repositories.question_repo import QuestionRepository
from app.models.session_question import SessionQuestion


def _serialize_question_evidence(session_question: SessionQuestion) -> dict[str, Any]:
    question = session_question.question
    latest_submission = next(
        (
            submission.code_answer or submission.text_answer or ""
            for submission in reversed(session_question.submissions)
        ),
        "",
    )

    return {
        "session_question_id": session_question.id,
        "session_id": session_question.session_id,
        "sequence_no": session_question.sequence_no,
        "status": session_question.status,
        "question_id": question.id if question else None,
        "question_type": question.type if question else None,
        "title": question.title if question else None,
        "prompt": question.prompt if question else None,
        "difficulty": question.difficulty if question else None,
        "rubric": question.rubric_json if question else {},
        "metadata": question.metadata_json if question else {},
        "latest_submission": latest_submission,
        "submissions": [
            {
                "submission_id": submission.id,
                "submission_type": submission.submission_type,
                "text_answer": submission.text_answer,
                "code_answer": submission.code_answer,
                "language": submission.language,
                "created_at": submission.created_at.isoformat(),
            }
            for submission in session_question.submissions
        ],
        "ai_interactions": [
            {
                "interaction_id": interaction.id,
                "user": interaction.user_message,
                "assistant": interaction.ai_response,
                "created_at": interaction.created_at.isoformat(),
            }
            for interaction in session_question.ai_interactions
        ],
        "evaluator_runs": [
            {
                "run_id": run.id,
                "evaluator_type": run.evaluator_type,
                "source": run.source,
                "confidence": run.confidence,
                "output_json": run.output_json,
                "raw_output": run.raw_output,
                "error_message": run.error_message,
                "created_at": run.created_at.isoformat(),
            }
            for run in session_question.evaluator_runs
        ],
    }


def _fetch_question_evidence(
    db: Session,
    session_question_id: str,
) -> SessionQuestion | None:
    stmt = (
        select(SessionQuestion)
        .options(
            joinedload(SessionQuestion.question),
            joinedload(SessionQuestion.submissions),
            joinedload(SessionQuestion.ai_interactions),
            joinedload(SessionQuestion.evaluator_runs),
        )
        .where(SessionQuestion.id == session_question_id)
    )
    return db.execute(stmt).unique().scalar_one_or_none()


class LoadQuestionTool:
    def __init__(self) -> None:
        self.repo = QuestionRepository()

    def run(self, db: Session, question_id: str):
        return self.repo.fetch_question_by_id(db, question_id)


def build_load_question_evidence_tool(*, db: Session, session_question_id: str):
    current_session_question_id = session_question_id

    @tool
    def load_question_evidence_tool(
        target_session_question_id: str | None = None,
    ) -> dict[str, Any]:
        """Load prompt, rubric, submission, helper transcript, and evaluator outputs for the given session question."""
        resolved_session_question_id = (
            target_session_question_id or current_session_question_id
        )
        session_question = _fetch_question_evidence(db, resolved_session_question_id)
        if session_question is None:
            return {
                "error": (
                    f"Session question {resolved_session_question_id} was not found."
                )
            }
        return _serialize_question_evidence(session_question)

    return load_question_evidence_tool
