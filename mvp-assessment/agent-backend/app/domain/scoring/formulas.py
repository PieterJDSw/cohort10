from __future__ import annotations


QUESTION_FORMULAS = {
    "coding": {
        "correctness": 0.45,
        "code_quality": 0.15,
        "problem_solving": 0.15,
        "efficiency": 0.10,
        "testing_reasoning": 0.10,
        "communication": 0.05,
    },
    "theory": {
        "conceptual_correctness": 0.40,
        "depth": 0.25,
        "tradeoff_reasoning": 0.20,
        "clarity": 0.15,
    },
    "architecture": {
        "decomposition": 0.20,
        "tradeoffs": 0.25,
        "scalability": 0.15,
        "reliability": 0.15,
        "maintainability": 0.15,
        "communication": 0.10,
    },
    "culture": {
        "ownership": 0.30,
        "collaboration": 0.25,
        "prioritization": 0.25,
        "communication_clarity": 0.20,
    },
    "ai_fluency": {
        "prompt_quality": 0.20,
        "context_provided": 0.10,
        "verification_behavior": 0.35,
        "correction_of_ai_errors": 0.20,
        "effective_use": 0.15,
    },
}


def calculate_weighted_score(question_type: str, rubric_scores: dict[str, float]) -> float:
    weights = QUESTION_FORMULAS.get(question_type, {})
    if not weights:
        return 0.0
    score = sum(float(rubric_scores.get(key, 0.0)) * weight for key, weight in weights.items())
    return round(score, 2)
