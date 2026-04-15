from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.services.session_service import SessionService
from app.schemas.session import QuestionPayload, SessionSummary

router = APIRouter()
service = SessionService()


@router.get("/{session_id}", response_model=SessionSummary)
def get_session(session_id: str, db: Session = Depends(get_db)):
    try:
        return SessionSummary(**service.get_session_summary(db, session_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{session_id}/current-question", response_model=QuestionPayload | None)
def current_question(session_id: str, db: Session = Depends(get_db)):
    try:
        payload = service.get_current_question(db, session_id)
        return QuestionPayload(**payload) if payload else None
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{session_id}/next", response_model=QuestionPayload | None)
def advance_session(session_id: str, db: Session = Depends(get_db)):
    try:
        payload = service.advance_session(db, session_id)
        return QuestionPayload(**payload) if payload else None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{session_id}/finish")
def finish_session(session_id: str, db: Session = Depends(get_db)):
    try:
        return service.finish_session(db, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
