from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.crew.crew import run_crewai_evaluation, run_crewai_synthesis
from app.domain.repositories.result_repo import ResultRepository
from app.domain.repositories.submission_repo import SubmissionRepository
from app.logging_config import get_logger
from app.messaging import publish_dead_letter, publish_event
from app.metrics import (
    llm_requests_total,
    measure_question_evaluation,
    measure_session_finalization,
    question_evaluation_total,
    session_finalization_total,
)
from app.domain.scoring.engine import (
    aggregate_dimension_scores,
    build_chart_payload,
    build_recommendation,
    score_question,
)
from app.models.session import TestSession
from app.models.session_question import SessionQuestion
from app.tools.code_runner_tools import run_python_tests

logger = get_logger(__name__)

submission_repo = SubmissionRepository()
result_repo = ResultRepository()


def _evaluation_message(session_question: SessionQuestion, context: dict, *, force: bool) -> dict:
    return {
        "event_type": "evaluate_question_requested",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "session_id": context["session_id"],
        "session_question_id": context["session_question_id"],
        "question_type": context["question_type"],
        "force": force,
        "has_submission": bool(str(context["submission"]).strip()),
        "has_ai_logs": bool(context.get("ai_logs")),
        "rubric_keys": context["rubric_keys"],
    }


def _synthesis_message(
    session_id: str,
    scored_questions: list[dict],
    dimension_scores: list[dict],
    strengths: list[str],
    weaknesses: list[str],
) -> dict:
    return {
        "event_type": "session_synthesis_requested",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "question_count": len(scored_questions),
        "dimension_count": len(dimension_scores),
        "strength_count": len(strengths),
        "weakness_count": len(weaknesses),
        "question_types": sorted(
            {
                item.get("question_type", "unknown")
                for item in scored_questions
                if isinstance(item, dict)
            }
        ),
    }


def _serialize_ai_logs(ai_interactions) -> list[dict]:
    return [
        {"user": item.user_message, "assistant": item.ai_response}
        for item in ai_interactions
    ]


def _collect_session_ai_logs(
    session_questions: list[SessionQuestion], *, question_types: set[str] | None = None
) -> list[dict]:
    logs: list[dict] = []
    for item in session_questions:
        if question_types and item.question.type not in question_types:
            continue
        logs.extend(_serialize_ai_logs(item.ai_interactions))
    return logs


def _format_ai_usage_transcript(ai_logs: list[dict]) -> str:
    lines: list[str] = []
    for index, item in enumerate(ai_logs, start=1):
        lines.append(f"Turn {index} user: {item['user']}")
        lines.append(f"Turn {index} assistant: {item['assistant']}")
    return "\n".join(lines)


def _build_no_submission_output(context: dict) -> dict:
    scores = {key: 0.0 for key in context["rubric_keys"]}
    question_type = context["question_type"]
    ai_logs = context.get("ai_logs") or []

    return {
        "summary": f"No candidate response was submitted for this {question_type} question.",
        "rubric_scores": scores,
        "strengths": [],
        "weaknesses": context["rubric_keys"][:2],
        "red_flags": ["missing_submission"],
        "confidence": 0.0,
    }


def _build_llm_failure_output(context: dict, error_message: str | None) -> dict:
    rubric_scores = {key: 0.0 for key in context["rubric_keys"]}
    return {
        "summary": (
            "Evaluation failed after LLM retry attempts."
            if not error_message
            else f"Evaluation failed after LLM retry attempts: {error_message}"
        ),
        "rubric_scores": rubric_scores,
        "strengths": [],
        "weaknesses": context["rubric_keys"][:2],
        "red_flags": ["evaluation_failed"],
        "confidence": 0.0,
    }


def _merge_evaluation_result(context: dict, llm_result: dict | None) -> dict:
    parsed_output = (llm_result or {}).get("parsed_output")
    if parsed_output:
        return {
            "parsed_output": parsed_output,
            "source": (llm_result or {}).get("source", "llm"),
            "raw_output": (llm_result or {}).get("raw_output"),
            "error_message": (llm_result or {}).get("error_message"),
        }

    return {
        "parsed_output": _build_llm_failure_output(
            context,
            (llm_result or {}).get("error_message"),
        ),
        "source": (llm_result or {}).get("source", "llm_failed_after_retries"),
        "raw_output": (llm_result or {}).get("raw_output"),
        "error_message": (llm_result or {}).get("error_message"),
    }


def _latest_submission_value(session_question: SessionQuestion) -> tuple[str, object | None]:
    latest_text = next(
        (item for item in reversed(session_question.submissions) if item.submission_type == "text"),
        None,
    )
    latest_code = next(
        (item for item in reversed(session_question.submissions) if item.submission_type == "code"),
        None,
    )
    latest_submission = (
        latest_code.code_answer if latest_code else latest_text.text_answer if latest_text else ""
    )
    return latest_submission, latest_code


def _build_question_context(session_question: SessionQuestion, db: Session) -> tuple[dict, dict | None]:
    question = session_question.question
    session_questions = list(session_question.session.session_questions)
    latest_submission, latest_code = _latest_submission_value(session_question)
    local_ai_logs = _serialize_ai_logs(session_question.ai_interactions)
    coding_ai_logs = _collect_session_ai_logs(session_questions, question_types={"coding"})
    evaluation_ai_logs = local_ai_logs
    if question.type == "ai_fluency":
        evaluation_ai_logs = coding_ai_logs + [
            item for item in local_ai_logs if item not in coding_ai_logs
        ]
        if not latest_submission and evaluation_ai_logs:
            latest_submission = _format_ai_usage_transcript(evaluation_ai_logs)

    code_results = None
    if question.type == "coding" and latest_code:
        code_results = run_python_tests(latest_code.code_answer or "", question.metadata_json or {})

    context = {
        "db": db,
        "session_id": session_question.session_id,
        "session_question_id": session_question.id,
        "question_type": question.type,
        "prompt": question.prompt,
        "rubric": question.rubric_json,
        "rubric_keys": list((question.rubric_json or {}).keys()),
        "submission": latest_submission,
        "ai_logs": evaluation_ai_logs,
        "code_results": code_results,
        "code_metadata": question.metadata_json or {},
    }
    return context, code_results


def _latest_evaluator_run(session_question: SessionQuestion):
    if not session_question.evaluator_runs:
        return None
    return max(session_question.evaluator_runs, key=lambda item: item.created_at)


def _score_saved_evaluation(session_question: SessionQuestion, evaluator_output: dict) -> dict:
    _, latest_code = _latest_submission_value(session_question)
    code_results = None
    if session_question.question.type == "coding" and latest_code:
        code_results = run_python_tests(
            latest_code.code_answer or "",
            session_question.question.metadata_json or {},
        )
    return score_question(session_question.question.type, evaluator_output, code_results)


def _persist_evaluation_result(
    db: Session,
    session_question: SessionQuestion,
    evaluation_result: dict,
) -> dict:
    evaluator_output = evaluation_result["parsed_output"]
    submission_repo.clear_evaluator_runs(db, session_question.id)
    submission_repo.save_evaluator_output(
        db,
        session_question.id,
        session_question.question.type,
        evaluation_result["source"],
        evaluator_output,
        evaluation_result.get("raw_output"),
        evaluation_result.get("error_message"),
        float(evaluator_output.get("confidence", 0.0)),
    )
    return _score_saved_evaluation(session_question, evaluator_output)


def evaluate_question(db: Session, session_question_id: str, *, force: bool = True) -> dict | None:
    logger.info(
        "question_evaluation_started",
        extra={"session_question_id": session_question_id, "force": force},
    )
    session_question = db.execute(
        select(SessionQuestion)
        .options(
            joinedload(SessionQuestion.question),
            joinedload(SessionQuestion.submissions),
            joinedload(SessionQuestion.ai_interactions),
            joinedload(SessionQuestion.evaluator_runs),
            joinedload(SessionQuestion.session)
            .joinedload(TestSession.session_questions)
            .joinedload(SessionQuestion.question),
            joinedload(SessionQuestion.session)
            .joinedload(TestSession.session_questions)
            .joinedload(SessionQuestion.ai_interactions),
        )
        .where(SessionQuestion.id == session_question_id)
    ).unique().scalar_one_or_none()
    if not session_question:
        return None

    latest_saved_run = _latest_evaluator_run(session_question)
    if latest_saved_run and not force:
        return _score_saved_evaluation(session_question, latest_saved_run.output_json or {})

    context, _ = _build_question_context(session_question, db)
    evaluation_message = _evaluation_message(session_question, context, force=force)
    publish_event(settings.rabbitmq_evaluate_queue, evaluation_message)
    with measure_question_evaluation(session_question.question.type):
        if not str(context["submission"]).strip():
            evaluation_result = {
                "parsed_output": _build_no_submission_output(context),
                "source": "no_submission",
                "raw_output": None,
                "error_message": None,
            }
        else:
            llm_requests_total.labels(operation="question_evaluation", status="started").inc()
            try:
                llm_result = run_crewai_evaluation(session_question.question.type, context)
            except Exception as exc:
                publish_dead_letter(
                    "question_evaluation_exception",
                    {
                        **evaluation_message,
                        "error_message": str(exc),
                    },
                )
                raise
            evaluation_result = _merge_evaluation_result(context, llm_result)
            llm_status = "success" if llm_result.get("parsed_output") else "failure"
            llm_requests_total.labels(operation="question_evaluation", status=llm_status).inc()
            if llm_status == "failure":
                publish_dead_letter(
                    "question_evaluation_failed",
                    {
                        **evaluation_message,
                        "source": evaluation_result.get("source"),
                        "error_message": evaluation_result.get("error_message"),
                    },
                )
    scored = _persist_evaluation_result(db, session_question, evaluation_result)
    question_evaluation_total.labels(
        question_type=session_question.question.type,
        source=evaluation_result.get("source", "unknown"),
    ).inc()
    logger.info(
        "question_evaluation_completed",
        extra={
            "session_question_id": session_question_id,
            "question_type": session_question.question.type,
            "source": evaluation_result.get("source"),
        },
    )
    return scored


def finalize_session(db: Session, session_id: str) -> dict:
    logger.info("session_finalization_started", extra={"session_id": session_id})
    with measure_session_finalization():
        session = db.execute(
            select(TestSession)
            .options(
                joinedload(TestSession.session_questions)
                .joinedload(SessionQuestion.question),
                joinedload(TestSession.session_questions)
                .joinedload(SessionQuestion.submissions),
                joinedload(TestSession.session_questions)
                .joinedload(SessionQuestion.ai_interactions),
                joinedload(TestSession.session_questions)
                .joinedload(SessionQuestion.evaluator_runs),
            )
            .where(TestSession.id == session_id)
        ).unique().scalar_one_or_none()
        if not session:
            raise ValueError("Session not found")

        scored_questions: list[dict] = []
        strengths: list[str] = []
        weaknesses: list[str] = []
        for session_question in sorted(session.session_questions, key=lambda item: item.sequence_no):
            latest_saved_run = _latest_evaluator_run(session_question)
            if latest_saved_run:
                scored = _score_saved_evaluation(session_question, latest_saved_run.output_json or {})
            else:
                scored = evaluate_question(db, session_question.id, force=True)
            if not scored:
                continue
            strengths.extend(scored["strengths"])
            weaknesses.extend(scored["weaknesses"])
            scored_questions.append(scored)

        dimension_scores = aggregate_dimension_scores(scored_questions)
        overall_score = round(
            sum(item["score"] for item in dimension_scores) / max(len(dimension_scores), 1), 2
        )
        recommendation = build_recommendation(overall_score)

        synthesis_message = _synthesis_message(
            session_id,
            scored_questions,
            dimension_scores,
            strengths,
            weaknesses,
        )
        publish_event(settings.rabbitmq_synthesis_queue, synthesis_message)
        llm_requests_total.labels(operation="session_synthesis", status="started").inc()
        try:
            synthesis_result = run_crewai_synthesis(
                {
                    "session_id": session_id,
                    "scored_questions": scored_questions,
                    "dimension_scores": dimension_scores,
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                },
                db=db,
                session_id=session_id,
            )
        except Exception as exc:
            publish_dead_letter(
                "session_synthesis_exception",
                {
                    **synthesis_message,
                    "error_message": str(exc),
                },
            )
            raise
        llm_status = "success" if synthesis_result.get("parsed_output") else "failure"
        llm_requests_total.labels(operation="session_synthesis", status=llm_status).inc()
        if llm_status == "failure":
            publish_dead_letter(
                "session_synthesis_failed",
                {
                    **synthesis_message,
                    "error_message": synthesis_result.get("error_message"),
                    "source": synthesis_result.get("source"),
                },
            )
        synthesis = synthesis_result.get("parsed_output") or {
            "recommendation": recommendation,
            "summary": (
                "Synthesis failed after LLM retry attempts."
                if not synthesis_result.get("error_message")
                else f"Synthesis failed after LLM retry attempts: {synthesis_result.get('error_message')}"
            ),
            "strengths": list(dict.fromkeys(strengths))[:5],
            "weaknesses": list(dict.fromkeys(weaknesses))[:5],
        }
        synthesis_source = synthesis_result.get("source", "llm_failed_after_retries")
        synthesis_raw_output = synthesis_result.get("raw_output")
        synthesis_error_message = synthesis_result.get("error_message")

        result_repo.save_dimension_scores(db, session_id, dimension_scores)
        chart_payload = build_chart_payload(
            dimension_scores, synthesis.get("strengths", []), synthesis.get("weaknesses", [])
        )
        chart_payload["overall_score"] = overall_score
        chart_payload["confidence"] = round(
            sum(item["confidence"] for item in dimension_scores) / max(len(dimension_scores), 1), 2
        )
        result_repo.save_final_report(
            db,
            session_id,
            {
                "recommendation": synthesis.get("recommendation", recommendation),
                "summary": synthesis["summary"],
                "chart_payload": chart_payload,
                "source": synthesis_source,
                "raw_output": synthesis_raw_output,
                "error_message": synthesis_error_message,
            },
        )
    session_finalization_total.labels(
        recommendation=synthesis.get("recommendation", recommendation),
    ).inc()
    logger.info(
        "session_finalization_completed",
        extra={
            "session_id": session_id,
            "overall_score": overall_score,
            "recommendation": synthesis.get("recommendation", recommendation),
        },
    )
    return {
        "overall_score": overall_score,
        "confidence": chart_payload["confidence"],
        "recommendation": synthesis.get("recommendation", recommendation),
        "summary": synthesis["summary"],
        "dimension_scores": dimension_scores,
        "strengths": synthesis.get("strengths", []),
        "weaknesses": synthesis.get("weaknesses", []),
        "chart_payload": chart_payload,
    }
