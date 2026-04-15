# Scaling And Secure Code Execution

This is how I would scale this MVP and make code execution safer over time.

Right now the app is simple:

- the frontend is a React/Vite SPA
- the backend is a FastAPI app
- Postgres stores sessions, questions, submissions, AI interactions, evaluator runs, scores, and final reports
- vLLM is used for AI assistance and evaluation
- Python code is executed directly inside the backend process

That last part is the biggest weakness. At the moment, the backend is acting as:

- API server
- orchestration layer
- evaluator
- code runner

That is acceptable for an MVP, but it is not how I would run this at scale.

## What I See As The Main Bottlenecks

The biggest issues in the current design are:

- code execution happens inside the API backend, which is both a security risk and a scaling problem
- `finish_session()` runs scoring and synthesis inline, so a user request can block on long evaluation work
- the backend is doing too many different jobs at once
- model latency and code execution latency can directly hurt API responsiveness
- adding more languages would make the backend image and execution path much more complex

## How I Would Scale It

I would scale this system in stages rather than redesigning everything at once.

### 1. Keep the API stateless and scale it horizontally

I would run multiple backend replicas behind a load balancer and keep Postgres as the source of truth for session state. I would also add proper connection pooling and make sure the hot foreign-key paths are indexed.

### 2. Move long-running work off the request path

I would stop doing heavy evaluation work inside the HTTP request cycle. In particular, I would change `finish_session()` so that it:

1. marks the session as submitted
2. enqueues a background scoring job
3. returns immediately

A worker can then run the evaluation flow, persist dimension scores and the final report, and update the session to `scored`.

### 3. Introduce a queue and workers

I would add a job queue for:

- session scoring
- code execution
- possibly AI helper generation later if needed

Redis is already present in `docker-compose.yml`, so it is a natural next step. The important part is not the exact queue product, but separating API traffic from background work.

### 4. Split responsibilities into clearer services

Once traffic grows, I would separate the platform into:

- an API service
- an evaluation worker
- a code execution worker
- a model service
- Postgres
- a queue

That separation matters because API capacity, evaluation capacity, and code execution capacity should not all be tied to one process.

## How I Would Handle Secure Code Execution

I would not keep executing candidate code inside the FastAPI process.

Even with restricted builtins, in-process `compile` and `exec` is not a strong isolation boundary. It also means one bad or expensive run can hurt the rest of the system.

Instead, I would move to this model:

1. the backend receives a code run request
2. the backend creates an execution job
3. an execution worker picks up the job
4. the worker runs the code in an isolated sandbox
5. the worker stores structured test results
6. the API returns or fetches those results

## Why I Would Use Firecracker

If I want to support untrusted code safely, Firecracker is a strong option because it gives a much better isolation boundary than running code directly in-process or in a general-purpose worker container.

What I like about Firecracker:

- stronger isolation for untrusted code
- good fit for short-lived per-run environments
- easier to enforce hard CPU, memory, filesystem, and network limits
- better path for supporting multiple languages cleanly

The tradeoff is extra operational complexity. Because of that, I would not start with the full Firecracker platform on day one unless I already knew this was heading toward real multi-user untrusted execution at scale.

## Practical Migration Path

This is the sequence I would follow.

### Step 1: Abstract code execution

I would replace the direct Python execution path in:

- [`backend/app/domain/services/submission_service.py`]
- [`backend/app/tools/code_runner_tools.py`]

with an execution service abstraction.

Initially I would support:

- `LocalPythonExecutionService` for compatibility
- `RemoteSandboxExecutionService` for the real isolated path

### Step 2: Make scoring asynchronous

I would move `finalize_session()` out of the request cycle and into a worker. That would let the UI poll for session completion instead of waiting for scoring inline.

### Step 3: Externalize Python execution first

Before adding more languages, I would first move Python execution out of process and into an isolated worker or sandbox. That gives me a safer foundation without changing the product surface too much.

### Step 4: Generalize the runner model

Right now the code runner is Python-specific. To support more languages, I would move from "run this Python function" to "run this language-specific test harness".

The backend should only care about:

- language
- runtime version
- resource limits
- result schema

Each runner should handle its own compile and test logic internally.

### Step 5: Add languages one at a time

I would start with:

1. Python
2. JavaScript / TypeScript
3. Java or Go

I would not add many runtimes until the sandbox model, logging, and failure handling are stable.

## What A Better Execution Contract Looks Like

Instead of assuming Python `entrypoint` metadata, I would evolve toward a runner contract that supports:

- source files
- runtime or language version
- compile command
- run command
- test specification
- resource limits

Each runner should return a common result shape such as:

- `status`
- `passed`
- `total`
- `results`
- `stdout`
- `stderr`
- `compile_error`
- `runtime_ms`
- `memory_kb`
- `sandbox_id`

That keeps the frontend and evaluator pipeline mostly stable even as runtimes change.

## Minimum Sandbox Controls I Would Require

Whether I use Firecracker immediately or not, I would require:

- CPU limits
- memory limits
- hard timeout
- no backend credentials inside the sandbox
- no direct database access
- no outbound internet by default
- isolated temporary filesystem
- process count limits
- output size limits

I would enforce those controls outside the candidate runtime, not trust the candidate code to behave.

## Bottom Line

If I wanted this app to handle more users and more load safely, I would make two big architectural changes first:

1. move code execution out of the API process and into isolated sandboxes
2. move scoring and synthesis onto background workers

After that, I would scale the API horizontally, keep Postgres as the source of truth, introduce a queue, and gradually move toward a worker-based architecture with Firecracker for secure multi-language execution.
