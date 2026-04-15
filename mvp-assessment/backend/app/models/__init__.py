"""Database model registry."""

from app.models.ai_interaction import AIInteraction
from app.models.candidate import Candidate
from app.models.dimension_score import DimensionScore
from app.models.evaluator_run import EvaluatorRun
from app.models.final_report import FinalReport
from app.models.question import Question
from app.models.session import TestSession
from app.models.session_question import SessionQuestion
from app.models.submission import Submission

__all__ = [
    "AIInteraction",
    "Candidate",
    "DimensionScore",
    "EvaluatorRun",
    "FinalReport",
    "Question",
    "SessionQuestion",
    "Submission",
    "TestSession",
]
