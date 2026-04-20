from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SessionSummary(BaseModel):
    session_id: str
    candidate_id: str
    candidate_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    total_questions: int
    current_sequence: int


class QuestionPayload(BaseModel):
    session_question_id: str
    question_id: str
    type: str
    title: str
    prompt: str
    difficulty: str
    sequence_no: int
    total_questions: int
    rubric: dict
    metadata: dict
