from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DashboardSessionRow(BaseModel):
    session_id: str
    candidate_name: str
    status: str
    recommendation: str | None = None
    overall_score: float | None = None
    confidence: float | None = None
    started_at: datetime
    completed_at: datetime | None = None


class DashboardSessionDetail(BaseModel):
    session_id: str
    candidate_name: str
    status: str
    recommendation: str | None = None
    summary: str | None = None
    chart_payload: dict | None = None
