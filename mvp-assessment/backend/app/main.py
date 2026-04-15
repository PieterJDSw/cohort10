from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ai, candidates, dashboard, results, sessions, submissions
from app.bootstrap import bootstrap_application
from app.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap_application()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://frontend:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(submissions.router, prefix="/api/sessions", tags=["submissions"])
app.include_router(ai.router, prefix="/api/sessions", tags=["ai"])
app.include_router(results.router, prefix="/api/sessions", tags=["results"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
