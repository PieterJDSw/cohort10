# Relational Data Model

This ER diagram is based on the SQLAlchemy models and Alembic migrations in `app/models` and `app/migrations`.

```mermaid
erDiagram
    CANDIDATES {
        string id PK
        string full_name
        datetime created_at
    }

    TEST_SESSIONS {
        string id PK
        string candidate_id FK
        string status
        datetime started_at
        datetime completed_at
        datetime created_at
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
        datetime created_at
    }

    SESSION_QUESTIONS {
        string id PK
        string session_id FK
        string question_id FK
        int sequence_no
        string status
        datetime created_at
    }

    SUBMISSIONS {
        string id PK
        string session_question_id FK
        string submission_type
        text text_answer
        text code_answer
        string language
        datetime created_at
    }

    AI_INTERACTIONS {
        string id PK
        string session_question_id FK
        text user_message
        text ai_response
        datetime created_at
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
        datetime created_at
    }

    DIMENSION_SCORES {
        string id PK
        string session_id FK
        string dimension_name
        float score
        float confidence
        json evidence_json
        datetime created_at
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
        datetime created_at
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
- `submissions`, `ai_interactions`, and `evaluator_runs` are append-only history tables for each session question.
- `dimension_scores` is rebuilt from the final session scoring pass.

