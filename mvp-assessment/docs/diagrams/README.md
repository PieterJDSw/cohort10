# Diagrams

This folder contains Mermaid diagrams for the assessment system.

- [Current runtime architecture](./current-runtime-architecture.md)
- [Agent graph](./agent-graph.md)
- [Conversation and reviewer flow](./conversation-flow.md)
- [Scalable architecture overview](./scalable-architecture.md)
- [Production deployment architecture](./production-deployment-architecture.md)
- [Relational data model](./relational-data-model.md)

## Implemented Vs Target

Implemented today:

- [Current runtime architecture](./current-runtime-architecture.md)
- [Current observability architecture](./current-observability-architecture.md)
- [Agent graph](./agent-graph.md)
- [Conversation and reviewer flow](./conversation-flow.md)
- [Relational data model](./relational-data-model.md)

Target / future-state architecture:

- [Scalable architecture overview](./scalable-architecture.md)
- [Production deployment architecture](./production-deployment-architecture.md)

Diagram intent:

- `current-runtime-architecture.md`, `current-observability-architecture.md`, `agent-graph.md`, `conversation-flow.md`, and `relational-data-model.md` describe the current implementation.
- `scalable-architecture.md` and `production-deployment-architecture.md` describe the target future-state architecture, not the current Docker Compose stack.

These diagrams were reviewed against the current backend implementation in:

- `backend/app/crew/agents.py`
- `backend/app/crew/crew.py`
- `backend/app/crew/flow.py`
- `backend/app/domain/services/*.py`
- `backend/app/models/*.py`
- `backend/app/migrations/versions/*.py`
