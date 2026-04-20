# Conversation Flow

This diagram shows how a submission moves through the current system, including the reviewer pass, retry/validation behavior, and the session-finalization path.

```mermaid
flowchart TD
    USER["Candidate / participant"] --> API["Submission or AI-chat API"]
    API --> SS["SubmissionService"]

    SS --> SQ["Current session question"]

    SQ -->|text or code answer| SAVE["Save submission"]
    SQ -->|AI help chat| AICHAT["Generate hint response"]
    AICHAT --> SAVEAI["Save AIInteraction"]

    SAVE --> QUEUED["session_question.status = evaluation_queued"]
    SAVEAI --> EVIDENCE["AIInteraction stored as later evidence"]

    QUEUED --> EVALQ["Publish evaluate event<br/>RabbitMQ assessment.evaluate"]
    EVALQ --> WORKER["agent-backend evaluate consumer"]
    WORKER --> EVAL["status = evaluating<br/>evaluate_question()"]
    EVAL --> CTX["Build question context<br/>rubric, submission, ai_logs, code_results"]
    CTX --> RUN["run_crewai_evaluation()"]
    EVIDENCE --> CTX

    RUN --> EVALAGENT["Target evaluator agent<br/>coding / theory / architecture / culture / ai_fluency"]
    EVALAGENT --> CHECK1["clean / parse / repair / validate JSON"]
    CHECK1 --> REVIEW["evaluation_reviewer"]
    REVIEW -->|fair and supported| FINALOUTPUT["Reviewed evaluator JSON"]
    REVIEW -->|criticized or corrected| FINALOUTPUT["Reviewed evaluator JSON"]

    FINALOUTPUT --> CHECK2["validate reviewed payload"]
    CHECK2 --> PERSISTRUN["Save EvaluatorRun<br/>status = evaluated or completed"]
    PERSISTRUN --> SCORE["score_question()"]
    RUN -. exception or failed output .-> EVALDLQ["Publish dead letter<br/>RabbitMQ assessment.dead_letter"]
    SCORE --> RELEASE["If session.status = synthesis_requested<br/>and no evaluation jobs are still in flight,<br/>publish assessment.synthesis exactly once"]
    RELEASE --> RESP["Worker commit"]

    RESP --> DB1["evaluator_runs"]
    RESP --> DB2["submission / session state"]

    USER -->|finishes session| SESSIONAPI["SessionService.finish_session()"]
    SESSIONAPI --> MARK["Mark active/evaluated questions completed"]
    MARK --> FINREQ["session.status = synthesis_requested"]
    FINREQ --> READY{"Any question still<br/>evaluation_queued or evaluating?"}
    READY -->|yes| WAIT["Return immediately<br/>wait for last evaluate worker"]
    READY -->|no| SYNQ["Publish synthesis event<br/>RabbitMQ assessment.synthesis"]

    SYNQ --> SYNWORKER["agent-backend synthesis consumer"]
    SYNWORKER --> FINALIZE["status = synthesizing<br/>finalize_session()"]
    FINALIZE --> LOOP["Iterate ordered session_questions"]
    LOOP --> SCORED["reuse saved evaluator output<br/>or score no-submission questions"]
    SCORED --> DIM["aggregate_dimension_scores()"]
    DIM --> SYN["run_crewai_synthesis()"]
    SYN --> SYNAGENT["synthesizer"]
    SYNAGENT --> SYNCHECK["clean / parse / repair / validate synthesis JSON"]
    SYN -. exception or failed output .-> SYNDLQ["Publish dead letter<br/>RabbitMQ assessment.dead_letter"]
    SYNCHECK --> REPORT["Save FinalReport"]
    DIM --> DIMSAVE["Save DimensionScore rows"]
    REPORT --> OUT["Session status becomes scored"]

    style REVIEW fill:#fff3cd,stroke:#d39e00,color:#333
    style SYNAGENT fill:#d1ecf1,stroke:#0c5460,color:#333
    style EVALAGENT fill:#e2f0d9,stroke:#6aa84f,color:#333
```

Current behavior in plain terms:

- A submission is saved first.
- Only text and code submissions publish evaluation work to RabbitMQ immediately.
- AI helper chat is persisted as evidence and may influence later evaluation, but it does not itself trigger evaluation.
- The agent backend moves question status through `evaluation_queued -> evaluating -> evaluated` while processing.
- The evaluator agent produces a JSON rubric response.
- The reviewer agent checks that response for fairness, evidence alignment, and rubric consistency.
- The validated output is persisted as an `EvaluatorRun`.
- Finishing a session now sets `synthesis_requested`. The last successful evaluation worker releases synthesis when no evaluation jobs are still in flight.
- The actual evaluator and synthesizer work now runs in the separate `agent-backend` service, not in the candidate-facing backend.
- Failures in evaluation or synthesis publish a dead-letter envelope to `assessment.dead_letter`.
- Session completion fans out across all questions, then the synthesizer produces the final recommendation.
