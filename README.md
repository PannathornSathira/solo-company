# Solo Company Platform

Phase 1 is a single-company modular monolith with two applications:

- `apps/web`: Next.js 16 owner console
- `apps/api`: FastAPI business API and checkpointed LangGraph runtime

The runtime turns an objective into an owner-approved plan, executes specialist
work sequentially, persists events and Markdown artifacts, and finishes with an
executive brief. It uses a deterministic fake model by default; Gemini is an
optional runtime adapter.

## Bootstrap

Requires Node.js 22+, pnpm 11+, Python 3.12+, uv, and Docker.

```bash
pnpm install
uv --directory apps/api sync
docker compose -f infra/compose.yaml up -d
uv --directory apps/api run alembic upgrade head
```

The checked-in [`.env.example`](.env.example) documents all runtime settings.
The defaults work with the local PostgreSQL container and use
`RUNTIME_MODEL_BACKEND=fake`, so normal development requires no model API key.

Important runtime settings:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Local PostgreSQL | Application persistence |
| `LANGGRAPH_DATABASE_URL` | Derived from `DATABASE_URL` | LangGraph checkpoints |
| `RUNTIME_MODEL_BACKEND` | `fake` | Select `fake` or `gemini` |
| `GRAPH_VERSION` | `p1-v1` | Persisted runtime graph version |
| `GEMINI_MODEL_ID` | `gemini-3.1-pro-preview` | Provider model for the seeded Gemini alias |
| `GEMINI_API_KEY` | Empty | Required only when using Gemini |

## Run

Start PostgreSQL and apply migrations before starting the API:

```bash
docker compose -f infra/compose.yaml up -d
uv --directory apps/api run alembic upgrade head
pnpm dev:web
pnpm dev:api
```

The web app runs at <http://localhost:3000>; API health is at
<http://localhost:8000/api/health>.

## Runtime API

P1-M05 activates the existing Phase 1 plan and run operations:

- `POST /api/objectives/{objective_id}/plan`
- `POST /api/objectives/{objective_id}/plan/revise`
- `POST /api/objectives/{objective_id}/plan/approve`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/events`
- `GET /api/runs/{run_id}/artifacts`

Plan approval requires an `Idempotency-Key` header. Approval executes
synchronously in P1-M05. SSE delivery, retry/recovery hardening, and the final
error taxonomy remain P1-M06 work; production UI wiring remains P1-M07 work.

## Verify

```bash
pnpm test
pnpm build
```

The default suite uses the fake model and an in-memory LangGraph checkpointer.
Optional integration smoke tests are isolated behind explicit flags:

```bash
RUN_POSTGRES_CHECKPOINT_SMOKE=1 uv --directory apps/api run pytest -m postgres
RUN_REAL_MODEL_SMOKE=1 uv --directory apps/api run pytest -m real_model
```

The PostgreSQL smoke test requires the local database. The real-model smoke test
also requires `GEMINI_API_KEY` in the environment and may incur provider costs.

The Phase 1 API contract is [`contracts/openapi.yaml`](contracts/openapi.yaml).
Architecture decisions and module handoffs live under `docs/`; the runtime
handoff is
[`docs/modules/phase-1/p1-m05.md`](docs/modules/phase-1/p1-m05.md).
