# Solo Company Platform — Phase 1 Operator Guide

This guide describes how to configure, deploy, run, and troubleshoot the **Phase 1 (Single-Company MVP)** modular monolith.

---

## 1. System Overview & Architecture

The Phase 1 architecture is a single-company modular monolith composed of three primary services:
1. **`apps/web`**: A Next.js 16 React owner console built with App Router, TypeScript, and standard CSS design tokens.
2. **`apps/api`**: A Python FastAPI service hosting REST endpoints, domain validation, and the single-threaded Phase 1 LangGraph execution coordinator (`app/runtime/`).
3. **`infra/compose.yaml`**: A local PostgreSQL 17 container providing transactional storage for business domain tables and LangGraph checkpoint state.

### Execution Coordinator Guarantees
- **In-Process Sequential Execution**: An objective is transformed into a Chief of Staff plan, approved by the owner via an idempotency key, and executed sequentially across specialist agents (`marketing-specialist`, `operations-manager`, etc.).
- **State Persistence (ADR-003)**: LangGraph state checkpoints only contain JSON-safe IDs, routing flags, revision feedback, and pending outputs—never model clients, raw provider payloads, or database sessions.
- **Idempotency**: All state-mutating actions (`POST .../approve`, `POST .../retry`) require a unique UUID `Idempotency-Key` header. Re-submitting an existing key returns the existing run without spawning duplicate execution.

---

## 2. Prerequisites & Environment Setup

### Required Toolchain
- **Node.js** 22.x or later
- **pnpm** 11.x or later
- **Python** 3.12.x or later
- **uv** (fast Python package and environment manager)
- **Docker** and **Docker Compose**

### Workspace Bootstrap
Run the following commands from the repository root to initialize the JavaScript and Python development environments:

```bash
# 1. Install JavaScript workspace dependencies
pnpm install

# 2. Sync and create the Python virtual environment for the API
uv --directory apps/api sync
```

---

## 3. Environment & Configuration Reference

Create or inspect a `.env` file in the root directory (modeled after `.env.example`). The default settings operate out of the box using the local Docker PostgreSQL database and deterministic fake model adapter:

| Variable | Default Value | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/solo_company` | Primary SQLAlchemy application database URL |
| `LANGGRAPH_DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/solo_company` | Async connection string used by the LangGraph checkpointer |
| `RUNTIME_MODEL_BACKEND` | `fake` | Selects between the `fake` model adapter and the real `gemini` adapter |
| `GRAPH_VERSION` | `p1-v1` | Persisted graph version tag recorded on runs and checkpoints |
| `GEMINI_MODEL_ID` | `gemini-3.1-pro-preview` | Provider model ID used when `RUNTIME_MODEL_BACKEND=gemini` |
| `GEMINI_API_KEY` | *(empty)* | Optional Google Gemini API key; required only when calling real provider models |

> [!TIP]
> **No API Key Required for Local Dev**: Leaving `RUNTIME_MODEL_BACKEND=fake` allows you to develop, test, and demo the entire objective-to-artifact workflow without any external provider credentials or API costs.

---

## 4. Database & Migration Management

Before launching the API service, start the local database container and apply Alembic schema migrations:

```bash
# Start local PostgreSQL 17 in the background
docker compose -f infra/compose.yaml up -d

# Apply all pending database schema migrations
uv --directory apps/api run alembic upgrade head
```

### Useful Database Commands
- **Check Migration Status**: `uv --directory apps/api run alembic current`
- **Reset Database (Local Dev Only)**: `docker compose -f infra/compose.yaml down -v && docker compose -f infra/compose.yaml up -d && uv --directory apps/api run alembic upgrade head`

---

## 5. Starting Local Development Servers

Start the backend API and frontend web application in separate terminal windows:

```bash
# Terminal 1: Start FastAPI development server (http://localhost:8000)
pnpm dev:api

# Terminal 2: Start Next.js development server (http://localhost:3000)
pnpm dev:web
```

- API Health Check Endpoint: `http://localhost:8000/api/health`
- OpenAPI Schema Specification: `contracts/openapi.yaml` (also available via `/docs` when API is running in debug mode).

---

## 6. Error Taxonomy & Troubleshooting

The Phase 1 backend adheres to a strict, structured error taxonomy. All error responses return a standardized JSON envelope:

```json
{
  "code": "RUN_NOT_RETRYABLE",
  "message": "Run is not retryable in its current state",
  "details": {}
}
```

### HTTP Status & Error Taxonomy Table

| HTTP Status | Category | Common Error Codes | Operator Action / Meaning |
| :---: | :--- | :--- | :--- |
| **422** | Validation Error | `VALIDATION_ERROR`, `INVALID_PAYLOAD` | Request payload failed Pydantic or schema validation. Inspect input fields. |
| **404** | Resource Not Found | `OBJECTIVE_NOT_FOUND`, `RUN_NOT_FOUND`, `AGENT_NOT_FOUND` | Requested entity UUID does not exist within the current company scope. |
| **409** | State / Conflict | `IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_PAYLOAD`, `INVALID_STATE_TRANSITION` | An idempotency key was reused with conflicting parameters, or the objective/run is not in a valid state for the requested operation. |
| **500** | Persistence Error | `CHECKPOINT_PERSISTENCE_ERROR`, `DATABASE_ERROR` | Internal database transaction or checkpointing failed. Check PostgreSQL container health. |
| **502** | Model Provider Error | `PROVIDER_API_ERROR`, `MODEL_GENERATION_FAILED` | Upstream Gemini API call failed or timed out. Inspect provider status or check `GEMINI_API_KEY`. |
| **503** | Runtime Availability | `WORKER_UNAVAILABLE`, `DATABASE_UNREACHABLE` | In-process execution worker is busy or the database connection pool is exhausted. |

### Common Troubleshooting Scenarios

1. **`command not found: pnpm` or `uv`**:
   - Ensure Node.js 22+ is installed and enable corepack (`corepack enable`) or install pnpm globally (`npm install -g pnpm`).
   - Install uv via official installer (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
2. **FastAPI Cannot Connect to PostgreSQL**:
   - Verify Docker container is running: `docker compose -f infra/compose.yaml ps`.
   - Verify port `5432` is not bound by another local PostgreSQL instance.
3. **SSE Stream (`/api/runs/[id]/stream`) Immediately Disconnects**:
   - Ensure the run ID is valid and that you are passing a valid `after_sequence` query parameter (defaulting to `0`).
   - If the backend is offline, `apps/web` will log a warning and fall back to local demo fixtures seamlessly.
