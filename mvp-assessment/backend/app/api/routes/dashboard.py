from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.services.result_service import ResultService
from app.schemas.dashboard import DashboardSessionDetail, DashboardSessionRow

router = APIRouter()
service = ResultService()


@router.get("/sessions", response_model=list[DashboardSessionRow])
def list_sessions(db: Session = Depends(get_db)):
    return [DashboardSessionRow(**row) for row in service.list_sessions(db)]


@router.get("/sessions/{session_id}", response_model=DashboardSessionDetail)
def get_dashboard_session(session_id: str, db: Session = Depends(get_db)):
    try:
        return DashboardSessionDetail(**service.get_dashboard_session(db, session_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
