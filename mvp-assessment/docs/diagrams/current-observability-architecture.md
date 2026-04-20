# Current Observability Architecture

This diagram shows the observability wiring that is actually implemented today.

```mermaid
flowchart LR
    subgraph APP["Application and platform services"]
        BACKEND["FastAPI backend<br/>JSON logs + /metrics"]
        AGENT["Agent FastAPI backend<br/>JSON logs + /metrics"]
        PROM["Prometheus"]
        ALLOY["Grafana Alloy"]
        LOKI["Loki"]
        GRAFANA["Grafana"]
    end

    subgraph METRICS["Prometheus scrape targets"]
        BEM["backend:8000/metrics"]
        AEM["agent-backend:8000/metrics"]
        PM["prometheus:9090/metrics"]
        LM["loki:3100/metrics"]
        AM["alloy:12345/metrics"]
        GM["grafana:3000/metrics"]
    end

    subgraph LOGS["Container log path"]
        DOCKER["Docker container stdout/stderr"]
        LABELS["Alloy relabels<br/>service_name, compose_service,<br/>container_name, stack"]
    end

    subgraph UI["Operator view"]
        DASH["Assessment Observability dashboard"]
        LOGEXP["Loki log exploration"]
    end

    BACKEND --> BEM --> PROM
    AGENT --> AEM --> PROM
    PROM --> PM
    LOKI --> LM --> PROM
    ALLOY --> AM --> PROM
    GRAFANA --> GM --> PROM

    BACKEND --> DOCKER
    AGENT --> DOCKER
    PROM --> DOCKER
    LOKI --> DOCKER
    GRAFANA --> DOCKER
    ALLOY --> DOCKER

    DOCKER --> ALLOY
    ALLOY --> LABELS --> LOKI

    PROM --> GRAFANA
    LOKI --> GRAFANA
    GRAFANA --> DASH
    GRAFANA --> LOGEXP

    style APP fill:#eef4ff,stroke:#5b7cfa,color:#333
    style METRICS fill:#eaf7ea,stroke:#4b9b4b,color:#333
    style LOGS fill:#fff7e6,stroke:#d99600,color:#333
    style UI fill:#f3eefc,stroke:#7a4ec7,color:#333
```

What is implemented today:

- The candidate backend and the agent backend both expose Prometheus metrics on `/metrics`.
- Prometheus scrapes both backends, Prometheus itself, Loki, Alloy, and Grafana.
- Both backends write structured JSON logs to stdout.
- Alloy reads Docker container logs, adds labels, and forwards them to Loki.
- Grafana is provisioned with `Prometheus` and `Loki` datasources on startup.
- The starter dashboard is `Assessment Observability`.

Important current details:

- There is no Tempo or tracing pipeline in the current build.
- Strands logs flow through the agent-backend logger and reach Loki as agent-backend container logs.
- The current Strands dashboard panels are based on:
  - `assessment_strands_tokens_total`
  - `assessment_strands_duration_seconds`
