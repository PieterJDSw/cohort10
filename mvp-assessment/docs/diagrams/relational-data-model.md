# Relational Data Model

This ER diagram is based on the SQLAlchemy models and Alembic migrations in `app/models` and `app/migrations`.

```mermaid
erDiagram
    CANDIDATES {
        string id PK
        string full_name
    }

    TEST_SESSIONS {
        string id PK
        string candidate_id FK
        string status
        datetime started_at
        datetime completed_at
    }

    QUESTIONS {
        string id PK
        string type
        string title
        text prompt
        string difficulty
        json rubric_json
        json metadata_json
        boolean is_active
    }

    SESSION_QUESTIONS {
        string id PK
        string session_id FK
        string question_id FK
        int sequence_no
        string status
    }

    SUBMISSIONS {
        string id PK
        string session_question_id FK
        string submission_type
        text text_answer
        text code_answer
        string language
    }

    AI_INTERACTIONS {
        string id PK
        string session_question_id FK
        text user_message
        text ai_response
    }

    EVALUATOR_RUNS {
        string id PK
        string session_question_id FK
        string evaluator_type
        string source
        json output_json
        text raw_output
        text error_message
        float confidence
    }

    DIMENSION_SCORES {
        string id PK
        string session_id FK
        string dimension_name
        float score
        float confidence
        json evidence_json
    }

    FINAL_REPORTS {
        string id PK
        string session_id FK
        string recommendation
        text summary
        json chart_payload
        string source
        text raw_output
        text error_message
    }

    CANDIDATES ||--o{ TEST_SESSIONS : has
    TEST_SESSIONS ||--o{ SESSION_QUESTIONS : contains
    QUESTIONS ||--o{ SESSION_QUESTIONS : assigned_to
    SESSION_QUESTIONS ||--o{ SUBMISSIONS : receives
    SESSION_QUESTIONS ||--o{ AI_INTERACTIONS : logs
    SESSION_QUESTIONS ||--o{ EVALUATOR_RUNS : stores
    TEST_SESSIONS ||--o{ DIMENSION_SCORES : aggregates
    TEST_SESSIONS ||--|| FINAL_REPORTS : finalizes
```

Key constraints and behavior:

- `session_questions` enforces one ordered row per `(session_id, sequence_no)`.
- `final_reports.session_id` is unique, so there is only one final report per session.
- `submissions`, `ai_interactions`, and `evaluator_runs` are used as append-style history tables for each session question by the current service layer.
- `dimension_scores` is rebuilt from the final session scoring pass.
