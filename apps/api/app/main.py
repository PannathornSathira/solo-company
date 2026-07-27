from fastapi import FastAPI

app = FastAPI(
    title="Solo Company API",
    version="0.1.0",
    description="Phase 1 modular-monolith API.",
)


@app.get("/api/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}

