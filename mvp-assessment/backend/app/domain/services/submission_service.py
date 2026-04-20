from __future__ import annotations

import json
from datetime import datetime, timezone

from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.domain.repositories.submission_repo import SubmissionRepository
from app.domain.services.question_service import QuestionService
from app.logging_config import get_logger
from app.messaging import publish_event
from app.metrics import llm_requests_total
from app.tools.code_runner_tools import run_python_tests

logger = get_logger(__name__)


class SubmissionService:
    def __init__(self) -> None:
        self.submission_repo = SubmissionRepository()
        self.question_service = QuestionService()

    def _current_session_question(self, db: Session, session_id: str):
        current, _ = self.question_service.get_active_session_question(db, session_id)
        if not current:
            raise ValueError("No active question")
        return current

    def _evaluation_message(self, session_id: str, current) -> dict:
        return {
            "event_type": "evaluate_question_requested",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "session_question_id": current.id,
            "question_type": current.question.type,
            "force": True,
        }

    def _publish_evaluation_request(self, session_id: str, current) -> None:
        published = publish_event(
            settings.rabbitmq_evaluate_queue,
            self._evaluation_message(session_id, current),
        )
        if not published:
            raise ValueError("Unable to publish evaluation request")

    def save_text_submission(self, db: Session, session_id: str, answer: str):
        current = self._current_session_question(db, session_id)
        submission = self.submission_repo.save_text_answer(db, current.id, answer)
        current.status = "evaluation_queued"
        self._publish_evaluation_request(session_id, current)
        db.commit()
        logger.info(
            "text_submission_saved",
            extra={
                "session_id": session_id,
                "session_question_id": current.id,
                "question_type": current.question.type,
                "submission_id": submission.id,
            },
        )
        return submission

    def save_code_submission(self, db: Session, session_id: str, code: str, language: str):
        current = self._current_session_question(db, session_id)
        submission = self.submission_repo.save_code_answer(db, current.id, code, language)
        current.status = "evaluation_queued"
        self._publish_evaluation_request(session_id, current)
        db.commit()
        logger.info(
            "code_submission_saved",
            extra={
                "session_id": session_id,
                "session_question_id": current.id,
                "question_type": current.question.type,
                "submission_id": submission.id,
                "language": language,
            },
        )
        return submission

    def run_code(self, db: Session, session_id: str, code: str, language: str) -> dict:
        current = self._current_session_question(db, session_id)
        if current.question.type != "coding":
            raise ValueError("Current question is not a coding question")
        if language.lower() != "python":
            raise ValueError("Only Python is supported in the MVP code runner")
        result = run_python_tests(code, current.question.metadata_json or {})
        logger.info(
            "code_run_completed",
            extra={
                "session_id": session_id,
                "session_question_id": current.id,
                "status": result.get("status"),
                "passed": result.get("passed"),
                "total": result.get("total"),
            },
        )
        return result

    def _llm_model_name(self) -> str:
        return settings.model_name.removeprefix("openai/")

    def _fallback_hint(self, current, message: str) -> str:
        metadata = current.question.metadata_json or {}

        if current.question.type == "coding":
            tests = metadata.get("tests", [])
            entrypoint = metadata.get("entrypoint")
            if tests:
                examples = []
                for test in tests[:2]:
                    examples.append(
                        f"{test.get('name', 'test')}: input={test.get('input')} expected={test.get('expected')}"
                    )
                return (
                    f"Start from the function contract first: implement `{entrypoint or 'the requested function'}` "
                    "for the happy path, then check it against the provided examples. "
                    f"Use the tests as anchors: {'; '.join(examples)}. "
                    "Choose the simplest data structure that makes those examples pass before refining."
                )

            return (
                "Restate the problem as input, output, and rule. Then pick the data structure you need, "
                "solve the happy path first, and only after that handle edge cases and cleanup."
            )

        if current.question.type == "theory":
            return (
                "Answer in three parts: what it is, when you would use it, and what tradeoffs it creates. "
                "That usually gives enough depth without drifting."
            )
        if current.question.type == "architecture":
            return (
                "Structure the answer as components, data flow, failure handling, and scaling tradeoffs. "
                "If you keep that order, the answer will stay concrete."
            )
        if current.question.type == "culture":
            return (
                "Lead with the first concrete action you would take, then explain how you would communicate "
                "and prioritize. Avoid abstract values-only answers."
            )
        return (
            "Explain how you would use AI, then show how you would verify the output before trusting it. "
            "That verification step is the important part."
        )

    def _generate_ai_hint(self, db: Session, current, message: str) -> str:
        if not settings.llm_enabled:
            return self._fallback_hint(current, message)

        tests = (current.question.metadata_json or {}).get("tests", [])
        latest_submission = self.submission_repo.fetch_latest_answer(db, current.id)
        previous_answer = ""
        if latest_submission:
            previous_answer = latest_submission.code_answer or latest_submission.text_answer or ""

        rubric_text = json.dumps(current.question.rubric_json or {}, ensure_ascii=True)
        tests_text = json.dumps(tests, ensure_ascii=True)

        system_prompt = (
            "You are an assessment helper. Give useful, concrete guidance without giving the full final answer "
            "unless the user explicitly asks for it. "
            "Do not narrate internal reasoning. Do not use preambles such as 'Okay, let's see'. "
            "Respond with 2 to 4 short bullets. Each bullet must be actionable. "
            "For coding questions, mention the likely algorithm or data structure and the next implementation step."
        )

        user_prompt = (
            f"Question type: {current.question.type}\n"
            f"Question title: {current.question.title}\n"
            f"Question prompt: {current.question.prompt}\n"
            f"Question rubric: {rubric_text}\n"
            f"Known tests: {tests_text}\n"
            f"Candidate draft answer/code so far: {previous_answer}\n"
            f"Candidate asks: {message.strip()}\n"
            "Give a practical hint, not a generic coaching statement."
        )

        try:
            llm_requests_total.labels(operation="ai_helper_chat", status="started").inc()
            client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)
            response = client.chat.completions.create(
                model=self._llm_model_name(),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=220,
            )
            content = response.choices[0].message.content or ""
            cleaned = content.replace("<think>", "").replace("</think>", "").strip()
            logger.info(
                "ai_hint_generated",
                extra={"question_type": current.question.type, "used_fallback": not bool(cleaned)},
            )
            llm_requests_total.labels(operation="ai_helper_chat", status="success").inc()
            return cleaned or self._fallback_hint(current, message)
        except Exception:
            llm_requests_total.labels(operation="ai_helper_chat", status="failure").inc()
            logger.exception("ai_hint_generation_failed", extra={"question_type": current.question.type})
            return self._fallback_hint(current, message)

    def run_ai_chat(self, db: Session, session_id: str, message: str) -> dict:
        current = self._current_session_question(db, session_id)
        response = self._generate_ai_hint(db, current, message)
        self.submission_repo.save_ai_interaction(db, current.id, message, response)
        db.commit()
        logger.info(
            "ai_chat_saved",
            extra={
                "session_id": session_id,
                "session_question_id": current.id,
                "question_type": current.question.type,
            },
        )
        return {"response": response}
