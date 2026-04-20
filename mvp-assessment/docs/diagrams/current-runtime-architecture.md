# Current Runtime Architecture

This diagram shows what is actually deployed today in `docker-compose.yml` and how the current runtime behaves.

```mermaid
flowchart LR
    subgraph CLIENT["User-facing runtime"]
        USER["Candidate / recruiter browser"]
        FRONTEND["Frontend<br/>Vite SPA"]
    end

    subgraph APP["Candidate API runtime"]
        BACKEND["FastAPI backend"]
        ROUTES["Candidate, session, submission,<br/>AI, results, dashboard routes"]
        SERVICES["SessionService / SubmissionService / ResultService"]
        CODERUN["Python code runner<br/>runs inline in backend"]
    end

    subgraph AGENT["Agent runtime"]
        AGENTAPI["Agent FastAPI service"]
        CONSUMERS["RabbitMQ consumers<br/>evaluate + synthesis"]
        CREW["Strands evaluation and synthesis flow"]
    end

    subgraph STATE["State and messaging"]
        POSTGRES["PostgreSQL"]
        RABBIT["RabbitMQ"]
        EVALQ["assessment.evaluate"]
        SYNQ["assessment.synthesis"]
        DLQ["assessment.dead_letter"]
    end

    subgraph MODEL["Model runtime"]
        VLLM["vLLM OpenAI-compatible endpoint"]
    end

    subgraph OBS["Observability runtime"]
        METRICS["/metrics endpoint"]
        PROM["Prometheus"]
        ALLOY["Grafana Alloy"]
        LOKI["Loki"]
        GRAFANA["Grafana"]
    end

    USER --> FRONTEND --> BACKEND
    BACKEND --> ROUTES --> SERVICES

    SERVICES --> POSTGRES
    SERVICES --> CODERUN
    SERVICES --> RABBIT
    RABBIT --> EVALQ
    RABBIT --> SYNQ
    RABBIT --> DLQ
    EVALQ --> CONSUMERS
    SYNQ --> CONSUMERS
    CONSUMERS --> AGENTAPI --> CREW
    CREW --> POSTGRES
    CREW --> VLLM

    BACKEND --> METRICS --> PROM
    AGENTAPI --> PROM
    BACKEND --> ALLOY
    AGENTAPI --> ALLOY
    ALLOY --> LOKI
    PROM --> GRAFANA
    LOKI --> GRAFANA

    style APP fill:#eef4ff,stroke:#5b7cfa,color:#333
    style STATE fill:#fff7e6,stroke:#d99600,color:#333
    style MODEL fill:#eaf7ea,stroke:#4b9b4b,color:#333
    style OBS fill:#f3eefc,stroke:#7a4ec7,color:#333
```

What is true in the current runtime:

- The frontend talks directly to the FastAPI backend.
- The backend handles candidate/session HTTP requests and publishes RabbitMQ jobs.
- A separate `agent-backend` service consumes evaluation and synthesis jobs from RabbitMQ.
- Python code execution still happens inline in the backend process.
- RabbitMQ carries evaluation, synthesis, and dead-letter traffic between the API backend and the agent backend.
- Strands agents call the local `vllm` service through the OpenAI-compatible API.
- Prometheus scrapes both backends plus the observability services, Alloy ships container logs to Loki, and Grafana reads from Prometheus and Loki.
