# Phase 3 — Safe Autonomy and Quality

## Outcome

The company can perform recurring and background work without the browser staying open, while deterministic policy, human approvals, audit history, and evaluations keep the owner in control.

This phase comes before multi-company scale because multiplying unreliable autonomy multiplies risk.

## Scope

### Included

- durable worker and scheduler;
- retries, cancellation, idempotency, and restart recovery;
- deterministic tool policy: allow, require confirmation, or block;
- approval inbox;
- autonomy level per agent and tool;
- prompt, graph, skill, and model snapshot versioning;
- Phoenix/OpenTelemetry traces and evaluation datasets;
- reusable agent templates based on the source document's twelve roles;
- optional, out-of-process n8n webhook adapter;
- tightly sandboxed execution for approved skill scripts.

### Explicitly excluded

- fully autonomous financial, legal, publishing, sales-outreach, or destructive actions;
- arbitrary shell access on the host;
- agent-created permissions;
- agent-created agents without owner review;
- customer-facing workflow builder;
- multi-user approval chains;
- automatic production deployment.

## Autonomy levels

| Level | Meaning |
| --- | --- |
| Manual | owner explicitly starts every run; all effectful tools require approval |
| Supervised | schedules may start runs; configured effects pause for approval |
| Trusted | selected low-risk actions may execute automatically within budgets |

The model does not decide its own level. Policy is stored and evaluated outside prompts.

## Tool policy

Every proposed invocation is evaluated using:

- company and agent;
- tool and operation;
- read/write/destructive classification;
- data sensitivity;
- destination allowlist;
- autonomy level;
- per-run and per-day budget;
- required fields and schema;
- idempotency key.

The result is one of:

- `ALLOW`
- `REQUIRE_CONFIRM`
- `BLOCK`

LangGraph pauses only for `REQUIRE_CONFIRM`. A model cannot rewrite a `BLOCK` decision.

## Durable execution

Move run execution to a worker process. Select the smallest maintained job library that supports:

- durable queue storage;
- delayed and recurring jobs;
- retry policy with backoff;
- cancellation;
- unique/idempotent jobs;
- health and backlog inspection.

Prefer PostgreSQL-backed jobs if operationally sound; otherwise use one Redis-backed worker library. Do not add Kafka, Temporal, or Kubernetes for this scale.

LangGraph checkpoints remain the workflow-state source. The queue says which run needs execution; it does not duplicate graph state.

## Quality system

Use [Phoenix](https://github.com/Arize-ai/phoenix) through OpenTelemetry for:

- LLM, retrieval, and tool traces;
- latency and error analysis;
- versioned evaluation datasets;
- prompt/model comparisons;
- retrieval relevance and citation checks.

The product database remains the official run history. Phoenix is an engineering observability surface, not a business record.

Minimum evaluation suites:

- plan quality and schema adherence;
- correct specialist assignment;
- artifact completeness;
- groundedness and citation correctness;
- prompt-injection resistance;
- tool selection and argument validity;
- local-versus-frontier capability comparison;
- approval-policy correctness.

No prompt, model, skill, graph, or retrieval change ships unless the relevant regression suite passes.

## Agent templates

Convert the source document's roles into versioned templates:

- Chief of Staff / Strategy;
- Operations & Workflow;
- Content & Copywriting;
- Market Research & Intelligence;
- Sales Development;
- Customer Onboarding;
- Technical Lead / Architect;
- Documentation & API;
- Tier 1 Support;
- Tier 2 Support & Escalation;
- Finance & Invoicing;
- Compliance & Risk.

Templates are starting points, not autonomous legal or financial authorities. Creating an agent from a template shows its responsibilities, recommended capabilities, and default permission level for owner approval.

## Sandboxed skill scripts

Only explicitly trusted skill versions may execute scripts.

The sandbox must provide:

- ephemeral filesystem;
- no host filesystem mounts;
- network disabled by default and destination allowlist when enabled;
- CPU, memory, output-size, and wall-time limits;
- non-root execution;
- explicitly mounted input artifacts;
- schema-validated outputs;
- audit event with skill version and content checksum.

Community provenance alone is not trust. The owner must approve the exact version and requested permissions.

## n8n boundary

n8n is optional and out-of-process:

- the platform invokes a versioned webhook contract;
- n8n owns vendor-specific automation;
- the platform stores request/response summaries and correlation IDs;
- n8n is never embedded as the product's workflow builder;
- commercial exposure receives a licensing review.

## Screens

| Route | Purpose |
| --- | --- |
| `/approvals` | pending, approved, rejected, expired actions |
| `/schedules` | recurring objectives, owner, next run, pause/resume |
| `/quality` | release-gate results, evaluation history, regressions |
| `/templates/agents` | twelve source-based role templates |
| `/agents/new` | create from template and review capabilities/permissions |
| `/settings/policies` | autonomy, tool risk, budgets, destination allowlists |
| `/runs/[id]` | retry history, checkpoints, approvals, version snapshot |
| `/audit` | immutable security and operator actions |

## Data additions

| Table | Purpose |
| --- | --- |
| `schedules` | recurrence, objective template, enabled, next run |
| `job_executions` | queue ID, run ID, attempt, lease, status |
| `approval_requests` | proposed action, policy result, expiry, decision |
| `permission_policies` | company/agent/tool rules and autonomy level |
| `audit_events` | append-only operator and security actions |
| `agent_templates` | immutable source-based role template versions |
| `runtime_versions` | graph, prompt, retrieval, and policy versions |
| `evaluation_datasets` | named fixture sets and versions |
| `evaluation_runs` | version snapshot, metrics, pass/fail |
| `skill_script_permissions` | trusted version, requested capabilities, approval |

## Module order and coding-model ownership

The safety-critical runtime modules remain with GPT for several consecutive modules. Gemini begins after those contracts stabilize and owns the bounded operator interfaces and documentation.

| Order | Module | Owner | Deliverable | Acceptance |
| --- | --- | --- | --- | --- |
| 1 | P3-M01 Autonomy and policy contracts | GPT | ADRs, policy schema, audit vocabulary, threat cases | policy fixtures produce deterministic allow/confirm/block |
| 2 | P3-M02 Durable worker and scheduler | GPT | queue, worker, recurrence, recovery, cancellation | scheduled run survives API and worker restart |
| 3 | P3-M03 Policy-gated tool execution | GPT | LangGraph interrupt integration, idempotent action execution | double approval cannot duplicate an effect |
| 4 | P3-M04 Observability and evaluation platform | GPT | OpenTelemetry, Phoenix, datasets, release gates | a known regression fails CI and links to trace evidence |
| 5 | P3-M05 Agent template and version engine | GPT | twelve templates, clone/version rules, capability validation | template creation produces a valid reviewable agent draft |
| 6 | P3-M06 Skill script sandbox and optional n8n adapter | GPT | isolated runner, permission manifest, webhook boundary | denied network/host access tests pass |
| 7 | P3-M07 Adversarial integration and recovery | GPT | restart, duplicate, injection, budget, and permission tests | no test produces unauthorized or duplicate effects |
| 8 | P3-M08 Approval and policy UI | Gemini | approval inbox, policy forms, risk labels | owner can understand and decide a pending action |
| 9 | P3-M09 Schedule and job UX | Gemini | schedule CRUD, history, retry/cancel feedback | owner can pause a schedule and inspect attempts |
| 10 | P3-M10 Run, approval, and audit UX | Gemini | combined timeline and audit filters | every action has a clear proposer, decision, executor, and result |
| 11 | P3-M11 Quality dashboard | Gemini | metric trends, compare versions, failure drill-down | owner can identify which version caused a regression |
| 12 | P3-M12 Agent builder UI | Gemini | template gallery and review/edit flow | owner creates an agent without direct database edits |
| 13 | P3-M13 Sandbox and integration UX | Gemini | trust warnings, permission review, webhook status | risky capability cannot be enabled accidentally |
| 14 | P3-M14 Operator runbooks and templates guide | Gemini | schedule, approval, evaluation, and recovery docs | owner can stop all autonomy using documented controls |

## Required failure tests

- worker dies after a model response but before status update;
- worker dies after proposing a tool call;
- approval is submitted twice;
- approval expires while the worker is offline;
- schedule fires twice due to clock or retry;
- model proposes a different tool than assigned;
- RAG content says to ignore tool policy;
- web content contains prompt injection;
- tool result exceeds size limit;
- local model emits invalid structured output;
- skill script attempts network and host filesystem access;
- daily budget is exhausted during a run.

## Emergency controls

The owner must have:

- global pause for new runs;
- global disable for all write tools;
- per-company and per-agent pause;
- revoke tool credentials;
- cancel queued work;
- terminate a running job;
- view affected runs;
- export the audit trail.

These controls are deterministic API operations, not chat prompts.

## Exit criteria

Phase 3 is complete when:

- scheduled work completes after browser, API, and worker restarts;
- every effectful tool proposal is deterministically allowed, confirmed, or blocked;
- approval decisions are idempotent and auditable;
- the evaluation gate catches a seeded prompt/RAG/tool regression;
- the twelve role templates can create reviewable agents;
- trusted skill scripts run only inside the constrained sandbox;
- the global stop control prevents new autonomous work;
- the owner can explain what ran, under which versions, with which permissions.
