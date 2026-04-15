from __future__ import annotations

import json

EVALUATOR_OUTPUT_SCHEMA = {
    "summary": "string",
    "rubric_scores": "object keyed by rubric dimension name with numeric 0-100 values",
    "strengths": ["string"],
    "weaknesses": ["string"],
    "red_flags": ["string"],
    "confidence": "number between 0 and 1",
}

SYNTHESIS_OUTPUT_SCHEMA = {
    "recommendation": "one of strong_hire, hire, mixed, no_hire",
    "summary": "string",
    "strengths": ["string"],
    "weaknesses": ["string"],
}

REVIEW_OUTPUT_SCHEMA = {
    "critique": "string",
    "final_output": EVALUATOR_OUTPUT_SCHEMA,
}

MAX_SIGNAL_ITEMS = 6
MAX_ITEM_CHARS = 220
MAX_SUMMARY_CHARS = 320


def _json_block(value) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _truncate_text(value: str, limit: int) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def _compact_string_list(values, *, limit: int = MAX_SIGNAL_ITEMS) -> list[str]:
    compacted: list[str] = []
    seen: set[str] = set()
    for item in values or []:
        text = _truncate_text(str(item), MAX_ITEM_CHARS)
        normalized = text.lower()
        if not text or normalized in seen:
            continue
        seen.add(normalized)
        compacted.append(text)
        if len(compacted) >= limit:
            break
    return compacted


def _compact_dimension_scores(values) -> list[dict]:
    compacted: list[dict] = []
    for item in values or []:
        if not isinstance(item, dict):
            continue
        compacted.append(
            {
                "dimension_name": item.get("dimension_name"),
                "score": item.get("score"),
                "confidence": item.get("confidence"),
            }
        )
    return compacted


def _compact_question_summaries(values) -> list[dict]:
    compacted: list[dict] = []
    for item in values or []:
        if not isinstance(item, dict):
            continue
        compacted.append(
            {
                "question_type": item.get("question_type"),
                "summary": _truncate_text(str(item.get("summary", "")), MAX_SUMMARY_CHARS),
                "strengths": _compact_string_list(item.get("strengths"), limit=2),
                "weaknesses": _compact_string_list(item.get("weaknesses"), limit=2),
            }
        )
    return compacted


def build_evaluation_prompt(context: dict) -> str:
    retry_note = context.get("retry_note")
    scoring_instruction = ""
    if context["question_type"] == "coding":
        scoring_instruction = (
            "For coding evaluations, treat the provided Code results as the source of truth for correctness. "
            "Do not invent passing tests or ignore failing tests.\n"
        )
    sections = [
        "Evaluate the candidate response.",
        f"Question type: {context['question_type']}",
        f"Question:\n{context['prompt']}",
        f"Rubric:\n{_json_block(context['rubric'])}",
        f"Submission:\n{context['submission']}",
    ]
    if context.get("code_metadata"):
        sections.append(f"Question metadata:\n{_json_block(context['code_metadata'])}")
    if context.get("ai_logs"):
        sections.append(f"AI interactions:\n{_json_block(context['ai_logs'])}")
    if context.get("code_results") is not None:
        sections.append(f"Code results:\n{_json_block(context['code_results'])}")
    sections.extend(
        [
            f"Required output schema:\n{_json_block(EVALUATOR_OUTPUT_SCHEMA)}",
            f"Rubric keys that must appear in rubric_scores:\n{_json_block(context['rubric_keys'])}",
            f"{scoring_instruction}Return JSON only.".strip(),
        ]
    )
    description = "\n".join(section for section in sections if section)
    if retry_note:
        description += f"\nRetry instructions:\n{retry_note}\nReturn repaired JSON only."
    return description


def build_review_prompt(context: dict) -> str:
    retry_note = context.get("retry_note")
    description = (
        "Review the evaluator output for fairness and evidence alignment.\n"
        f"Question type: {context['question_type']}\n"
        f"Question:\n{context['prompt']}\n"
        f"Rubric:\n{_json_block(context['rubric'])}\n"
        f"Rubric keys that must appear in rubric_scores:\n{_json_block(context['rubric_keys'])}\n"
        f"Candidate submission:\n{context['submission']}\n"
        f"Evaluator output to review:\n{_json_block(context['evaluator_output'])}\n"
    )
    if context.get("code_metadata"):
        description += f"Question metadata:\n{_json_block(context['code_metadata'])}\n"
    if context.get("ai_logs"):
        description += f"AI interactions:\n{_json_block(context['ai_logs'])}\n"
    if context.get("code_results") is not None:
        description += (
            "Code results are the source of truth for coding correctness.\n"
            f"Code results:\n{_json_block(context['code_results'])}\n"
        )
    description += (
        f"Required output schema:\n{_json_block(REVIEW_OUTPUT_SCHEMA)}\n"
        "Return JSON only. Keep `critique` brief. If the evaluator output is fair and well-supported, "
        "keep `final_output` materially the same. If it is unfair, overconfident, or inconsistent with the evidence, "
        "correct `final_output`."
    )
    if retry_note:
        description += f"\nRetry instructions:\n{retry_note}\nReturn repaired JSON only."
    return description


def build_synthesis_prompt(context: dict) -> str:
    retry_note = context.get("retry_note")
    compacted_question_summaries = _compact_question_summaries(context.get("scored_questions"))
    compacted_dimension_scores = _compact_dimension_scores(context.get("dimension_scores"))
    compacted_strengths = _compact_string_list(context.get("strengths"))
    compacted_weaknesses = _compact_string_list(context.get("weaknesses"))
    description = (
        "Synthesize evaluator evidence into a final hiring summary.\n"
        f"Question summaries:\n{_json_block(compacted_question_summaries)}\n"
        f"Dimension scores:\n{_json_block(compacted_dimension_scores)}\n"
        f"Strengths:\n{_json_block(compacted_strengths)}\n"
        f"Weaknesses:\n{_json_block(compacted_weaknesses)}\n"
        f"Required output schema:\n{_json_block(SYNTHESIS_OUTPUT_SCHEMA)}\n"
        "Return JSON only."
    )
    if retry_note:
        description += f"\nRetry instructions:\n{retry_note}\nReturn repaired JSON only."
    return description
