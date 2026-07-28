# Repository Guidelines

## Project Structure & Module Organization

This repository is a pnpm monorepo containing two applications:

- `apps/web/`: Next.js 16 owner console. App Router pages and layouts live in `apps/web/app/`.
- `apps/api/`: FastAPI service. Application code is under `apps/api/app/`,
  LangGraph orchestration and versioned prompts are under
  `apps/api/app/runtime/`, Alembic revisions are under
  `apps/api/alembic/versions/`, and pytest tests and JSON fixtures are under
  `apps/api/tests/`.
- `contracts/openapi.yaml`: approved Phase 1 API contract shared across modules.
- `docs/architecture/`, `docs/roadmap/`, and `docs/modules/`: ADRs, delivery plans, and module handoffs.
- `infra/compose.yaml`: local PostgreSQL 17 service definition.

Keep application-specific dependencies inside that application's manifest. Treat contracts and accepted ADRs as cross-module interfaces; document intentional changes.

## Build, Test, and Development Commands

Prerequisites are Node.js 22+, pnpm 11+, Python 3.12+, uv, and Docker.

- `pnpm install`: install workspace JavaScript dependencies.
- `uv --directory apps/api sync`: create/sync the API Python environment.
- `pnpm dev:web`: start Next.js at `http://localhost:3000`.
- `pnpm dev:api`: start FastAPI with reload; health is at `/api/health`.
- `pnpm test`: run API pytest tests, then web TypeScript checks.
- `pnpm build`: create the production web build.
- `docker compose -f infra/compose.yaml up -d`: start local PostgreSQL when persistence work requires it.
- `uv --directory apps/api run alembic upgrade head`: apply API database migrations.
- `RUN_POSTGRES_CHECKPOINT_SMOKE=1 uv --directory apps/api run pytest -m postgres`: run the opt-in PostgreSQL checkpoint smoke test.
- `RUN_REAL_MODEL_SMOKE=1 uv --directory apps/api run pytest -m real_model`: run the opt-in Gemini smoke test when `GEMINI_API_KEY` is set.

## Coding Style & Naming Conventions

Use existing formatting: four spaces and type hints in Python; two spaces, double quotes, and semicolons in TypeScript/TSX. TypeScript is strict—do not bypass errors with `any`. Use `snake_case` for Python functions/modules, `PascalCase` for Python models and React components, and descriptive lowercase route paths. Keep Pydantic validation close to contract models. No formatter or linter is configured, so preserve surrounding style and keep imports grouped.

## Testing Guidelines

API tests use pytest and follow `apps/api/tests/test_*.py`; test functions start with `test_`. Store deterministic payload samples in `tests/fixtures/`. Web verification currently uses `tsc --noEmit`; add focused component tests when a test framework is introduced. Every contract change should update and verify both `contracts/openapi.yaml` and matching runtime models. Run `pnpm test` and `pnpm build` before opening a PR.

Default tests must remain deterministic and credential-free: use the fake model
adapter and `InMemorySaver`. Keep real Gemini and PostgreSQL checkpoint checks
opt-in through their existing environment flags.

## Runtime Boundaries

- Treat the database run ID as the LangGraph `thread_id`. Keep checkpoint state
  JSON-safe and limited to IDs, routing fields, revision feedback, and pending
  validated outputs; never checkpoint database sessions, model clients,
  credentials, prompts, raw provider responses, or private reasoning.
- Resolve an agent's exact versioned prompt and fail visibly when it is missing.
  Do not silently fall back to another prompt version.
- Validate event envelopes and the 16-KiB payload limit before persistence.
  Never persist secrets, full prompts, or provider-native responses.
- Preserve approval idempotency: the same key must not repeat model calls,
  events, or artifacts, while a competing key must conflict.
- P1-M05 owns synchronous graph execution and persisted run reads. SSE delivery,
  retry/recovery hardening, and the final error taxonomy belong to P1-M06;
  production UI wiring belongs to P1-M07.

## Commit & Pull Request Guidelines

History currently uses module-scoped subjects such as `Phrase1:P1-M01`; follow the intended pattern with corrected spelling, for example `Phase1:P1-M02 add owner console shell`. Keep commits focused on one module. PRs should state scope, affected contracts or ADRs, verification commands, and known limitations. Link the roadmap/module item and include screenshots for visible UI changes. Call out migrations, configuration changes, or newly required environment variables explicitly; never commit `.env` files or secrets.
