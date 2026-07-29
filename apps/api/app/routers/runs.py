import asyncio
from collections.abc import AsyncIterator
from time import monotonic
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.contracts.events import RunEvent
from app.contracts.runtime import AgentRun, Artifact
from app.db.session import get_db, get_session_factory
from app.repositories import artifact_repo, event_repo, run_repo
from app.runtime.coordinator import RuntimeCoordinator
from app.runtime.dependencies import (
    get_runtime_coordinator,
    get_runtime_service,
)
from app.runtime.service import RuntimeService

router = APIRouter(tags=["runs"])
SSE_HEARTBEAT_SECONDS = 15.0
SSE_POLL_SECONDS = 0.25


def format_sse_event(event: RunEvent) -> str:
    return (
        f"id: {event.sequence}\n"
        f"event: {event.event_type}\n"
        f"data: {event.model_dump_json()}\n\n"
    )


async def stream_run_events(
    request: Request,
    *,
    run_id: UUID,
    after_sequence: int,
) -> AsyncIterator[str]:
    cursor = after_sequence
    heartbeat_at = monotonic() + SSE_HEARTBEAT_SECONDS
    session_factory = get_session_factory()

    while True:
        if await request.is_disconnected():
            return

        with session_factory() as db:
            run = run_repo.get_run(db, run_id)
            events = event_repo.list_run_events(
                db,
                run_id=run.id,
                after_sequence=cursor,
                company_id=run.company_id,
            )
            terminal = run.status in {"completed", "failed"}

        for record in events:
            event = RunEvent.model_validate(record)
            cursor = event.sequence
            heartbeat_at = monotonic() + SSE_HEARTBEAT_SECONDS
            yield format_sse_event(event)

        if terminal and not events:
            return

        if monotonic() >= heartbeat_at:
            heartbeat_at = monotonic() + SSE_HEARTBEAT_SECONDS
            yield ": keep-alive\n\n"

        await asyncio.sleep(SSE_POLL_SECONDS)


@router.get(
    "/api/runs/{run_id}",
    response_model=AgentRun,
    operation_id="getRun",
    summary="Get run details",
)
def get_run(run_id: UUID, db: Session = Depends(get_db)) -> AgentRun:
    return AgentRun.from_record(run_repo.get_run(db, run_id))


@router.get(
    "/api/runs/{run_id}/events",
    response_model=list[RunEvent],
    operation_id="listRunEvents",
    summary="List persisted run events",
)
def list_run_events(
    run_id: UUID,
    after_sequence: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[RunEvent]:
    run = run_repo.get_run(db, run_id)
    events = event_repo.list_run_events(
        db,
        run_id=run.id,
        after_sequence=after_sequence,
        company_id=run.company_id,
    )
    return [RunEvent.model_validate(event) for event in events]


@router.get(
    "/api/runs/{run_id}/stream",
    operation_id="streamRunEvents",
    summary="Stream persisted run events",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Persisted run events as Server-Sent Events.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def stream_events(
    request: Request,
    run_id: UUID,
    after_sequence: int = Query(default=0, ge=0),
    last_event_id: int = Header(
        default=0,
        ge=0,
        alias="Last-Event-ID",
    ),
) -> StreamingResponse:
    with get_session_factory()() as db:
        run_repo.get_run(db, run_id)
    cursor = max(after_sequence, last_event_id)
    return StreamingResponse(
        stream_run_events(
            request,
            run_id=run_id,
            after_sequence=cursor,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/api/runs/{run_id}/retry",
    response_model=AgentRun,
    status_code=status.HTTP_202_ACCEPTED,
    operation_id="retryRun",
    summary="Retry the failed stage of a run",
)
def retry_run(
    run_id: UUID,
    idempotency_key: str = Header(
        min_length=1,
        max_length=128,
        alias="Idempotency-Key",
    ),
    runtime: RuntimeService = Depends(get_runtime_service),
    coordinator: RuntimeCoordinator = Depends(get_runtime_coordinator),
) -> AgentRun:
    result = runtime.retry_run(run_id, idempotency_key)
    if result.should_schedule:
        coordinator.submit(result.run.id)
    return result.run


@router.get(
    "/api/runs/{run_id}/artifacts",
    response_model=list[Artifact],
    operation_id="listRunArtifacts",
    summary="List persisted run artifacts",
)
def list_run_artifacts(
    run_id: UUID,
    db: Session = Depends(get_db),
) -> list[Artifact]:
    run = run_repo.get_run(db, run_id)
    artifacts = artifact_repo.list_run_artifacts(
        db, run_id=run.id, company_id=run.company_id
    )
    return [Artifact.model_validate(artifact) for artifact in artifacts]
