from uuid import UUID

from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver
from sqlalchemy.orm import Session

from app.db import session as db_session_module
from app.main import app
from app.repositories import artifact_repo, event_repo, work_item_repo
from app.runtime.model_adapters import FakeModelAdapter
from app.runtime.service import RuntimeService


def create_objective(client: TestClient, title: str = "Launch service") -> str:
    response = client.post(
        "/api/objectives",
        json={
            "title": title,
            "desired_outcome": "Launch with a complete owner-reviewed plan",
            "context": "Target small professional services firms",
            "constraints": ["No external tools"],
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def event_types(client: TestClient, run_id: str) -> list[str]:
    response = client.get(f"/api/runs/{run_id}/events")
    assert response.status_code == 200
    return [event["event_type"] for event in response.json()]


def test_create_revise_approve_and_reload_runtime(
    client: TestClient, fake_model: FakeModelAdapter
) -> None:
    objective_id = create_objective(client)

    plan_response = client.post(f"/api/objectives/{objective_id}/plan")
    assert plan_response.status_code == 201
    plan = plan_response.json()
    assert len(plan["work_items"]) == 3
    assert [item["position"] for item in plan["work_items"]] == [1, 2, 3]
    assigned_ids = {item["assigned_agent_id"] for item in plan["work_items"]}
    assert len(assigned_ids) == 2

    objective = client.get(f"/api/objectives/{objective_id}").json()
    assert objective["status"] == "awaiting_approval"

    revise_response = client.post(
        f"/api/objectives/{objective_id}/plan/revise",
        json={"feedback": "Emphasize a lower-risk launch sequence."},
    )
    assert revise_response.status_code == 200
    assert len(revise_response.json()["work_items"]) == 3
    assert fake_model.plan_calls == 2

    approve_response = client.post(
        f"/api/objectives/{objective_id}/plan/approve",
        headers={"Idempotency-Key": "approve-launch-1"},
    )
    assert approve_response.status_code == 201
    run = approve_response.json()
    assert run["status"] == "completed"
    assert run["started_at"] is not None
    assert run["finished_at"] is not None

    expected_events = [
        "run.created",
        "plan.proposed",
        "plan.revision_requested",
        "plan.proposed",
        "plan.approved",
        "work.started",
        "artifact.created",
        "work.completed",
        "work.started",
        "artifact.created",
        "work.completed",
        "work.started",
        "artifact.created",
        "work.completed",
        "brief.created",
        "run.completed",
    ]
    assert event_types(client, run["id"]) == expected_events

    work_items = client.get(
        f"/api/work-items?objective_id={objective_id}"
    ).json()
    assert [item["status"] for item in work_items] == ["done", "done", "done"]

    artifacts_response = client.get(f"/api/runs/{run['id']}/artifacts")
    assert artifacts_response.status_code == 200
    artifacts = artifacts_response.json()
    assert len(artifacts) == 4
    assert artifacts[-1]["artifact_type"] == "executive_brief"
    assert artifacts[-1]["work_item_id"] is None

    paged_events = client.get(
        f"/api/runs/{run['id']}/events?after_sequence=14"
    ).json()
    assert [event["sequence"] for event in paged_events] == [15, 16]


def test_no_revision_event_order_is_deterministic(client: TestClient) -> None:
    objective_id = create_objective(client, "Deterministic run")
    plan_response = client.post(f"/api/objectives/{objective_id}/plan")
    assert plan_response.status_code == 201

    approve_response = client.post(
        f"/api/objectives/{objective_id}/plan/approve",
        headers={"Idempotency-Key": "deterministic-1"},
    )
    run = approve_response.json()
    assert event_types(client, run["id"]) == [
        "run.created",
        "plan.proposed",
        "plan.approved",
        "work.started",
        "artifact.created",
        "work.completed",
        "work.started",
        "artifact.created",
        "work.completed",
        "work.started",
        "artifact.created",
        "work.completed",
        "brief.created",
        "run.completed",
    ]


def test_plan_supports_repeated_revisions(
    client: TestClient, fake_model: FakeModelAdapter
) -> None:
    objective_id = create_objective(client, "Repeated revisions")
    assert client.post(f"/api/objectives/{objective_id}/plan").status_code == 201
    for feedback in (
        "Make the sequence more conservative.",
        "Clarify the completion criteria.",
    ):
        response = client.post(
            f"/api/objectives/{objective_id}/plan/revise",
            json={"feedback": feedback},
        )
        assert response.status_code == 200
        assert len(response.json()["work_items"]) == 3
    assert fake_model.plan_calls == 3


def test_approval_idempotency_does_not_repeat_effects(
    client: TestClient, fake_model: FakeModelAdapter
) -> None:
    objective_id = create_objective(client, "Idempotent run")
    client.post(f"/api/objectives/{objective_id}/plan")
    first = client.post(
        f"/api/objectives/{objective_id}/plan/approve",
        headers={"Idempotency-Key": "same-key"},
    )
    assert first.status_code == 201
    run_id = first.json()["id"]
    first_events = client.get(f"/api/runs/{run_id}/events").json()
    first_artifacts = client.get(f"/api/runs/{run_id}/artifacts").json()
    call_counts = (
        fake_model.plan_calls,
        fake_model.work_calls,
        fake_model.brief_calls,
    )

    repeated = client.post(
        f"/api/objectives/{objective_id}/plan/approve",
        headers={"Idempotency-Key": "same-key"},
    )
    assert repeated.status_code == 201
    assert repeated.json()["id"] == run_id
    assert client.get(f"/api/runs/{run_id}/events").json() == first_events
    assert client.get(f"/api/runs/{run_id}/artifacts").json() == first_artifacts
    assert (
        fake_model.plan_calls,
        fake_model.work_calls,
        fake_model.brief_calls,
    ) == call_counts

    competing = client.post(
        f"/api/objectives/{objective_id}/plan/approve",
        headers={"Idempotency-Key": "different-key"},
    )
    assert competing.status_code == 409


def test_work_failure_stops_later_items(
    client: TestClient, db_session: Session
) -> None:
    failing_model = FakeModelAdapter(fail_on_position=2)
    app.state.runtime_service = RuntimeService(
        session_factory=db_session_module.get_session_factory(),
        model_adapter=failing_model,
        checkpointer=InMemorySaver(),
        graph_version="p1-v1",
    )
    objective_id = create_objective(client, "Failure run")
    client.post(f"/api/objectives/{objective_id}/plan")
    response = client.post(
        f"/api/objectives/{objective_id}/plan/approve",
        headers={"Idempotency-Key": "failure-key"},
    )
    assert response.status_code == 201
    run = response.json()
    assert run["status"] == "failed"
    assert run["error_code"] == "SPECIALIST_EXECUTION_FAILED"
    assert event_types(client, run["id"])[-2:] == ["work.failed", "run.failed"]

    with db_session_module.get_session_factory()() as db:
        work_items = work_item_repo.list_work_items(
            db, objective_id=UUID(objective_id)
        )
        assert [item.status for item in work_items] == [
            "done",
            "failed",
            "approved",
        ]
        artifacts = artifact_repo.list_run_artifacts(
            db, run_id=UUID(run["id"])
        )
        assert len(artifacts) == 1


def test_checkpoint_can_resume_with_rebuilt_runtime(
    db_session: Session,
) -> None:
    checkpointer = InMemorySaver()
    model = FakeModelAdapter()
    first_runtime = RuntimeService(
        session_factory=db_session_module.get_session_factory(),
        model_adapter=model,
        checkpointer=checkpointer,
        graph_version="p1-v1",
    )
    with db_session_module.get_session_factory()() as db:
        from app.contracts.objectives import ObjectiveCreate
        from app.repositories import objective_repo

        objective = objective_repo.create_objective(
            db,
            ObjectiveCreate(
                title="Resume checkpoint",
                desired_outcome="Prove graph reconstruction",
            ),
        )
    plan = first_runtime.create_plan(objective.id)
    assert len(plan.work_items) == 3

    rebuilt_runtime = RuntimeService(
        session_factory=db_session_module.get_session_factory(),
        model_adapter=model,
        checkpointer=checkpointer,
        graph_version="p1-v1",
    )
    run = rebuilt_runtime.approve_plan(objective.id, "resume-key")
    assert run.status == "completed"

    with db_session_module.get_session_factory()() as db:
        events = event_repo.list_run_events(db, run_id=run.id)
        assert events[-1].event_type == "run.completed"


def test_missing_prompt_version_fails_visibly(client: TestClient) -> None:
    agents = client.get("/api/agents").json()
    chief = next(agent for agent in agents if agent["slug"] == "chief-of-staff")
    update = client.patch(
        f"/api/agents/{chief['id']}",
        json={"prompt_version": "v9.9.9"},
    )
    assert update.status_code == 200

    objective_id = create_objective(client, "Missing prompt")
    response = client.post(f"/api/objectives/{objective_id}/plan")
    assert response.status_code == 409
    assert response.json()["code"] == "PROMPT_VERSION_NOT_FOUND"
