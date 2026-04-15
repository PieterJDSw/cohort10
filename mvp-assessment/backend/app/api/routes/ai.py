from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.services.submission_service import SubmissionService
from app.schemas.submission import AIChatRequest, AIChatResponse

router = APIRouter()
service = SubmissionService()


@router.post("/{session_id}/ai/chat", response_model=AIChatResponse)
def ai_chat(
    session_id: str,
    payload: AIChatRequest,
    db: Session = Depends(get_db),
):
    try:
        return AIChatResponse(**service.run_ai_chat(db, session_id, payload.message))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
