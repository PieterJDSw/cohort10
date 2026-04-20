from __future__ import annotations

from typing import Any

from strands import tool


def _compute_ai_usage_metrics(ai_logs: list[dict[str, Any]]) -> dict[str, Any]:
    verification_terms = ["test", "verify", "edge", "case", "check", "debug"]
    correction_terms = ["wrong", "fix", "error", "bug", "why", "incorrect"]
    prompt_terms = ["constraint", "optimize", "complexity", "approach", "algorithm"]

    user_messages = [str(item.get("user", "")) for item in ai_logs]
    assistant_messages = [str(item.get("assistant", "")) for item in ai_logs]
    joined_user_text = " ".join(message.lower() for message in user_messages)

    def _matched_terms(terms: list[str]) -> list[str]:
        return [term for term in terms if term in joined_user_text]

    verification_matches = _matched_terms(verification_terms)
    correction_matches = _matched_terms(correction_terms)
    prompt_matches = _matched_terms(prompt_terms)

    return {
        "turn_count": len(ai_logs),
        "user_message_count": len(user_messages),
        "assistant_message_count": len(assistant_messages),
        "user_word_count": sum(len(message.split()) for message in user_messages),
        "assistant_word_count": sum(
            len(message.split()) for message in assistant_messages
        ),
        "avg_user_words_per_turn": round(
            (
                sum(len(message.split()) for message in user_messages)
                / max(len(user_messages), 1)
            ),
            2,
        ),
        "flags": {
            "mentions_verification": bool(verification_matches),
            "mentions_correction": bool(correction_matches),
            "mentions_prompt_specificity": bool(prompt_matches),
        },
        "matched_terms": {
            "verification": verification_matches,
            "correction": correction_matches,
            "prompt_specificity": prompt_matches,
        },
    }


def build_compute_ai_usage_metrics_tool(*, ai_logs: list[dict[str, Any]]):
    current_ai_logs = list(ai_logs)

    @tool
    def compute_ai_usage_metrics_tool(
        logs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Compute deterministic AI-usage metrics from helper chat logs, using the active transcript by default."""
        resolved_logs = current_ai_logs if logs is None else logs
        return _compute_ai_usage_metrics(resolved_logs)

    return compute_ai_usage_metrics_tool
