from __future__ import annotations

import json
from typing import Any, Callable

from json_repair import repair_json
from strands import Agent
from strands.multiagent import GraphBuilder
from sqlalchemy.orm import Session

from app.config import settings
from app.crew.agents import build_evaluator_agents, build_llm_model
from app.crew.tasks import build_evaluation_prompt, build_review_prompt, build_synthesis_prompt
from app.metrics import strands_duration_seconds, strands_tokens_total

MAX_LLM_ATTEMPTS = 3
MAX_RETRY_FIELD_CHARS = 600


def _clean_raw_output(raw_output: str | None) -> str | None:
    if not raw_output:
        return None

    cleaned = raw_output.replace("<think>", "").replace("</think>", "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    return cleaned or None


def _parse_json_output(raw_output: str | None) -> dict | None:
    cleaned = _clean_raw_output(raw_output)
    if not cleaned:
        return None

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            parsed = json.loads(repair_json(cleaned))
        except Exception:
            return None

    return parsed if isinstance(parsed, dict) else None


def _coerce_float(value, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        cleaned = value.strip().lower()
        confidence_aliases = {
            "low": 0.35,
            "medium": 0.6,
            "med": 0.6,
            "high": 0.85,
        }
        if cleaned in confidence_aliases:
            return confidence_aliases[cleaned]
        try:
            return float(cleaned)
        except ValueError:
            return default

    return default


def _string_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _normalize_evaluator_output(payload: dict | None) -> dict | None:
    if not payload:
        return None

    rubric_scores = payload.get("rubric_scores")
    if isinstance(rubric_scores, dict):
        normalized_rubric_scores = {
            str(key): _coerce_float(value) for key, value in rubric_scores.items()
        }
    else:
        normalized_rubric_scores = {}

    return {
        "summary": str(payload.get("summary", "")),
        "rubric_scores": normalized_rubric_scores,
        "strengths": _string_list(payload.get("strengths")),
        "weaknesses": _string_list(payload.get("weaknesses")),
        "red_flags": _string_list(payload.get("red_flags")),
        "confidence": _coerce_float(payload.get("confidence"), 0.0),
    }


def _extract_nested_synthesis_payload(payload: dict) -> dict:
    current = payload
    for key in ("result", "output", "final_report", "recommendation"):
        nested = current.get(key)
        if isinstance(nested, dict):
            current = nested
    return current


def _coerce_recommendation(value) -> str | None:
    if isinstance(value, str):
        normalized = value.strip().lower().replace(" ", "_")
        if normalized in {"strong_hire", "hire", "mixed", "no_hire"}:
            return normalized
    return None


def _normalize_synthesis_output(payload: dict | None) -> dict | None:
    if not payload:
        return None

    normalized_payload = _extract_nested_synthesis_payload(payload)
    recommendation = _coerce_recommendation(normalized_payload.get("recommendation"))
    summary = normalized_payload.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        summary = payload.get("summary")
    summary = summary.strip() if isinstance(summary, str) else ""

    return {
        "recommendation": recommendation,
        "summary": summary,
        "strengths": _string_list(normalized_payload.get("strengths")),
        "weaknesses": _string_list(normalized_payload.get("weaknesses")),
    }


def _normalize_review_output(payload: dict | None) -> dict | None:
    if not payload or not isinstance(payload, dict):
        return None

    final_output = payload.get("final_output")
    normalized_final_output = _normalize_evaluator_output(final_output if isinstance(final_output, dict) else None)
    critique = payload.get("critique", "")

    return {
        "critique": critique.strip() if isinstance(critique, str) else "",
        "final_output": normalized_final_output,
    }


def _validate_evaluator_output(payload: dict | None, rubric_keys: list[str]) -> str | None:
    if not payload:
        return "Model returned no usable JSON object."

    missing_keys = [key for key in rubric_keys if key not in payload.get("rubric_scores", {})]
    if missing_keys:
        return f"rubric_scores is missing required keys: {missing_keys}"

    if not str(payload.get("summary", "")).strip():
        return "summary must be a non-empty string."

    confidence = payload.get("confidence", 0.0)
    if not isinstance(confidence, (int, float)) and not (
        isinstance(confidence, str) and confidence.strip()
    ):
        return "confidence must be numeric."

    return None


def _validate_synthesis_output(payload: dict | None) -> str | None:
    if not payload:
        return "Model returned no usable JSON object."

    if payload.get("recommendation") not in {"strong_hire", "hire", "mixed", "no_hire"}:
        return "recommendation must be one of strong_hire, hire, mixed, no_hire."

    if not str(payload.get("summary", "")).strip():
        return "summary must be a non-empty string."

    return None


def _validate_review_output(payload: dict | None, rubric_keys: list[str]) -> str | None:
    if not payload:
        return "Model returned no usable JSON object."

    final_output = payload.get("final_output")
    validation_error = _validate_evaluator_output(final_output, rubric_keys)
    if validation_error:
        return f"final_output is invalid: {validation_error}"

    if not str(payload.get("critique", "")).strip():
        return "critique must be a non-empty string."

    return None


def _extract_message(candidate: Any) -> str | None:
    if candidate is None:
        return None
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip()
    if isinstance(candidate, dict):
        content = candidate.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
            if parts:
                return "\n".join(parts)
    message = getattr(candidate, "message", None)
    if message is not None:
        nested_message = _extract_message(message)
        if nested_message:
            return nested_message
    result = getattr(candidate, "result", None)
    if isinstance(result, str) and result.strip():
        return result.strip()
    if result is not None and result is not candidate:
        nested = _extract_message(result)
        if nested:
            return nested
    return None


def _extract_graph_node_output(graph_result: Any, node_id: str) -> str | None:
    candidates = [
        graph_result,
        getattr(graph_result, "results", {}).get(node_id) if graph_result is not None else None,
    ]
    for candidate in candidates:
        resolved = _extract_message(candidate)
        if resolved:
            return resolved
    return None


def _extract_graph_node_result(graph_result: Any, node_id: str) -> Any:
    if graph_result is None:
        return None

    results = getattr(graph_result, "results", None)
    if isinstance(results, dict) and node_id in results:
        return results[node_id]
    return graph_result


def _extract_metric_value(container: Any, key: str) -> float | None:
    if container is None:
        return None

    if isinstance(container, dict):
        value = container.get(key)
    else:
        value = getattr(container, key, None)

    if isinstance(value, (int, float)):
        return float(value)
    return None


def _record_strands_metrics(agent_name: str, graph_result: Any, node_id: str) -> None:
    candidate = _extract_graph_node_result(graph_result, node_id)
    accumulated_usage = getattr(candidate, "accumulated_usage", None)
    cycle_durations = None
    result = getattr(candidate, "result", None)

    if accumulated_usage is None or cycle_durations is None:
        metrics = getattr(result, "metrics", None)
        if metrics is None:
            return

        if accumulated_usage is None:
            accumulated_usage = getattr(metrics, "accumulated_usage", None)
            if accumulated_usage is None:
                accumulated_usage = getattr(metrics, "accumulatedUsage", None)

        cycle_durations = getattr(metrics, "cycle_durations", None)

    total_tokens = _extract_metric_value(accumulated_usage, "totalTokens")
    duration_seconds = None
    if isinstance(cycle_durations, list) and cycle_durations:
        duration_seconds = float(sum(cycle_durations))

    if total_tokens is not None:
        strands_tokens_total.labels(agent_name=agent_name).inc(total_tokens)
    if duration_seconds is not None:
        strands_duration_seconds.labels(agent_name=agent_name).observe(duration_seconds)


def _build_retry_note(
    *,
    attempt: int,
    validation_error: str,
    raw_output: str | None,
) -> str:
    trimmed_error = validation_error.strip()[:MAX_RETRY_FIELD_CHARS]
    note = (
        f"Attempt {attempt} failed validation. "
        f"Fix the output so it is valid JSON and satisfies this error: {trimmed_error}."
    )
    if raw_output:
        note += f"\nPrevious invalid output:\n{raw_output[:MAX_RETRY_FIELD_CHARS]}"
    return note


def _run_task_with_retries(
    *,
    build_graph: Callable[[dict[str, Any]], tuple[Any, str]],
    base_context: dict,
    build_prompt: Callable[[dict[str, Any]], str],
    normalize_output,
    validate_output,
):
    retry_context = dict(base_context)
    last_raw_output = None
    last_error = None

    for attempt in range(1, MAX_LLM_ATTEMPTS + 1):
        prompt = build_prompt(retry_context)
        graph, target_node_id = build_graph(retry_context)
        try:
            result = graph(prompt)
        except Exception as exc:
            last_error = str(exc)
            retry_context["retry_note"] = _build_retry_note(
                attempt=attempt,
                validation_error=last_error,
                raw_output=last_raw_output,
            )
            continue

        _record_strands_metrics(target_node_id, result, target_node_id)

        raw_output = _extract_graph_node_output(result, target_node_id)
        cleaned_raw_output = _clean_raw_output(raw_output)
        normalized_output = normalize_output(_parse_json_output(raw_output))
        validation_error = validate_output(normalized_output)
        if not validation_error:
            return {
                "parsed_output": normalized_output,
                "raw_output": cleaned_raw_output,
                "source": "llm",
                "error_message": None,
                "attempts": attempt,
            }

        last_raw_output = cleaned_raw_output
        last_error = validation_error
        retry_context["retry_note"] = _build_retry_note(
            attempt=attempt,
            validation_error=validation_error,
            raw_output=cleaned_raw_output,
        )

    return {
        "parsed_output": None,
        "raw_output": last_raw_output,
        "source": "llm_failed_after_retries",
        "error_message": last_error,
        "attempts": MAX_LLM_ATTEMPTS,
    }


def _build_evaluation_graph(context: dict[str, Any]) -> tuple[Any, str]:
    question_type = context["question_type"]
    agents = build_evaluator_agents(
        context,
        db=context.get("db"),
        session_id=context.get("session_id"),
    )
    builder = GraphBuilder()
    builder.add_node(agents[question_type], question_type)
    builder.set_entry_point(question_type)
    builder.set_max_node_executions(1)
    builder.set_execution_timeout(120)
    return builder.build(), question_type


def _build_synthesis_graph(
    context: dict[str, Any],
    *,
    db: Session | None = None,
    session_id: str | None = None,
) -> tuple[Any, str]:
    agents = build_evaluator_agents(context, db=db, session_id=session_id)
    builder = GraphBuilder()
    builder.add_node(agents["synthesizer"], "synthesizer")
    builder.set_entry_point("synthesizer")
    builder.set_max_node_executions(1)
    builder.set_execution_timeout(180)
    return builder.build(), "synthesizer"


def _build_review_graph(
    context: dict[str, Any],
    *,
    db: Session | None = None,
    session_id: str | None = None,
) -> tuple[Any, str]:
    agents = build_evaluator_agents(context, db=db, session_id=session_id)
    builder = GraphBuilder()
    builder.add_node(agents["reviewer"], "reviewer")
    builder.set_entry_point("reviewer")
    builder.set_max_node_executions(1)
    builder.set_execution_timeout(120)
    return builder.build(), "reviewer"


def run_crewai_evaluation(question_type: str, context: dict) -> dict:
    if not settings.llm_enabled:
        return {
            "parsed_output": None,
            "raw_output": None,
            "source": "llm_disabled",
            "error_message": "LLM evaluation is disabled.",
        }
    evaluation_result = _run_task_with_retries(
        build_graph=_build_evaluation_graph,
        base_context=context,
        build_prompt=build_evaluation_prompt,
        normalize_output=_normalize_evaluator_output,
        validate_output=lambda payload: _validate_evaluator_output(
            payload,
            context.get("rubric_keys", []),
        ),
    )
    if not evaluation_result.get("parsed_output"):
        return evaluation_result

    review_context = dict(context)
    review_context["evaluator_output"] = evaluation_result["parsed_output"]
    review_result = _run_task_with_retries(
        build_graph=lambda retry_context: _build_review_graph(
            retry_context,
            db=context.get("db"),
            session_id=context.get("session_id"),
        ),
        base_context=review_context,
        build_prompt=build_review_prompt,
        normalize_output=_normalize_review_output,
        validate_output=lambda payload: _validate_review_output(
            payload,
            context.get("rubric_keys", []),
        ),
    )
    if review_result.get("parsed_output", {}).get("final_output"):
        return {
            "parsed_output": review_result["parsed_output"]["final_output"],
            "raw_output": evaluation_result.get("raw_output"),
            "source": "llm_reviewed",
            "error_message": None,
        }

    return {
        "parsed_output": evaluation_result["parsed_output"],
        "raw_output": evaluation_result.get("raw_output"),
        "source": "llm_review_failed",
        "error_message": review_result.get("error_message"),
    }


def run_crewai_synthesis(
    context: dict,
    *,
    db: Session | None = None,
    session_id: str | None = None,
) -> dict:
    if not settings.llm_enabled:
        return {
            "parsed_output": None,
            "raw_output": None,
            "source": "llm_disabled",
            "error_message": "LLM synthesis is disabled.",
        }
    return _run_task_with_retries(
        build_graph=lambda retry_context: _build_synthesis_graph(
            retry_context,
            db=db,
            session_id=session_id,
        ),
        base_context=context,
        build_prompt=build_synthesis_prompt,
        normalize_output=_normalize_synthesis_output,
        validate_output=_validate_synthesis_output,
    )
