from __future__ import annotations

from typing import Any

from strands import tool
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.domain.repositories.session_repo import SessionRepository
from app.models.dimension_score import DimensionScore
from app.models.session import TestSession
from app.models.session_question import SessionQuestion


def _serialize_session_evidence(session) -> dict[str, Any]:
    report = getattr(session, "final_report", None)
    dimension_scores = getattr(session, "dimension_scores", None) or []
    session_questions = getattr(session, "session_questions", None) or []

    return {
        "session_id": session.id,
        "status": session.status,
        "candidate_name": (
            session.candidate.full_name
            if getattr(session, "candidate", None) is not None
            else None
        ),
        "dimension_scores": [
            {
                "dimension_name": item.dimension_name,
                "score": item.score,
                "confidence": item.confidence,
                "evidence_json": item.evidence_json,
            }
            for item in dimension_scores
        ],
        "final_report": (
            {
                "recommendation": report.recommendation,
                "summary": report.summary,
                "source": report.source,
            }
            if report is not None
            else None
        ),
        "questions": [
            {
                "session_question_id": item.id,
                "sequence_no": item.sequence_no,
                "question_type": item.question.type if item.question else None,
                "title": item.question.title if item.question else None,
                "prompt": item.question.prompt if item.question else None,
                "latest_submission": next(
                    (
                        submission.code_answer or submission.text_answer or ""
                        for submission in reversed(item.submissions)
                    ),
                    "",
                ),
                "ai_interactions": [
                    {
                        "user": interaction.user_message,
                        "assistant": interaction.ai_response,
                    }
                    for interaction in item.ai_interactions
                ],
                "evaluator_runs": [
                    {
                        "evaluator_name": run.evaluator_name,
                        "source": run.source,
                        "confidence": run.confidence,
                        "output_json": run.output_json,
                        "raw_output": run.raw_output,
                        "error_message": run.error_message,
                    }
                    for run in item.evaluator_runs
                ],
            }
            for item in sorted(session_questions, key=lambda row: row.sequence_no)
        ],
    }


class LoadSessionEvidenceTool:
    def __init__(self) -> None:
        self.repo = SessionRepository()

    def run(self, db: Session, session_id: str):
        return self.repo.fetch_session(db, session_id)


def build_load_session_evidence_tool(*, db: Session, session_id: str):
    repo = SessionRepository()
    current_session_id = session_id

    @tool
    def load_session_evidence_tool(target_session_id: str | None = None) -> dict[str, Any]:
        """Load structured evidence for the given session or the active session when no id is provided."""
        resolved_session_id = target_session_id or current_session_id
        session = repo.fetch_session_for_audit(db, resolved_session_id)
        if session is None:
            return {"error": f"Session {resolved_session_id} was not found."}
        return _serialize_session_evidence(session)

    return load_session_evidence_tool


def _fetch_session_coding_transcript(
    db: Session, session_id: str
) -> TestSession | None:
    stmt = (
        select(TestSession)
        .options(
            joinedload(TestSession.session_questions)
            .joinedload(SessionQuestion.question),
            joinedload(TestSession.session_questions)
            .joinedload(SessionQuestion.ai_interactions),
        )
        .where(TestSession.id == session_id)
    )
    return db.execute(stmt).unique().scalar_one_or_none()


def _serialize_coding_ai_transcript(session: TestSession) -> dict[str, Any]:
    coding_questions = [
        item
        for item in sorted(session.session_questions, key=lambda row: row.sequence_no)
        if item.question and item.question.type == "coding"
    ]
    transcript_items: list[dict[str, Any]] = []
    transcript_lines: list[str] = []

    for question in coding_questions:
        turns = []
        for index, interaction in enumerate(question.ai_interactions, start=1):
            turn = {
                "turn": index,
                "user": interaction.user_message,
                "assistant": interaction.ai_response,
                "created_at": interaction.created_at.isoformat(),
            }
            turns.append(turn)
            transcript_lines.append(
                f"{question.title} | Turn {index} user: {interaction.user_message}"
            )
            transcript_lines.append(
                f"{question.title} | Turn {index} assistant: {interaction.ai_response}"
            )

        transcript_items.append(
            {
                "session_question_id": question.id,
                "title": question.question.title,
                "prompt": question.question.prompt,
                "turns": turns,
            }
        )

    return {
        "session_id": session.id,
        "question_count": len(transcript_items),
        "turn_count": sum(len(item["turns"]) for item in transcript_items),
        "coding_questions": transcript_items,
        "transcript": "\n".join(transcript_lines),
    }


def build_load_coding_ai_transcript_tool(*, db: Session, session_id: str):
    current_session_id = session_id

    @tool
    def load_coding_ai_transcript_tool(
        target_session_id: str | None = None,
    ) -> dict[str, Any]:
        """Load the AI-helper transcript from coding questions for the given session or the active session by default."""
        resolved_session_id = target_session_id or current_session_id
        session = _fetch_session_coding_transcript(db, resolved_session_id)
        if session is None:
            return {"error": f"Session {resolved_session_id} was not found."}
        return _serialize_coding_ai_transcript(session)

    return load_coding_ai_transcript_tool


def build_load_dimension_evidence_tool(*, db: Session, session_id: str):
    current_session_id = session_id
    repo = SessionRepository()

    @tool
    def load_dimension_evidence_tool(
        target_session_id: str | None = None,
    ) -> dict[str, Any]:
        """Load dimension scores and evidence for the given session or the active session by default."""
        resolved_session_id = target_session_id or current_session_id
        session = repo.fetch_session(db, resolved_session_id)
        if session is None:
            return {"error": f"Session {resolved_session_id} was not found."}

        dimension_scores = [
            {
                "dimension_name": item.dimension_name,
                "score": item.score,
                "confidence": item.confidence,
                "evidence_json": item.evidence_json,
            }
            for item in session.dimension_scores
        ]

        return {
            "session_id": session.id,
            "status": session.status,
            "candidate_name": (
                session.candidate.full_name
                if getattr(session, "candidate", None) is not None
                else None
            ),
            "recommendation": (
                session.final_report.recommendation if session.final_report else None
            ),
            "summary": session.final_report.summary if session.final_report else None,
            "dimension_scores": dimension_scores,
        }

    return load_dimension_evidence_tool
