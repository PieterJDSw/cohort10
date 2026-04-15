from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.question import Question


class QuestionRepository:
    def fetch_active_questions(self, db: Session) -> list[Question]:
        stmt = (
            select(Question)
            .where(Question.is_active.is_(True))
            .order_by(Question.created_at.asc())
        )
        return list(db.scalars(stmt))

    def fetch_question_by_id(self, db: Session, question_id: str) -> Question | None:
        return db.scalar(select(Question).where(Question.id == question_id))

    def fetch_titles(self, db: Session) -> set[str]:
        stmt = select(Question.title)
        return {title for title in db.scalars(stmt)}

    def seed_questions(self, db: Session, questions: list[dict]) -> list[Question]:
        created: list[Question] = []
        for payload in questions:
            question = Question(**payload)
            db.add(question)
            created.append(question)
        db.flush()
        return created

    def count_questions(self, db: Session) -> int:
        return int(db.scalar(select(func.count(Question.id))) or 0)
