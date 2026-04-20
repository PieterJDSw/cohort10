from __future__ import annotations

QUESTION_TYPE_TO_DIMENSIONS = {
    "coding": {
        "coding_skill": 0.70,
        "core_understanding": 0.20,
        "communication": 0.10,
    },
    "architecture": {
        "architecture_design": 0.70,
        "core_understanding": 0.20,
        "communication": 0.10,
    },
    "theory": {
        "core_understanding": 0.75,
        "communication": 0.25,
    },
    "culture": {
        "ownership_judgment": 0.60,
        "communication": 0.40,
    },
    "ai_fluency": {
        "ai_fluency": 0.70,
        "ownership_judgment": 0.15,
        "core_understanding": 0.15,
    },
}
