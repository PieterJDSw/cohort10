from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.dimension_score import DimensionScore
from app.models.final_report import FinalReport


class ResultRepository:
    def save_dimension_scores(
        self, db: Session, session_id: str, scores: list[dict]
    ) -> list[DimensionScore]:
        db.execute(delete(DimensionScore).where(DimensionScore.session_id == session_id))
        created: list[DimensionScore] = []
        for payload in scores:
            item = DimensionScore(session_id=session_id, **payload)
            db.add(item)
            created.append(item)
        db.flush()
        return created

    def save_final_report(self, db: Session, session_id: str, payload: dict) -> FinalReport:
        existing = db.scalar(select(FinalReport).where(FinalReport.session_id == session_id))
        if existing:
            existing.recommendation = payload["recommendation"]
            existing.summary = payload["summary"]
            existing.chart_payload = payload["chart_payload"]
            existing.source = payload["source"]
            existing.raw_output = payload.get("raw_output")
            existing.error_message = payload.get("error_message")
            db.add(existing)
            db.flush()
            return existing

        report = FinalReport(session_id=session_id, **payload)
        db.add(report)
        db.flush()
        return report

    def fetch_final_report(self, db: Session, session_id: str) -> FinalReport | None:
        return db.scalar(select(FinalReport).where(FinalReport.session_id == session_id))

    def fetch_dimension_scores(self, db: Session, session_id: str) -> list[DimensionScore]:
        stmt = (
            select(DimensionScore)
            .where(DimensionScore.session_id == session_id)
            .order_by(DimensionScore.dimension_name.asc())
        )
        return list(db.scalars(stmt))
