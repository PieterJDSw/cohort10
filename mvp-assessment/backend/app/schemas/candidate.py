from __future__ import annotations

from pydantic import BaseModel, Field


class CandidateStartRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)


class CandidateStartResponse(BaseModel):
    candidate_id: str
    session_id: str
    status: str
