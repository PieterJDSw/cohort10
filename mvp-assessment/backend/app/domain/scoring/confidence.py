from __future__ import annotations


def average_confidence(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)
