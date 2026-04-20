# Startup Guide

This project can be started in two ways:

1. with Docker Compose for the full runtime stack
2. with `uv` and `npm` for local development

## Docker Compose

Run this from the repo root that contains `docker-compose.yml`:

```powershell
cd C:\Users\piete\OneDrive\Documents\GitHub\cohort10
docker compose up --build
```

If port `8000` is already in use on your machine:

```powershell
cd C:\Users\piete\OneDrive\Documents\GitHub\cohort10
$env:BACKEND_PORT="8002"
docker compose up --build
```

### Core Services

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000` by default
- backend health: `http://localhost:8000/health`
- backend metrics: `http://localhost:8000/metrics`
- agent backend: `http://localhost:8002`
- agent backend health: `http://localhost:8002/health`
- agent backend metrics: `http://localhost:8002/metrics`
- postgres: `localhost:5432`
- RabbitMQ AMQP: `localhost:5672`
- RabbitMQ management UI: `http://localhost:15672`
- local vLLM OpenAI-compatible endpoint: `http://localhost:8001/v1`

### Observability Services

- Prometheus: `http://localhost:9090`
- Loki: `http://localhost:3100`
- Grafana Alloy metrics: `http://localhost:12345/metrics`
- Grafana: `http://localhost:3000`

Grafana credentials:

- username: `admin`
- password: `admin`

RabbitMQ credentials:

- username: `assessment`
- password: `assessment`

### What Happens On Backend Startup

- Alembic migrations are applied automatically
- the default question bank is inserted if the database is empty
- Strands agents are configured to use the local `vllm` OpenAI-compatible model endpoint
- structured JSON logging is enabled by default
- Prometheus metrics are exposed on `/metrics` from both backends
- the candidate backend publishes evaluation and synthesis work to RabbitMQ
- the agent backend consumes RabbitMQ evaluation and synthesis jobs and writes results back to Postgres

### Current Docker Compose Stack

- `postgres`
- `backend`
- `agent-backend`
- `frontend`
- `rabbitmq`
- `vllm`
- `prometheus`
- `loki`
- `alloy`
- `grafana`

### Queue Topology

RabbitMQ queues are declared lazily by the backend on first publish. They will appear in the RabbitMQ UI after an evaluation or synthesis event is triggered.

Expected queues:

- `assessment.evaluate`
- `assessment.synthesis`
- `assessment.dead_letter`

Expected exchanges:

- `assessment.events`
- `assessment.events.dlx`

## Local Development

### Backend

```powershell
cd C:\Users\piete\OneDrive\Documents\GitHub\cohort10\mvp-assessment\backend
uv sync
uv run uvicorn app.main:app --reload
```

The backend uses these important environment variables:

```env
DATABASE_URL=postgresql+psycopg://assessment_user:assessment_pass@localhost:5432/assessment_db
OPENAI_API_BASE=http://localhost:8001/v1
MODEL_NAME=google/gemma-4-E2B-it
LLM_ENABLED=true
LLM_TOOL_USE_ENABLED=true
LOG_LEVEL=INFO
LOG_FORMAT=json
STRANDS_LOG_LEVEL=DEBUG
RABBITMQ_ENABLED=true
RABBITMQ_URL=amqp://assessment:assessment@rabbitmq:5672/%2f
RABBITMQ_EXCHANGE=assessment.events
RABBITMQ_DEAD_LETTER_EXCHANGE=assessment.events.dlx
RABBITMQ_EVALUATE_QUEUE=evaluate
RABBITMQ_SYNTHESIS_QUEUE=synthesis
RABBITMQ_DEAD_LETTER_QUEUE=dead_letter
```

If you are running the backend locally outside Docker but still using Docker infrastructure, you will normally need to override some hostnames:

```env
DATABASE_URL=postgresql+psycopg://assessment_user:assessment_pass@localhost:5432/assessment_db
OPENAI_API_BASE=http://localhost:8001/v1
RABBITMQ_URL=amqp://assessment:assessment@localhost:5672/%2f
```

### Frontend

```powershell
cd C:\Users\piete\OneDrive\Documents\GitHub\cohort10\mvp-assessment\frontend
npm install
npm run dev
```

If you need a different backend host, create `frontend/.env` with:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Recommended Run Order

1. Start the Docker Compose stack from the repo root.
2. Wait for Postgres and RabbitMQ to come up.
3. Wait for the backend to finish migrations and question seeding.
4. Wait for the agent backend health endpoint to come up.
5. Open `http://localhost:5173`.
6. Open Grafana or RabbitMQ UI if you want to inspect logs, metrics, or queue traffic.

## Observability Notes

- backend and agent-backend logs are written to stdout as structured JSON
- Alloy tails container logs and ships them to Loki
- Prometheus scrapes backend, agent-backend, Alloy, Loki, Grafana, and Prometheus itself
- Grafana is provisioned with Prometheus and Loki datasources on startup
- there is no Tempo or OpenTelemetry tracing stack in the current build
- the starter Grafana dashboard is `Assessment Observability`
- the current Strands panels are `Strands Tokens (30m)` and `Strands Avg Duration By Agent`
- Strands logs are routed through the agent-backend logging pipeline and can be queried in Grafana via Loki

Example Loki query for backend logs:

```logql
{stack="assessment", service_name="backend"}
```

Example Loki query for agent-backend logs:

```logql
{stack="assessment", service_name="agent-backend"}
```

Example Loki query for Strands logs:

```logql
{stack="assessment", service_name="agent-backend"} | json | logger=~"strands.*"
```

## Notes

- the MVP code runner supports Python only
- the default LLM path is the local `vllm` container serving `google/gemma-4-E2B-it`
- Strands tool calling is enabled by default via `LLM_TOOL_USE_ENABLED=true`
- RabbitMQ now mediates evaluation and synthesis between the candidate backend and the agent backend
- the candidate backend returns quickly after publish; the agent backend performs the long-running Strands work asynchronously
- the dead letter queue is in place for worker failures
