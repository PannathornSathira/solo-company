# Solo Company Platform

Phase 1 is a single-company modular monolith with two applications:

- `apps/web`: Next.js 16 owner console
- `apps/api`: FastAPI business API and checkpointed LangGraph runtime

The runtime turns an objective into an owner-approved plan, returns the claimed
run immediately, executes specialist work sequentially on one in-process
worker, persists events and Markdown artifacts, and finishes with an executive
brief. It uses a deterministic fake model by default; Gemini is an optional
runtime adapter.

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

P1-M06 exposes the complete backend handoff for the Phase 1 owner workflow:

- `POST /api/objectives/{objective_id}/plan`
- `POST /api/objectives/{objective_id}/plan/revise`
- `POST /api/objectives/{objective_id}/plan/approve`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/events`
- `GET /api/runs/{run_id}/stream`
- `POST /api/runs/{run_id}/retry`
- `GET /api/runs/{run_id}/artifacts`

Plan approval requires an `Idempotency-Key` header. Approval executes
asynchronously: the response contains the claimed `running` run, and the
single Phase 1 worker resumes its persisted LangGraph checkpoint. Reusing the
same key returns the same run and never schedules duplicate work.

SSE streams only persisted `RunEvent` records:

```bash
curl -N \
  -H 'Last-Event-ID: 0' \
  'http://localhost:8000/api/runs/<run-id>/stream?after_sequence=0'
```

The stream uses each event sequence as its SSE ID, emits a keep-alive comment
every 15 seconds, and closes after a completed or failed run is fully drained.
For an initial browser subscription, use `after_sequence`; automatic reconnect
uses `Last-Event-ID`, and the server applies the greater cursor.

A retry keeps the same run and requires a new key for each attempt:

```bash
curl -X POST \
  -H 'Idempotency-Key: retry-<unique-value>' \
  'http://localhost:8000/api/runs/<run-id>/retry'
```

Only a failed work item or executive brief is retried. Completed artifacts are
preserved. Reusing an earlier retry key returns the current representation of
the same run without launching another attempt.

JSON failures use one envelope:

```json
{
  "code": "RUN_NOT_RETRYABLE",
  "message": "Run is not retryable in its current state",
  "details": {}
}
```

The stable taxonomy covers validation (`422`), resource (`404`), state conflict
(`409`), internal persistence (`500`), model provider (`502`), and runtime
availability (`503`) failures. Failed run records also expose `error_code` and
the computed `retryable` flag.

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

The PostgreSQL suite creates an isolated temporary schema, migrates it from
empty to `head`, verifies checkpoint recovery and same-run retry, downgrades the
application tables, and drops the schema. It requires the local database but
does not alter normal application tables. The real-model smoke test also
requires `GEMINI_API_KEY` and may incur provider costs.

The Phase 1 API contract is [`contracts/openapi.yaml`](contracts/openapi.yaml).
Architecture decisions and module handoffs live under `docs/`; the reliability
handoff is
[`docs/modules/phase-1/p1-m06.md`](docs/modules/phase-1/p1-m06.md), the UI
integration handoff is
[`docs/modules/phase-1/p1-m07.md`](docs/modules/phase-1/p1-m07.md), and its
checkpoint policy is
[`docs/architecture/adr-003-langgraph-state-and-recovery.md`](docs/architecture/adr-003-langgraph-state-and-recovery.md).
