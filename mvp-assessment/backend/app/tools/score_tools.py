from __future__ import annotations

from typing import Any

from strands import tool

from app.domain.scoring.engine import aggregate_dimension_scores, score_question


class SaveEvaluatorRunTool:
    name = "save_evaluator_run"

    def run(self, *_args, **_kwargs):
        return "Use SubmissionRepository.save_evaluator_output from the flow."


class SaveFinalReportTool:
    name = "save_final_report"

    def run(self, *_args, **_kwargs):
        return "Use ResultRepository.save_final_report from the flow."


__all__ = [
    "aggregate_dimension_scores",
    "score_question",
    "SaveEvaluatorRunTool",
    "SaveFinalReportTool",
]


def build_aggregate_dimension_scores_tool(
    *,
    scored_questions: list[dict[str, Any]],
):
    current_scored_questions = list(scored_questions)

    @tool
    def aggregate_dimension_scores_tool(
        question_scores: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Aggregate scored questions into canonical dimension scores, using the active session scores by default."""
        resolved_scores = current_scored_questions if question_scores is None else question_scores
        return aggregate_dimension_scores(resolved_scores)

    return aggregate_dimension_scores_tool
