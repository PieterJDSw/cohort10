from __future__ import annotations

import random
from collections import defaultdict

from sqlalchemy.orm import Session

from app.domain.repositories.question_repo import QuestionRepository
from app.domain.repositories.session_repo import SessionRepository
from app.models.session_question import SessionQuestion


class QuestionService:
    QUESTION_DISTRIBUTION = {
        "coding": 3,
        "theory": 2,
        "architecture": 2,
        "culture": 2,
        "ai_fluency": 1,
    }

    def __init__(self) -> None:
        self.question_repo = QuestionRepository()
        self.session_repo = SessionRepository()

    def _build_random_question_set(self, questions):
        grouped = defaultdict(list)
        for question in questions:
            grouped[question.type].append(question)

        selected = []
        selected_ids = set()

        for question_type, target_count in self.QUESTION_DISTRIBUTION.items():
            pool = grouped.get(question_type, [])
            if not pool:
                continue
            picks = random.sample(pool, k=min(target_count, len(pool)))
            for item in picks:
                if item.id not in selected_ids:
                    selected.append(item)
                    selected_ids.add(item.id)

        remaining = [question for question in questions if question.id not in selected_ids]
        slots_left = sum(self.QUESTION_DISTRIBUTION.values()) - len(selected)
        if slots_left > 0 and remaining:
            extra = random.sample(remaining, k=min(slots_left, len(remaining)))
            for item in extra:
                selected.append(item)

        random.shuffle(selected)
        return selected

    def build_default_question_plan(self, db: Session, session_id: str) -> list[SessionQuestion]:
        session = self.session_repo.fetch_session(db, session_id)
        if not session:
            raise ValueError("Session not found")
        if session.session_questions:
            return sorted(session.session_questions, key=lambda item: item.sequence_no)

        questions = self._build_random_question_set(self.question_repo.fetch_active_questions(db))
        created: list[SessionQuestion] = []
        for index, question in enumerate(questions, start=1):
            item = SessionQuestion(
                session_id=session_id,
                question_id=question.id,
                sequence_no=index,
                status="active" if index == 1 else "pending",
            )
            db.add(item)
            created.append(item)
        db.flush()
        return created

    def get_active_session_question(
        self, db: Session, session_id: str
    ) -> tuple[SessionQuestion | None, int]:
        session = self.session_repo.fetch_session(db, session_id)
        if not session:
            raise ValueError("Session not found")

        ordered = sorted(session.session_questions, key=lambda item: item.sequence_no)
        current = next(
            (item for item in ordered if item.status in {"active", "answered"}),
            None,
        )
        if current is None:
            current = next((item for item in ordered if item.status == "pending"), None)
        return current, len(ordered)
