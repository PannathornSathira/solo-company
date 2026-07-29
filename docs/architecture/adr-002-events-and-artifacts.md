# ADR-002: Event vocabulary and artifact contract

- Status: accepted
- Date: 2026-07-27
- Owner: GPT

## Context

The work board, run inspector, and SSE stream need one durable account of what
happened. Events must be useful to an owner without storing secrets or private
model reasoning.

## Decision

Persist append-only run events with a sequence unique within each run. Phase 1
uses only:

- `run.created`
- `plan.proposed`
- `plan.revision_requested`
- `plan.approved`
- `work.started`
- `work.progress`
- `artifact.created`
- `work.completed`
- `work.failed`
- `brief.created`
- `run.completed`
- `run.failed`

Every event carries `id`, `company_id`, `run_id`, `sequence`, `event_type`,
`summary`, `payload_json`, and `created_at`. Summaries are plain owner-facing
descriptions limited to 240 characters. Payloads are JSON objects limited to
16 KiB after compact UTF-8 encoding.

Artifacts are versioned Markdown records. They carry `id`, `company_id`,
`run_id`, optional `work_item_id`, `artifact_type`, `title`,
`content_markdown`, `version`, `created_at`, and `updated_at`. An
`artifact.created` or `brief.created` event references the artifact by ID; the
event payload does not duplicate artifact content.

Secrets, credentials, raw prompts, private reasoning, and provider-native
response bodies are forbidden in summaries, payloads, and artifact content.
SSE sends the persisted event envelope and uses its sequence as the event ID.
`work.progress` also records an owner-requested retry, including the retry
target and prior error code without duplicating artifact content.

## Consequences

- REST reload and SSE live updates use the same source of truth.
- Reconnect can resume after the last observed sequence.
- Browser clients may supply an initial `after_sequence` cursor; automatic SSE
  reconnects use `Last-Event-ID`, and the server applies the greater value.
- New event types or artifact fields require this ADR and the OpenAPI contract
  to be revised together.
