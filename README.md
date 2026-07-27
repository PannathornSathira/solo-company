# Solo Company Platform

Phase 1 is a modular monolith with two applications:

- `apps/web`: Next.js owner console
- `apps/api`: FastAPI business API

## Bootstrap

Requires Node.js 22+, pnpm 11+, Python 3.12+, and uv.

```bash
pnpm install
uv --directory apps/api sync
```

## Run

```bash
pnpm dev:web
pnpm dev:api
```

The web app runs at <http://localhost:3000>; API health is at
<http://localhost:8000/api/health>.

## Verify

```bash
pnpm test
pnpm build
```

The Phase 1 API contract is [`contracts/openapi.yaml`](contracts/openapi.yaml).
Architecture decisions and module handoffs live under `docs/`.

