# ADR-003: LangGraph state, execution, and recovery policy

- Status: accepted
- Date: 2026-07-28
- Owner: GPT

## Context

Phase 1 must return an approved run ID before model work completes, stream only
durable events, survive an API restart, and let the owner retry a failed stage
without introducing the separate worker planned for Phase 3.

## Decision

The database run ID is the LangGraph `thread_id`. Approval and retry requests
are committed before execution is submitted to a single-threaded in-process
coordinator. The coordinator deduplicates active run IDs and preserves
sequential Phase 1 execution.

On startup, the coordinator inspects `pending` and `running` runs:

- a missing checkpoint restarts the initial graph input;
- a persisted approval interrupt is resumed after the database approval claim;
- a checkpoint with pending nodes continues with `invoke(None)`;
- a terminal failed checkpoint uses the latest persisted retry request to jump
  to `execute_next_work_item` or `synthesize_executive_brief`.

Retry keeps the same run ID. Completed work items and artifacts are immutable.
Only the failed work item is reset to `approved`, or brief synthesis is
re-entered when specialist work is already complete. Each retry attempt needs
a new idempotency key; reusing an earlier key never schedules another attempt.

Checkpoint state remains JSON-safe and contains only IDs, routing fields,
revision feedback, validated pending output, and error code. Database sessions,
model clients, credentials, prompts, provider responses, and private reasoning
are forbidden.

Runtime persistence is replay-idempotent. A node replay reuses running work and
already persisted plans, artifacts, briefs, and terminal events. Event
sequences are allocated while locking the parent run.

## Consequences

- Approval returns a `running` run immediately and P1-M07 can subscribe to SSE.
- A hard crash is recoverable from PostgreSQL checkpoints and persisted
  approval/retry commands.
- A provider call can repeat if the process dies after the response but before
  the next checkpoint. Persisted events and artifacts must still occur once.
- Phase 1 supports one API process and one runtime thread. Multi-process
  leases, a durable queue, scheduled retries, cancellation, and backoff remain
  Phase 3 work.
