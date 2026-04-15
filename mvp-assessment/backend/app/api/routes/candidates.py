from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.services.session_service import SessionService
from app.schemas.candidate import CandidateStartRequest, CandidateStartResponse

router = APIRouter()
service = SessionService()


@router.post("/start", response_model=CandidateStartResponse)
def start_candidate(payload: CandidateStartRequest, db: Session = Depends(get_db)):
    try:
        candidate, session = service.create_candidate_and_session(db, payload.full_name)
        return CandidateStartResponse(
            candidate_id=candidate.id,
            session_id=session.id,
            status=session.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
