from __future__ import annotations

from collections import defaultdict

from app.domain.scoring.confidence import average_confidence
from app.domain.scoring.formulas import calculate_weighted_score
from app.domain.scoring.mappings import QUESTION_TYPE_TO_DIMENSIONS

CANONICAL_DIMENSIONS = [
    "coding_skill",
    "architecture_design",
    "core_understanding",
    "communication",
    "ownership_judgment",
    "ai_fluency",
]


def score_question(
    question_type: str, evaluator_output: dict, code_results: dict | None = None
) -> dict:
    rubric_scores = dict(evaluator_output.get("rubric_scores", {}))
    if question_type == "coding" and code_results:
        total = max(code_results.get("total", 0), 1)
        rubric_scores["correctness"] = round((code_results.get("passed", 0) / total) * 100, 2)
    overall = calculate_weighted_score(question_type, rubric_scores)
    return {
        "question_type": question_type,
        "overall_score": overall,
        "rubric_scores": rubric_scores,
        "confidence": float(evaluator_output.get("confidence", 0.0)),
        "strengths": evaluator_output.get("strengths", []),
        "weaknesses": evaluator_output.get("weaknesses", []),
        "summary": evaluator_output.get("summary", ""),
    }


def aggregate_dimension_scores(scored_questions: list[dict]) -> list[dict]:
    totals: dict[str, float] = defaultdict(float)
    weights: dict[str, float] = defaultdict(float)
    confidence_buckets: dict[str, list[float]] = defaultdict(list)
    evidence: dict[str, list[dict]] = defaultdict(list)

    for item in scored_questions:
        mapping = QUESTION_TYPE_TO_DIMENSIONS.get(item["question_type"], {})
        for dimension, ratio in mapping.items():
            contribution = item["overall_score"] * ratio
            totals[dimension] += contribution
            weights[dimension] += ratio
            confidence_buckets[dimension].append(item["confidence"])
            evidence[dimension].append(
                {
                    "question_type": item["question_type"],
                    "score": item["overall_score"],
                    "summary": item["summary"],
                }
            )

    results: list[dict] = []
    for dimension, total in totals.items():
        weight = weights.get(dimension, 1.0) or 1.0
        results.append(
            {
                "dimension_name": dimension,
                "score": round(total / weight, 2),
                "confidence": average_confidence(confidence_buckets[dimension]),
                "evidence_json": {"items": evidence[dimension]},
            }
        )

    existing_dimensions = {item["dimension_name"] for item in results}
    for dimension in CANONICAL_DIMENSIONS:
        if dimension in existing_dimensions:
            continue
        results.append(
            {
                "dimension_name": dimension,
                "score": 0.0,
                "confidence": 0.0,
                "evidence_json": {"items": []},
            }
        )

    dimension_order = {name: index for index, name in enumerate(CANONICAL_DIMENSIONS)}
    return sorted(results, key=lambda item: dimension_order.get(item["dimension_name"], 999))


def build_chart_payload(
    dimension_scores: list[dict], strengths: list[str], weaknesses: list[str]
) -> dict:
    return {
        "labels": [item["dimension_name"] for item in dimension_scores],
        "scores": [item["score"] for item in dimension_scores],
        "confidences": [item["confidence"] for item in dimension_scores],
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


def build_recommendation(overall_score: float) -> str:
    if overall_score >= 80:
        return "strong_hire"
    if overall_score >= 65:
        return "hire"
    if overall_score >= 50:
        return "mixed"
    return "no_hire"
