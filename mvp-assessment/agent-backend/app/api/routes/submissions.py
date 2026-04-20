from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.services.submission_service import SubmissionService
from app.schemas.submission import (
    CodeRunRequest,
    CodeRunResponse,
    CodeSubmissionRequest,
    TextSubmissionRequest,
)

router = APIRouter()
service = SubmissionService()


@router.post("/{session_id}/answers/text")
def save_text_answer(
    session_id: str,
    payload: TextSubmissionRequest,
    db: Session = Depends(get_db),
):
    try:
        submission = service.save_text_submission(db, session_id, payload.answer)
        return {"submission_id": submission.id, "status": "saved"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{session_id}/answers/code")
def save_code_answer(
    session_id: str,
    payload: CodeSubmissionRequest,
    db: Session = Depends(get_db),
):
    try:
        submission = service.save_code_submission(db, session_id, payload.code, payload.language)
        return {"submission_id": submission.id, "status": "saved"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{session_id}/code/run", response_model=CodeRunResponse)
def run_code(
    session_id: str,
    payload: CodeRunRequest,
    db: Session = Depends(get_db),
):
    try:
        return CodeRunResponse(**service.run_code(db, session_id, payload.code, payload.language))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
