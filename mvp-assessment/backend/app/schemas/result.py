from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DimensionScorePayload(BaseModel):
    dimension_name: str
    score: float
    confidence: float
    evidence: dict


class ResultPayload(BaseModel):
    session_id: str
    recommendation: str
    summary: str
    overall_score: float
    confidence: float
    dimension_scores: list[DimensionScorePayload]
    strengths: list[str]
    weaknesses: list[str]
    chart_payload: dict


class AuditSubmissionPayload(BaseModel):
    id: str
    submission_type: str
    text_answer: str | None = None
    code_answer: str | None = None
    language: str | None = None
    created_at: datetime


class AuditAIInteractionPayload(BaseModel):
    id: str
    user_message: str
    ai_response: str
    created_at: datetime


class AuditEvaluatorRunPayload(BaseModel):
    id: str
    evaluator_type: str
    source: str
    confidence: float
    output_json: dict
    raw_output: str | None = None
    error_message: str | None = None
    created_at: datetime


class AuditQuestionPayload(BaseModel):
    session_question_id: str
    sequence_no: int
    status: str
    question_id: str
    question_type: str
    title: str
    difficulty: str
    prompt: str
    rubric: dict
    metadata: dict
    submissions: list[AuditSubmissionPayload]
    ai_interactions: list[AuditAIInteractionPayload]
    evaluator_runs: list[AuditEvaluatorRunPayload]


class AuditFinalReportPayload(BaseModel):
    recommendation: str
    summary: str
    chart_payload: dict
    source: str
    raw_output: str | None = None
    error_message: str | None = None
    created_at: datetime


class AuditPayload(BaseModel):
    session_id: str
    candidate_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    final_report: AuditFinalReportPayload | None = None
    dimension_scores: list[DimensionScorePayload]
    questions: list[AuditQuestionPayload]
