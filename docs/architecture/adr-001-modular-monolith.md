# ADR-001: Modular monolith and repository boundaries

- Status: accepted
- Date: 2026-07-27
- Owner: GPT

## Context

Phase 1 must prove one owner-controlled objective-to-artifact loop. Splitting
business capabilities into services would add deployment and consistency work
without proving more of that loop.

## Decision

Use one repository with two Phase 1 deployables:

- `apps/web`: Next.js owner console;
- `apps/api`: FastAPI API and bounded in-process runtime coordinator.

Business boundaries remain modules inside the API: company, agents, work, runs,
and model gateway. They share one PostgreSQL database but may only access data
owned by another boundary through its public Python API.

The committed OpenAPI document is the frontend contract. Frontend request and
response types will be generated from it when API-consuming UI begins.

Use pnpm for JavaScript and uv for Python. Local PostgreSQL runs through Docker
Compose. Phase 1 executes claimed runs on one background thread inside the API
process so approval can return before work completes. A separate durable
worker, shared packages, and deploy orchestration are deferred until a later
phase needs them.

## Consequences

- One process can enforce transactions across Phase 1 boundaries.
- Phase 1 supports one API process; multi-process execution requires the
  durable worker and lease design deferred to Phase 3.
- Deployments remain limited to the web app, API, and PostgreSQL.
- Later modules may add code within these boundaries without changing this ADR.
- A new deployable or cross-boundary contract requires a new ADR.
