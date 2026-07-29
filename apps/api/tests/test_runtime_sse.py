import asyncio
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.contracts.objectives import ObjectiveCreate
from app.contracts.events import RunEvent
from app.db.session import get_session_factory
from app.repositories import event_repo, objective_repo, run_repo
from app.routers import runs as runs_router

from test_runtime_routes import create_objective, wait_for_run


def test_sse_replays_after_greater_cursor_and_closes(
    client: TestClient,
) -> None:
    objective_id = create_objective(client, "SSE replay")
    client.post(f"/api/objectives/{objective_id}/plan")
    approval = client.post(
        f"/api/objectives/{objective_id}/plan/approve",
        headers={"Idempotency-Key": "sse-replay-approval"},
    )
    run_id = approval.json()["id"]
    wait_for_run(client, run_id, "completed")

    response = client.get(
        f"/api/runs/{run_id}/stream?after_sequence=12",
        headers={"Last-Event-ID": "13"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "text/event-stream"
    )
    assert "id: 14\n" in response.text
    assert "id: 13\n" not in response.text
    assert "event: run.completed\n" in response.text


def test_sse_validation_and_not_found_use_json_errors(
    client: TestClient,
) -> None:
    invalid = client.get(
        "/api/runs/00000000-0000-4000-8000-000000000000/stream"
        "?after_sequence=-1"
    )
    assert invalid.status_code == 422
    assert invalid.json()["code"] == "VALIDATION_ERROR"

    missing = client.get(
        "/api/runs/00000000-0000-4000-8000-000000000000/stream"
    )
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"


def test_sse_formatter_uses_persisted_sequence_and_event_name(
    db_session: Session,
) -> None:
    objective = objective_repo.create_objective(
        db_session,
        ObjectiveCreate(title="Format SSE", desired_outcome="Stay stable"),
    )
    run = run_repo.create_run(
        db_session,
        objective_id=objective.id,
        graph_version="p1-v1",
    )
    record = event_repo.append_event(
        db_session,
        run_id=run.id,
        event_type="run.created",
        summary="Created run",
    )
    frame = runs_router.format_sse_event(
        RunEvent.model_validate(record)
    )
    assert frame.startswith("id: 1\nevent: run.created\ndata: ")
    assert frame.endswith("\n\n")


def test_sse_emits_heartbeat_and_stops_on_disconnect(
    db_session: Session,
) -> None:
    objective = objective_repo.create_objective(
        db_session,
        ObjectiveCreate(
            title="Heartbeat SSE",
            desired_outcome="Keep connection observable",
        ),
    )
    run = run_repo.create_run(
        db_session,
        objective_id=objective.id,
        graph_version="p1-v1",
    )
    created = event_repo.append_event(
        db_session,
        run_id=run.id,
        event_type="run.created",
        summary="Created run",
    )

    class RequestStub:
        disconnected = False

        async def is_disconnected(self) -> bool:
            return self.disconnected

    request = RequestStub()
    original_heartbeat = runs_router.SSE_HEARTBEAT_SECONDS
    original_poll = runs_router.SSE_POLL_SECONDS
    runs_router.SSE_HEARTBEAT_SECONDS = 0
    runs_router.SSE_POLL_SECONDS = 0

    async def consume() -> None:
        stream = runs_router.stream_run_events(
            request,
            run_id=UUID(str(run.id)),
            after_sequence=created.sequence,
        )
        assert await anext(stream) == ": keep-alive\n\n"
        request.disconnected = True
        try:
            await anext(stream)
        except StopAsyncIteration:
            pass
        else:
            raise AssertionError("Disconnected SSE stream did not stop")

    try:
        asyncio.run(consume())
    finally:
        runs_router.SSE_HEARTBEAT_SECONDS = original_heartbeat
        runs_router.SSE_POLL_SECONDS = original_poll


def test_sse_delivers_event_persisted_after_subscription(
    db_session: Session,
) -> None:
    objective = objective_repo.create_objective(
        db_session,
        ObjectiveCreate(
            title="Live SSE",
            desired_outcome="Observe newly committed events",
        ),
    )
    run = run_repo.create_run(
        db_session,
        objective_id=objective.id,
        graph_version="p1-v1",
    )
    created = event_repo.append_event(
        db_session,
        run_id=run.id,
        event_type="run.created",
        summary="Created run",
    )

    class RequestStub:
        disconnected = False

        async def is_disconnected(self) -> bool:
            return self.disconnected

    request = RequestStub()
    original_poll = runs_router.SSE_POLL_SECONDS
    runs_router.SSE_POLL_SECONDS = 0.001

    async def consume() -> None:
        stream = runs_router.stream_run_events(
            request,
            run_id=UUID(str(run.id)),
            after_sequence=created.sequence,
        )

        async def append_later() -> None:
            await asyncio.sleep(0.01)
            with get_session_factory()() as db:
                event_repo.append_event(
                    db,
                    run_id=run.id,
                    event_type="plan.proposed",
                    summary="Proposed plan",
                )

        producer = asyncio.create_task(append_later())
        frame = await asyncio.wait_for(anext(stream), timeout=1)
        assert "id: 2\n" in frame
        assert "event: plan.proposed\n" in frame
        request.disconnected = True
        await producer
        await stream.aclose()

    try:
        asyncio.run(consume())
    finally:
        runs_router.SSE_POLL_SECONDS = original_poll
