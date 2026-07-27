# Phase 4 — Multi-Company Portfolio

## Outcome

The owner can create, switch, clone, archive, and operate multiple isolated companies from one portfolio. Each company has its own agents, knowledge, skills, models, tools, policies, budgets, schedules, runs, and artifacts.

This phase scales the number of companies for one owner. It is not yet a multi-user SaaS marketplace.

## Scope

### Included

- company creation wizard;
- company switcher and portfolio dashboard;
- company templates and cloning;
- hard company scoping across every domain;
- per-company budgets, concurrency, and health;
- archive, export, and restore;
- isolation tests covering database, retrieval, jobs, events, credentials, and caches;
- safe migration of the Phase 1 seeded company.

### Explicitly excluded

- team invitations and collaborative editing;
- customer accounts inside each company;
- public company storefronts;
- subscription billing;
- marketplace sharing of agents, skills, or templates;
- cross-company agents or shared memory;
- horizontal sharding and Kubernetes.

## Company context

Every request and background job resolves a trusted `CompanyContext` containing:

- owner identity;
- company ID;
- membership/ownership proof;
- policy version;
- budget state;
- correlation ID.

The company ID is not trusted simply because it appears in a URL or request body. Repository methods require `CompanyContext` rather than accepting an optional filter.

The model never chooses or changes company context.

## Isolation rules

1. Every business query filters by the trusted company context.
2. Retrieval filters company before ranking, not after results are returned.
3. Cache and checkpoint keys include company ID.
4. jobs, idempotency keys, event streams, and object paths include company ID.
5. model and tool credentials are resolved for the active company only.
6. run snapshots cannot reference capabilities from another company.
7. company exports contain only that company's records and files.
8. archived companies cannot start new runs.
9. no “global search” includes document text or artifacts by default.
10. cross-company aggregation uses precomputed safe metrics, not raw work content.

Add PostgreSQL row-level security when the chosen identity/deployment design supports it. Application scoping tests remain required even with RLS.

## Company templates

A company template may include:

- company profile fields;
- selected agent template versions;
- default model aliases, not credentials;
- selected skill IDs and versions;
- empty knowledge collection definitions;
- tool permission requests, disabled until credentials are provided;
- policy defaults;
- example objectives.

Templates never copy:

- API keys or OAuth tokens;
- private books and documents;
- run history or artifacts;
- approvals or audit actors;
- provider account IDs.

## Screens

| Route | Purpose |
| --- | --- |
| `/portfolio` | all companies, health, active work, pending approvals, spend |
| `/companies/new` | create blank or from template |
| `/companies/[id]/setup` | profile, agents, models, skills, tools, policies |
| `/companies/[id]/settings` | rename, export, archive, retention |
| global company switcher | change active company with clear visual context |
| `/templates/companies` | create, inspect, and version reusable blueprints |

Every company-scoped screen visibly shows the active company. Destructive actions repeat the company name in the confirmation.

## Data additions

| Table | Purpose |
| --- | --- |
| `owners` | local/production subject identity |
| `company_memberships` | owner-to-company access, future-ready for roles |
| `company_templates` | logical blueprint |
| `company_template_versions` | immutable versioned configuration |
| `company_resource_limits` | budgets, concurrency, storage, schedule limits |
| `company_exports` | export job, checksum, status, expiry |
| `company_health_snapshots` | safe portfolio-level status and metrics |

Existing Phase 1-3 tables already carry `company_id`; this phase makes the constraint non-optional and enforced.

## Module order and coding-model ownership

Isolation, migration, resource accounting, and recovery are all complex and remain grouped under GPT. Gemini then owns the bounded portfolio workflows once those contracts are stable.

| Order | Module | Owner | Deliverable | Acceptance |
| --- | --- | --- | --- | --- |
| 1 | P4-M01 Company-context and isolation architecture | GPT | ADR-008, trusted context, repository contract, migration plan | adversarial query fixtures fail closed |
| 2 | P4-M02 Company-scoped backend migration | GPT | non-null constraints, scoped repositories, cache/job/event keys | Phase 1 company migrates with no data loss |
| 3 | P4-M03 Company template and clone engine | GPT | safe blueprint export/import, versioning, secret exclusion | clone copies configuration but no private data or credentials |
| 4 | P4-M04 Resource accounting and portfolio metrics | GPT | company budgets, concurrency, safe aggregated health | one company's limits do not stop unrelated companies |
| 5 | P4-M05 Export, archive, and restore | GPT | complete export manifest, checksum, archive rules, restore test | restored company is isolated and operational |
| 6 | P4-M06 Multi-company integration and leakage testing | GPT | DB/RAG/cache/queue/SSE/credential adversarial suite | zero cross-company content or capability leakage |
| 7 | P4-M07 Portfolio and switcher UI | Gemini | portfolio fixtures, switcher, active-company indicators | switching updates every screen and clears stale client cache |
| 8 | P4-M08 Company creation wizard | Gemini | blank/template setup, validation, progress | owner creates a usable second company |
| 9 | P4-M09 Template and company-management UI | Gemini | template gallery, duplicate, archive, export | destructive actions clearly identify the target company |
| 10 | P4-M10 Portfolio operations UX | Gemini | spend, health, approvals, failed runs, filters | owner can find the company needing attention |
| 11 | P4-M11 Portfolio operator documentation | Gemini | create/clone/archive/restore and troubleshooting guide | owner can add a company without developer help |

## Isolation test matrix

Create company A and company B with deliberately recognizable canary values.

Test that B cannot:

- read A's agent definitions;
- retrieve A's knowledge chunks;
- subscribe to A's SSE run stream;
- fetch A's artifacts by guessed ID;
- use A's model or tool credentials;
- resume A's LangGraph checkpoint;
- approve or cancel A's action;
- consume A's idempotency key;
- see A's raw content in portfolio search;
- restore an export into A without explicit target authorization.

Tests must exercise API, repository, worker, retrieval, and direct object-access paths.

## Migration strategy

1. Verify every existing business row has the seeded Phase 1 company ID.
2. Add non-null and foreign-key constraints.
3. Introduce owner and membership records.
4. Require trusted company context in services.
5. regenerate API client and update routes;
6. clear or version caches;
7. run isolation suite;
8. enable second-company creation.

Do not expose the company switcher before backend scoping is complete.

## Exit criteria

Phase 4 is complete when:

- the owner can create and operate at least three companies;
- each company can have different agents, books, skills, model aliases, tools, schedules, and budgets;
- templates copy configuration without secrets or private content;
- cross-company isolation tests pass for every storage and runtime path;
- archive prevents new work but preserves export and restore;
- portfolio metrics reveal health without exposing raw company content;
- the original Phase 1 company survives migration unchanged.
