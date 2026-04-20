from __future__ import annotations

from pydantic import BaseModel, Field


class TextSubmissionRequest(BaseModel):
    answer: str = Field(min_length=1)


class CodeSubmissionRequest(BaseModel):
    code: str = Field(min_length=1)
    language: str = "python"


class CodeRunRequest(BaseModel):
    code: str = Field(min_length=1)
    language: str = "python"


class CodeRunResponse(BaseModel):
    status: str
    passed: int
    total: int
    results: list[dict]


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1)


class AIChatResponse(BaseModel):
    response: str
