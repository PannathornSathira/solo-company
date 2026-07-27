# Phase 2 — Models, Knowledge, Skills, and Tools

## Outcome

The owner can choose a tested frontier or local model per agent, upload books and company documents, assign portable skills, and enable a curated read-only web-search tool. Agent outputs show which model, sources, skills, and tools were used.

## Scope

### Included

- LiteLLM gateway and provider-neutral model aliases;
- OpenAI/frontier provider connection plus Ollama;
- per-agent model profile selection and connection tests;
- knowledge upload, parsing, chunking, embedding, retrieval, and citations;
- Agent Skills-compatible packages;
- skill versioning and agent assignment;
- MCP client and curated tool registry;
- one read-only Tavily search MCP integration;
- model, retrieval, and tool usage shown in run details;
- token and estimated-cost accounting.

### Explicitly excluded

- arbitrary community tool installation;
- write-capable external tools;
- automatic email, publishing, payments, or CRM changes;
- scheduled work and unattended retry loops;
- execution of untrusted skill scripts;
- a generic vector database abstraction supporting every vendor;
- automatic “best model” selection driven by another LLM.

## Capability model

An agent receives four separately versioned inputs:

```text
Agent definition
  + model profile
  + assigned skill versions
  + assigned knowledge scopes
  + allowed tool IDs
```

This composition is resolved at run start and stored as an immutable run snapshot. Later edits must not change the evidence for an existing run.

## 1. Model gateway

Use provider-neutral aliases:

- `frontier-reasoning`
- `frontier-fast`
- `local-general`
- `local-writing`
- `embedding-default`

An alias points to a LiteLLM model configuration. Agent definitions reference aliases, never provider model IDs.

The first model-selection UI is manual and explicit. The owner sees:

- provider and model display name;
- local or cloud label;
- connection health;
- capability test results;
- context window and structured-output support when known;
- estimated price or “local/no API charge”;
- fallback alias;
- privacy warning for cloud routing.

Do not promise that a local model can perform a role because it loads successfully. Each model profile must pass role-relevant capability fixtures.

Secrets remain in environment variables or a production secret manager. The database stores secret references, never plaintext API keys.

## 2. Knowledge and RAG

Use [Docling](https://github.com/docling-project/docling) for PDF, EPUB, DOCX, Markdown, and other supported document conversion. Use its structure-aware chunking before writing a custom parser.

Store:

- original file metadata and checksum;
- normalized document representation;
- chunk text, page/section metadata, and embedding;
- company scope and optional agent scope;
- parsing and embedding versions;
- provenance, license/ownership note, and ingestion status.

Use PostgreSQL full-text search plus [pgvector](https://github.com/pgvector/pgvector) for hybrid retrieval. One database keeps filters, transactions, backups, and company isolation together.

Every grounded artifact must provide citations that let the owner open the source and relevant page or section. If no supporting source is found, the agent must say so rather than fabricate a citation.

## 3. Skills

Adopt the [Open Agent Skills specification](https://openagentskills.dev/docs/specification):

```text
skill-name/
  SKILL.md
  references/   # optional
  assets/       # optional
  scripts/      # optional but disabled in this phase
```

Phase 2 supports:

- upload of a folder archive;
- `SKILL.md` validation;
- name, description, license, author, and version metadata;
- immutable stored versions;
- assignment to one or more agents;
- progressive loading: descriptions are discoverable, full instructions load only when selected;
- references and assets as contextual data.

Phase 2 does not execute imported scripts. Script contents are stored, clearly marked disabled, and excluded from model tool access. Sandboxed execution is a Phase 3 capability.

## 4. Tools

Use the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) as the client boundary.

The registry stores:

- server ID and transport;
- verified source and version;
- tool schema snapshots;
- read/write/destructive risk classification;
- enabled companies and agents;
- credential reference;
- connection health;
- invocation timeout and result-size limit.

Start with the official [Tavily MCP server](https://github.com/tavily-ai/tavily-mcp) and enable search only. Search results are untrusted external content, not instructions. Log the query, returned source URLs, duration, and errors.

Do not pass provider credentials to the model. The runtime invokes the tool after validating the model's structured request.

## Screens

| Route | Purpose |
| --- | --- |
| `/settings/models` | provider connections, aliases, health, capability tests |
| `/agents/[id]/capabilities` | assign model, skills, knowledge, and tools |
| `/knowledge` | document library, upload, status, scope, source preview |
| `/knowledge/[id]` | metadata, sections/pages, ingestion errors, re-index |
| `/skills` | skill library, version, trust state, assigned agents |
| `/skills/[id]` | rendered instructions, references, disabled scripts |
| `/tools` | curated MCP connections and tool permissions |
| `/runs/[id]` | model route, sources, skill versions, tool calls, tokens, cost |

## Data additions

| Table | Purpose |
| --- | --- |
| `model_providers` | provider type, secret reference, health |
| `model_profiles` | alias, provider model ID, capabilities, fallback, enabled |
| `model_capability_results` | fixture version, result, latency, timestamp |
| `knowledge_documents` | source, scope, checksum, parsing state, metadata |
| `knowledge_chunks` | document, section/page, text, search vector, embedding |
| `skill_packages` | logical skill identity and trust state |
| `skill_versions` | immutable manifest and stored files |
| `agent_skill_assignments` | agent-to-skill-version assignment |
| `agent_knowledge_scopes` | agent-to-document or collection assignment |
| `tool_servers` | MCP connection metadata and credential reference |
| `tool_definitions` | schema snapshot, risk classification, enabled |
| `agent_tool_assignments` | allowed tool IDs per agent |
| `tool_invocations` | proposed input, validated input, result summary, status |
| `model_usage` | run, agent, model profile, tokens, estimated cost |

Every table carrying business data includes `company_id`.

## Module order and coding-model ownership

Complex capability engines are grouped under GPT first. Once their contracts are stable, Gemini owns the bounded management and evidence surfaces. The grouping is intentional and is not an alternation pattern.

| Order | Module | Owner | Deliverable | Acceptance |
| --- | --- | --- | --- | --- |
| 1 | P2-M01 Capability contracts and migrations | GPT | ADR-004/005/006/007, schemas, run snapshot contract | old Phase 1 runs still render; migrations pass |
| 2 | P2-M02 LiteLLM and Ollama gateway | GPT | gateway adapter, health checks, aliases, fallback, usage records | frontier and local fixtures pass; secrets never enter logs |
| 3 | P2-M03 Skill package engine | GPT | validator, immutable versions, progressive loader, assignments | valid skill loads; malformed and script-bearing skills are safely classified |
| 4 | P2-M04 Knowledge ingestion and storage | GPT | upload pipeline, Docling conversion, chunking, embeddings, pgvector | representative PDF and EPUB ingest with stable provenance |
| 5 | P2-M05 Retrieval and citation runtime | GPT | hybrid retrieval, context budget, citation contract, evaluation fixtures | grounded answers cite correct sources; no-source case is explicit |
| 6 | P2-M06 MCP registry and Tavily search | GPT | MCP client, schema validation, timeout/size policy, search integration | allowed search succeeds; undeclared/write tools are blocked |
| 7 | P2-M07 Cross-capability integration and evaluation | GPT | immutable run snapshots, integration suite, cost totals | mixed model/RAG/skill/search run is reproducible |
| 8 | P2-M08 Model settings UI | Gemini | provider, alias, health, and per-agent selection screens | complete responsive/error states with no provider-specific logic |
| 9 | P2-M09 Model capability UX | Gemini | test runner UI, capability badges, routing disclosure in run view | owner can understand why a route passed, failed, or fell back |
| 10 | P2-M10 Skill library UI | Gemini | upload, inspect, version, assign, disabled-script warning | owner can assign a skill without editing files |
| 11 | P2-M11 Knowledge library UI | Gemini | uploads, progress, errors, source preview, agent scope | failed ingestion is understandable and retryable |
| 12 | P2-M12 Citations and evidence UI | Gemini | inline citations, source drawer, retrieval detail in run view | citation opens the relevant stored source location |
| 13 | P2-M13 Tool registry and invocation UI | Gemini | connection health, permissions, run tool-call detail | owner sees proposed inputs, result summary, sources, and failure |
| 14 | P2-M14 Operator docs and sample capability packs | Gemini | sample skills, sample book metadata, setup and troubleshooting | a new owner can configure one local and one cloud route |

## Required tests

### Model routing

- alias resolution does not leak provider IDs into agent definitions;
- unhealthy local model follows configured fallback only;
- local-only policy never sends data to a cloud provider;
- usage records survive provider errors;
- structured-output fixture is tested before assigning a model to the Chief of Staff.

### Knowledge

- duplicate file checksum is handled predictably;
- page/section provenance survives chunking;
- retrieval always filters by company and assigned scope;
- citation IDs refer to retrieved chunks;
- deleted or disabled documents stop appearing in new runs;
- prompt-injection text inside a document cannot directly invoke a tool.

### Skills

- schema and name validation;
- path traversal and oversized archive rejection;
- immutable versions;
- scripts remain unavailable;
- agent sees only assigned skill versions;
- skill text cannot override system permissions.

### Tools

- tool schema validation;
- timeouts and result-size bounds;
- credentials remain outside model-visible payloads;
- only assigned read-only tools execute;
- external content is labeled untrusted;
- every invocation has an auditable record.

## Exit criteria

Phase 2 is complete when:

- the owner can choose a frontier or Ollama model for each agent;
- capability tests prevent an unsuitable model from being silently promoted;
- an uploaded book can support an artifact with verifiable citations;
- an assigned skill changes behavior and its exact version appears in the run;
- Tavily search works as a read-only MCP tool and displays sources;
- all capability choices are captured in the immutable run snapshot;
- no imported script or write-capable external action can execute.
