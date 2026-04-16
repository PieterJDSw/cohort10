# Agent Graph

This diagram reflects the current crew implementation in `app/crew/agents.py` and `app/crew/crew.py`.

```mermaid
flowchart LR
    subgraph ENTRY["Crew runtime wrappers"]
        EVALRUN["run_crewai_evaluation(question_type, context)"]
        SYNRUN["run_crewai_synthesis(context)"]
        RETRY["Retry wrapper<br/>max 3 attempts"]
        PARSE["Clean output<br/>JSON parse / repair / normalize / validate"]
    end

    subgraph LLM["Strands / OpenAI Model"]
        MODEL["OpenAIModel<br/>settings.model_name"]
    end

    subgraph AGENTS["Evaluator Crew"]
        CODING["coding_evaluator"]
        THEORY["theory_evaluator"]
        ARCH["architecture_evaluator"]
        CULTURE["culture_evaluator"]
        AI["ai_fluency_evaluator"]
        REVIEWER["evaluation_reviewer"]
        SYNTH["synthesizer"]
    end

    subgraph TOOLS["Dynamic tool injection"]
        CODETEST["run_python_tests_tool<br/>coding only"]
        QUESTIONEVIDENCE["load_question_evidence_tool<br/>session_question_id"]
        AILOGS["compute_ai_usage_metrics_tool<br/>ai_fluency only"]
        CODINGTRANSCRIPT["load_coding_ai_transcript_tool<br/>ai_fluency only"]
        DIMEVIDENCE["load_dimension_evidence_tool<br/>synthesizer only"]
        AGGSCORES["aggregate_dimension_scores_tool<br/>synthesizer only"]
    end

    EVALRUN --> RETRY
    SYNRUN --> RETRY
    RETRY --> CODING
    RETRY --> THEORY
    RETRY --> ARCH
    RETRY --> CULTURE
    RETRY --> AI
    RETRY --> REVIEWER
    RETRY --> SYNTH

    MODEL --> CODING
    MODEL --> THEORY
    MODEL --> ARCH
    MODEL --> CULTURE
    MODEL --> AI
    MODEL --> REVIEWER
    MODEL --> SYNTH

    CODETEST --> CODING
    QUESTIONEVIDENCE --> THEORY
    QUESTIONEVIDENCE --> ARCH
    QUESTIONEVIDENCE --> CULTURE
    QUESTIONEVIDENCE --> AI
    AILOGS --> AI
    CODINGTRANSCRIPT --> AI
    DIMEVIDENCE --> SYNTH
    AGGSCORES --> SYNTH

    CODING --> PARSE
    THEORY --> PARSE
    ARCH --> PARSE
    CULTURE --> PARSE
    AI --> PARSE
    REVIEWER --> PARSE
    SYNTH --> PARSE

    style REVIEWER fill:#fff3cd,stroke:#d39e00,color:#333
    style SYNTH fill:#d1ecf1,stroke:#0c5460,color:#333
    style CODING fill:#e2f0d9,stroke:#6aa84f,color:#333
    style THEORY fill:#e2f0d9,stroke:#6aa84f,color:#333
    style ARCH fill:#e2f0d9,stroke:#6aa84f,color:#333
    style CULTURE fill:#e2f0d9,stroke:#6aa84f,color:#333
    style AI fill:#e2f0d9,stroke:#6aa84f,color:#333
```

What this shows:

- The crew is made of five evaluator agents, one reviewer agent, and one synthesizer.
- Each agent is built with the same OpenAI-backed Strands model when LLMs are enabled.
- Tools are injected per context, not globally.
- Each invocation is a single-node `GraphBuilder` execution today, not a multi-step in-process agent mesh.
- The reviewer is a second-pass gate on evaluator output, not a separate human step in the current code.
- Outputs are cleaned, JSON-repaired, normalized, and validated before they are accepted.
