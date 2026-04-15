from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.services.result_service import ResultService
from app.schemas.result import AuditPayload, ResultPayload

router = APIRouter()
service = ResultService()


@router.get("/{session_id}/results", response_model=ResultPayload)
def get_results(session_id: str, db: Session = Depends(get_db)):
    try:
        return ResultPayload(**service.get_results(db, session_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{session_id}/report", response_model=ResultPayload)
def get_report(session_id: str, db: Session = Depends(get_db)):
    try:
        return ResultPayload(**service.get_report(db, session_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{session_id}/audit", response_model=AuditPayload)
def get_audit(session_id: str, db: Session = Depends(get_db)):
    try:
        return AuditPayload(**service.get_audit(db, session_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
