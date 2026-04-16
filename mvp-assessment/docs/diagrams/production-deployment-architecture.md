# Production Deployment Architecture

This diagram focuses on how the system should be deployed for real-world traffic, resilience, scaling, and operational visibility.

```mermaid
flowchart LR
    subgraph EDGE["Edge and ingress"]
        USER["Candidate / recruiter traffic"]
        CDN["CDN"]
        WAF["WAF + rate limiting"]
        LB["Load balancer / ingress"]
    end

    subgraph PLATFORM["Application platform"]
        API["API pods / containers"]
        WORKERS["Worker pools<br/>evaluation, review, synthesis, AI-helper"]
        AUTOSCALE["Horizontal autoscaling"]
    end

    subgraph MESSAGING["Messaging"]
        QUEUES["Work queues"]
        DLQS["Dead letter queues"]
        REPLAY["Replay / redrive jobs"]
    end

    subgraph AI["AI execution"]
        AGENTS["Strands agent runtime"]
        MODELGW["Model gateway"]
        LLM["LLM endpoint(s)"]
        CACHE["Redis cache"]
    end

    subgraph DATA["Data layer"]
        DB["PostgreSQL primary"]
        REPLICAS["Read replicas"]
        OBJECTS["Object storage"]
        BACKUP["Backups + recovery"]
    end

    subgraph OPS["Observability and security"]
        OBS["Logs + metrics + traces + dashboards + alerting"]
        SECRETS["Secrets / KMS"]
    end

    USER --> CDN --> WAF --> LB --> API
    API --> QUEUES
    API --> DB
    API --> REPLICAS
    API --> CACHE

    QUEUES --> WORKERS
    WORKERS -. failed jobs .-> DLQS
    DLQS --> REPLAY --> QUEUES

    WORKERS --> AGENTS --> MODELGW --> LLM
    WORKERS --> CACHE
    WORKERS --> DB
    WORKERS --> OBJECTS

    AUTOSCALE --> API
    AUTOSCALE --> WORKERS

    DB --> BACKUP
    OBJECTS --> BACKUP
    REPLICAS --> API

    API --> OBS
    WORKERS --> OBS
    QUEUES --> OBS
    DB --> OBS
    CACHE --> OBS
    MODELGW --> OBS

    API --> SECRETS
    WORKERS --> SECRETS
    MODELGW --> SECRETS

    style PLATFORM fill:#f3f6ff,stroke:#6b7cff,color:#333
    style MESSAGING fill:#fff7e6,stroke:#d99600,color:#333
    style AI fill:#e2f0d9,stroke:#6aa84f,color:#333
    style DATA fill:#f7e6ff,stroke:#9b59b6,color:#333
    style OPS fill:#eef7ee,stroke:#3d8b40,color:#333
```

What this deployment view is making explicit:

- API and worker compute scale independently.
- Queues isolate burst traffic from slow downstream processing.
- DLQs and replay jobs are part of the default failure path.
- Redis sits near the agent runtime for hot reusable data and coordination.
- Read-heavy result and audit traffic should lean on replicas, not the primary database.
- Observability, backups, and secrets management are core platform pieces.

Production checks worth keeping in mind:

- Separate queues by workload type so synthesis cannot starve evaluation.
- Make submission, evaluation, and finalization flows idempotent.
- Put alarms on queue age, DLQ depth, worker failure rate, model error rate, DB saturation, and cache health.
- Keep final scores and session recommendations out of cross-candidate cache reuse.
