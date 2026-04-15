# Startup Guide

This project can be started in two ways:

1. with Docker Compose for the full stack
2. with `uv` and `npm` for local development

## Docker Compose

Run this from the parent folder that contains `docker-compose.yml`:

```powershell
cd C:\Users\piete\OneDrive\Desktop\parote
docker compose up --build
```

If port `8000` is already in use on your machine:

```powershell
cd C:\Users\piete\OneDrive\Desktop\parote
$env:BACKEND_PORT="8002"
docker compose up --build
```

Services:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000` by default
- backend health: `http://localhost:8000/health` by default
- postgres: `localhost:5432`
- local vLLM OpenAI-compatible endpoint: `http://localhost:8001/v1`

What happens on backend startup:

- Alembic migrations are applied automatically
- the default question bank is inserted if the database is empty
- CrewAI is configured to use the local `vllm` Qwen model, not the OpenAI API

Optional services:

- `docker compose --profile queue up --build` to include Redis

## Local Development

### Backend

```powershell
cd C:\Users\piete\OneDrive\Desktop\parote\mvp-assessment\backend
uv sync
uv run python app\create_tables.py
uv run python app\seed_questions.py
uv run uvicorn app.main:app --reload
```

The backend `.env` already contains a local Postgres URL:

```env
DATABASE_URL=postgresql+psycopg://assessment_user:assessment_pass@localhost:5432/assessment_db
OPENAI_API_BASE=http://localhost:8001/v1
MODEL_NAME=google/gemma-4-E2B-it
LLM_TOOL_USE_ENABLED=true
```

### Frontend

```powershell
cd C:\Users\piete\OneDrive\Desktop\parote\mvp-assessment\frontend
npm install
npm run dev
```

If you need a different backend host, create `frontend/.env` with:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Recommended Run Order

1. Start Postgres with Docker Compose or your local Postgres instance.
2. Start the backend so migrations and question seeding run.
3. Start the frontend.
4. Open `http://localhost:5173`.

## Notes

- The MVP code runner supports Python only.
- The default LLM path is the local `vllm` container serving `google/gemma-4-E2B-it`.
- Strands tool calling is enabled by default via `LLM_TOOL_USE_ENABLED=true`.
- If the local LLM is unavailable, the backend still falls back to deterministic local evaluation so the flow keeps working.
