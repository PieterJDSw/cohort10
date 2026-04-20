from __future__ import annotations

from pathlib import Path
from typing import Any

from strands import Agent
from strands.models.openai import OpenAIModel
from sqlalchemy.orm import Session

from app.config import settings
from app.tools.ai_tools import build_compute_ai_usage_metrics_tool
from app.tools.code_runner_tools import build_run_python_tests_tool
from app.tools.question_tools import build_load_question_evidence_tool
from app.tools.score_tools import build_aggregate_dimension_scores_tool
from app.tools.session_tools import (
    build_load_coding_ai_transcript_tool,
    build_load_dimension_evidence_tool,
)

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _build_agent_tools(
    context: dict[str, Any] | None,
    *,
    db: Session | None = None,
    session_id: str | None = None,
) -> dict[str, list[Any]]:
    tools: dict[str, list[Any]] = {
        "coding": [],
        "theory": [],
        "architecture": [],
        "culture": [],
        "ai_fluency": [],
        "reviewer": [],
        "synthesizer": [],
    }
    if not context or not settings.llm_tool_use_enabled:
        return tools

    if context.get("question_type") == "coding":
        tools["coding"].append(
            build_run_python_tests_tool(
                submission_code=str(context.get("submission", "") or ""),
                metadata=context.get("code_metadata") or {},
            )
        )

    if db is not None and context.get("session_question_id"):
        question_evidence_tool = build_load_question_evidence_tool(
            db=db,
            session_question_id=context["session_question_id"],
        )
        for agent_name in ("theory", "architecture", "culture", "ai_fluency"):
            tools[agent_name].append(question_evidence_tool)

    if context.get("question_type") == "ai_fluency":
        tools["ai_fluency"].append(
            build_compute_ai_usage_metrics_tool(ai_logs=context.get("ai_logs") or [])
        )
        if session_id and db is not None:
            tools["ai_fluency"].append(
                build_load_coding_ai_transcript_tool(db=db, session_id=session_id)
            )

    if session_id and db is not None:
        tools["synthesizer"].append(
            build_load_dimension_evidence_tool(db=db, session_id=session_id)
        )

    if context.get("scored_questions"):
        tools["synthesizer"].append(
            build_aggregate_dimension_scores_tool(
                scored_questions=context["scored_questions"]
            )
        )

    return tools


def build_llm_model() -> OpenAIModel | None:
    if not settings.llm_enabled:
        return None

    return OpenAIModel(
        client_args={
            "api_key": settings.llm_api_key,
            "base_url": settings.llm_base_url,
        },
        model_id=settings.model_name,
    )


def _build_system_prompt(*, role: str, goal: str, prompt_name: str) -> str:
    return (
        f"Role: {role}\n"
        f"Goal: {goal}\n"
        f"Instructions:\n{_prompt(prompt_name)}"
    )


def build_evaluator_agents(
    context: dict[str, Any] | None = None,
    *,
    db: Session | None = None,
    session_id: str | None = None,
) -> dict[str, Agent]:
    model = build_llm_model()
    common: dict[str, Any] = {}
    if model is not None:
        common["model"] = model
    agent_tools = _build_agent_tools(context, db=db, session_id=session_id)

    return {
        "coding": Agent(
            name="coding_evaluator",
            system_prompt=_build_system_prompt(
                role="Coding Evaluator",
                goal="Assess coding submissions against the rubric and return structured JSON.",
                prompt_name="coding_eval.txt",
            ),
            tools=agent_tools["coding"],
            **common,
        ),
        "theory": Agent(
            name="theory_evaluator",
            system_prompt=_build_system_prompt(
                role="Theory Evaluator",
                goal="Assess theory answers and return structured JSON.",
                prompt_name="theory_eval.txt",
            ),
            tools=agent_tools["theory"],
            **common,
        ),
        "architecture": Agent(
            name="architecture_evaluator",
            system_prompt=_build_system_prompt(
                role="Architecture Evaluator",
                goal="Assess architecture answers and return structured JSON.",
                prompt_name="architecture_eval.txt",
            ),
            tools=agent_tools["architecture"],
            **common,
        ),
        "culture": Agent(
            name="culture_evaluator",
            system_prompt=_build_system_prompt(
                role="Culture Evaluator",
                goal="Assess culture answers and return structured JSON.",
                prompt_name="culture_eval.txt",
            ),
            tools=agent_tools["culture"],
            **common,
        ),
        "ai_fluency": Agent(
            name="ai_fluency_evaluator",
            system_prompt=_build_system_prompt(
                role="AI Fluency Evaluator",
                goal="Assess AI fluency answers and return structured JSON.",
                prompt_name="ai_fluency_eval.txt",
            ),
            tools=agent_tools["ai_fluency"],
            **common,
        ),
        "synthesizer": Agent(
            name="synthesizer",
            system_prompt=_build_system_prompt(
                role="Synthesizer",
                goal="Synthesize all evidence into a concise final recommendation JSON payload.",
                prompt_name="synthesis.txt",
            ),
            tools=agent_tools["synthesizer"],
            **common,
        ),
        "reviewer": Agent(
            name="evaluation_reviewer",
            system_prompt=_build_system_prompt(
                role="Evaluation Reviewer",
                goal="Review evaluator outputs for fairness, evidence alignment, and rubric consistency.",
                prompt_name="reviewer_eval.txt",
            ),
            tools=agent_tools["reviewer"],
            **common,
        ),
    }
