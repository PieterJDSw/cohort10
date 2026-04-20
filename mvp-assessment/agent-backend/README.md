# Backend

FastAPI backend for the MVP developer assessment platform.

Key behaviors:

- runs Alembic migrations on startup
- seeds the default question bank when the database is empty
- exposes the assessment, dashboard, and result APIs
- emits structured logs to stdout using Python's standard `logging` module

Logging:

- default format is JSON for production-friendly structured logging
- request middleware adds request-scoped context such as `request_id`, method, and path
- configure with `LOG_LEVEL` and `LOG_FORMAT`
- supported formats: `json`, `plain`
