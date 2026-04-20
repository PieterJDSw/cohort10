from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.repositories.result_repo import ResultRepository
from app.domain.repositories.session_repo import SessionRepository


class ResultService:
    def __init__(self) -> None:
        self.result_repo = ResultRepository()
        self.session_repo = SessionRepository()

    def get_results(self, db: Session, session_id: str) -> dict:
        report = self.result_repo.fetch_final_report(db, session_id)
        dimension_scores = self.result_repo.fetch_dimension_scores(db, session_id)
        if not report:
            raise ValueError("Results not available")
        chart_payload = report.chart_payload or {}
        return {
            "session_id": session_id,
            "recommendation": report.recommendation,
            "summary": report.summary,
            "overall_score": chart_payload.get("overall_score", 0.0),
            "confidence": chart_payload.get("confidence", 0.0),
            "dimension_scores": [
                {
                    "dimension_name": item.dimension_name,
                    "score": item.score,
                    "confidence": item.confidence,
                    "evidence": item.evidence_json,
                }
                for item in dimension_scores
            ],
            "strengths": chart_payload.get("strengths", []),
            "weaknesses": chart_payload.get("weaknesses", []),
            "chart_payload": chart_payload,
        }

    def get_report(self, db: Session, session_id: str) -> dict:
        return self.get_results(db, session_id)

    def get_audit(self, db: Session, session_id: str) -> dict:
        session = self.session_repo.fetch_session_for_audit(db, session_id)
        if not session:
            raise ValueError("Session not found")

        ordered_questions = sorted(session.session_questions, key=lambda item: item.sequence_no)
        return {
            "session_id": session.id,
            "candidate_name": session.candidate.full_name,
            "status": session.status,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "final_report": (
                {
                    "recommendation": session.final_report.recommendation,
                    "summary": session.final_report.summary,
                    "chart_payload": session.final_report.chart_payload or {},
                    "source": session.final_report.source,
                    "raw_output": session.final_report.raw_output,
                    "error_message": session.final_report.error_message,
                    "created_at": session.final_report.created_at,
                }
                if session.final_report
                else None
            ),
            "dimension_scores": [
                {
                    "dimension_name": item.dimension_name,
                    "score": item.score,
                    "confidence": item.confidence,
                    "evidence": item.evidence_json,
                }
                for item in sorted(session.dimension_scores, key=lambda item: item.dimension_name)
            ],
            "questions": [
                {
                    "session_question_id": item.id,
                    "sequence_no": item.sequence_no,
                    "status": item.status,
                    "question_id": item.question_id,
                    "question_type": item.question.type,
                    "title": item.question.title,
                    "difficulty": item.question.difficulty,
                    "prompt": item.question.prompt,
                    "rubric": item.question.rubric_json or {},
                    "metadata": item.question.metadata_json or {},
                    "submissions": [
                        {
                            "id": submission.id,
                            "submission_type": submission.submission_type,
                            "text_answer": submission.text_answer,
                            "code_answer": submission.code_answer,
                            "language": submission.language,
                            "created_at": submission.created_at,
                        }
                        for submission in sorted(
                            item.submissions, key=lambda submission: submission.created_at
                        )
                    ],
                    "ai_interactions": [
                        {
                            "id": interaction.id,
                            "user_message": interaction.user_message,
                            "ai_response": interaction.ai_response,
                            "created_at": interaction.created_at,
                        }
                        for interaction in sorted(
                            item.ai_interactions, key=lambda interaction: interaction.created_at
                        )
                    ],
                    "evaluator_runs": [
                        {
                            "id": run.id,
                            "evaluator_type": run.evaluator_type,
                            "source": run.source,
                            "confidence": run.confidence,
                            "output_json": run.output_json or {},
                            "raw_output": run.raw_output,
                            "error_message": run.error_message,
                            "created_at": run.created_at,
                        }
                        for run in sorted(
                            item.evaluator_runs, key=lambda run: run.created_at
                        )
                    ],
                }
                for item in ordered_questions
            ],
        }

    def list_sessions(self, db: Session) -> list[dict]:
        sessions = self.session_repo.list_sessions(db)
        rows: list[dict] = []
        for session in sessions:
            chart_payload = session.final_report.chart_payload if session.final_report else {}
            rows.append(
                {
                    "session_id": session.id,
                    "candidate_name": session.candidate.full_name,
                    "status": session.status,
                    "recommendation": session.final_report.recommendation if session.final_report else None,
                    "overall_score": chart_payload.get("overall_score"),
                    "confidence": chart_payload.get("confidence"),
                    "started_at": session.started_at,
                    "completed_at": session.completed_at,
                }
            )
        return rows

    def get_dashboard_session(self, db: Session, session_id: str) -> dict:
        session = self.session_repo.fetch_session(db, session_id)
        if not session:
            raise ValueError("Session not found")
        return {
            "session_id": session.id,
            "candidate_name": session.candidate.full_name,
            "status": session.status,
            "recommendation": session.final_report.recommendation if session.final_report else None,
            "summary": session.final_report.summary if session.final_report else None,
            "chart_payload": session.final_report.chart_payload if session.final_report else None,
        }
