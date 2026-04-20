# Docs Map

Use this folder as the entry point for project documentation.

## Start Here

- [Startup Guide](./STARTUP.md)
  Current local and Docker startup instructions, service URLs, credentials, queues, and observability notes.

- [Scaling And Secure Code Execution](./SCALING_AND_SECURE_CODE_EXECUTION.md)
  Current scaling gaps, target worker split, and the recommended direction for isolating code execution.

- [Diagrams Index](./diagrams/README.md)
  Entry point for all Mermaid diagrams.

## Current-State Diagrams

- [Current Runtime Architecture](./diagrams/current-runtime-architecture.md)
  What is actually deployed today in Docker Compose.

- [Current Observability Architecture](./diagrams/current-observability-architecture.md)
  How metrics and logs currently flow through Prometheus, Alloy, Loki, and Grafana.

- [Agent Graph](./diagrams/agent-graph.md)
  The current Strands evaluator, reviewer, and synthesizer wiring.

- [Conversation And Reviewer Flow](./diagrams/conversation-flow.md)
  The current submission, evaluation, review, and finalization flow.

- [Relational Data Model](./diagrams/relational-data-model.md)
  The current SQLAlchemy-backed relational model.

## Target-State Architecture

- [Scalable Architecture Overview](./diagrams/scalable-architecture.md)
  High-level target architecture for a future worker-based system.

- [Production Deployment Architecture](./diagrams/production-deployment-architecture.md)
  Target production deployment view with platform concerns and resilience.

## How To Use This Folder

- If you want to understand what is built now, start with:
  - [Startup Guide](./STARTUP.md)
  - [Current Runtime Architecture](./diagrams/current-runtime-architecture.md)
  - [Current Observability Architecture](./diagrams/current-observability-architecture.md)

- If you want to understand where the system is heading, then read:
  - [Scaling And Secure Code Execution](./SCALING_AND_SECURE_CODE_EXECUTION.md)
  - [Scalable Architecture Overview](./diagrams/scalable-architecture.md)
  - [Production Deployment Architecture](./diagrams/production-deployment-architecture.md)

