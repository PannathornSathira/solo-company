import os
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema

from app.config import get_settings
from app.contracts.objectives import ObjectiveCreate
from app.repositories import (
    artifact_repo,
    event_repo,
    objective_repo,
    work_item_repo,
)
from app.runtime.model_adapters import FakeModelAdapter, GeminiModelAdapter
from app.runtime.service import RuntimeService


@pytest.mark.real_model
@pytest.mark.skipif(
    os.getenv("RUN_REAL_MODEL_SMOKE") != "1",
    reason="Set RUN_REAL_MODEL_SMOKE=1 to call Gemini",
)
def test_gemini_structured_plan_smoke() -> None:
    settings = get_settings()
    adapter = GeminiModelAdapter(
        api_key=settings.gemini_api_key or "",
        model_id=settings.gemini_model_id,
    )
    plan = adapter.propose_plan(
        prompt=(
            "Return a three-item sequential plan for launching a bookkeeping "
            "service. Assign only marketing-specialist or operations-manager."
        ),
        model_alias="gemini-3.1-pro",
        specialist_slugs=[
            "marketing-specialist",
            "operations-manager",
        ],
    )
    assert 2 <= len(plan.work_items) <= 5


class SmokeState(TypedDict, total=False):
    value: str
    decision: str


@pytest.mark.postgres
@pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_CHECKPOINT_SMOKE") != "1",
    reason="Set RUN_POSTGRES_CHECKPOINT_SMOKE=1 to use PostgreSQL",
)
def test_postgres_checkpoint_interrupt_resume_smoke() -> None:
    settings = get_settings()

    def wait_for_owner(state: SmokeState) -> SmokeState:
        decision = interrupt({"value": state["value"]})
        return {"decision": str(decision)}

    builder = StateGraph(SmokeState)
    builder.add_node("wait_for_owner", wait_for_owner)
    builder.add_edge(START, "wait_for_owner")
    builder.add_edge("wait_for_owner", END)

    with PostgresSaver.from_conn_string(
        settings.langgraph_database_url
    ) as checkpointer:
        checkpointer.setup()
        graph = builder.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": f"smoke-{uuid4()}"}}
        paused = graph.invoke({"value": "ready"}, config)
        assert "__interrupt__" in paused
        resumed = graph.invoke(Command(resume="approved"), config)
        assert resumed["decision"] == "approved"


@pytest.mark.postgres
@pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_CHECKPOINT_SMOKE") != "1",
    reason="Set RUN_POSTGRES_CHECKPOINT_SMOKE=1 to use PostgreSQL",
)
def test_clean_postgres_schema_runs_full_recovery_and_retry_flow() -> None:
    settings = get_settings()
    schema = f"p1_m06_{uuid4().hex}"
    admin_engine = create_engine(settings.database_url)
    app_url = make_url(settings.database_url).set(
        query={"options": f"-csearch_path={schema}"}
    )
    checkpoint_base = settings.langgraph_database_url
    checkpoint_url = make_url(checkpoint_base).set(
        query={"options": f"-csearch_path={schema}"}
    )
    scoped_app_url = app_url.render_as_string(hide_password=False)
    scoped_checkpoint_url = checkpoint_url.render_as_string(
        hide_password=False
    )
    original_database_url = os.environ.get("DATABASE_URL")

    with admin_engine.begin() as connection:
        connection.execute(CreateSchema(schema))

    engine = None
    try:
        os.environ["DATABASE_URL"] = scoped_app_url
        get_settings.cache_clear()
        alembic_config = AlembicConfig(
            str(Path(__file__).parents[1] / "alembic.ini")
        )
        command.upgrade(alembic_config, "head")

        engine = create_engine(scoped_app_url)
        factory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
        )
        with PostgresSaver.from_conn_string(
            scoped_checkpoint_url
        ) as checkpointer:
            checkpointer.setup()
            model = FakeModelAdapter()
            runtime = RuntimeService(
                session_factory=factory,
                model_adapter=model,
                checkpointer=checkpointer,
                graph_version="p1-v1",
            )
            with factory() as db:
                objective = objective_repo.create_objective(
                    db,
                    ObjectiveCreate(
                        title="Clean PostgreSQL flow",
                        desired_outcome=(
                            "Complete from migrations through executive brief"
                        ),
                    ),
                )
            runtime.create_plan(objective.id)
            approval = runtime.approve_plan(
                objective.id, "postgres-clean-approval"
            )
            rebuilt = RuntimeService(
                session_factory=factory,
                model_adapter=model,
                checkpointer=checkpointer,
                graph_version="p1-v1",
            )
            rebuilt.resume_run(approval.run.id)
            completed = rebuilt.get_run(approval.run.id)
            assert completed.status == "completed"
            with factory() as db:
                events = event_repo.list_run_events(
                    db, run_id=completed.id
                )
                artifacts = artifact_repo.list_run_artifacts(
                    db, run_id=completed.id
                )
                assert [event.sequence for event in events] == list(
                    range(1, len(events) + 1)
                )
                assert events[-1].event_type == "run.completed"
                assert artifacts[-1].artifact_type == "executive_brief"

            failing_runtime = RuntimeService(
                session_factory=factory,
                model_adapter=FakeModelAdapter(fail_on_position=2),
                checkpointer=checkpointer,
                graph_version="p1-v1",
            )
            with factory() as db:
                retry_objective = objective_repo.create_objective(
                    db,
                    ObjectiveCreate(
                        title="PostgreSQL retry flow",
                        desired_outcome="Resume only the failed stage",
                    ),
                )
            failing_runtime.create_plan(retry_objective.id)
            failed_approval = failing_runtime.approve_plan(
                retry_objective.id, "postgres-retry-approval"
            )
            failing_runtime.resume_run(failed_approval.run.id)
            assert (
                failing_runtime.get_run(failed_approval.run.id).status
                == "failed"
            )
            retry = failing_runtime.retry_run(
                failed_approval.run.id, "postgres-retry-1"
            )
            assert retry.should_schedule is True
            failing_runtime.resume_run(failed_approval.run.id)
            assert (
                failing_runtime.get_run(failed_approval.run.id).status
                == "completed"
            )
            with factory() as db:
                assert [
                    item.status
                    for item in work_item_repo.list_work_items(
                        db, objective_id=retry_objective.id
                    )
                ] == ["done", "done", "done"]
                assert len(
                    artifact_repo.list_run_artifacts(
                        db, run_id=failed_approval.run.id
                    )
                ) == 4

        command.downgrade(alembic_config, "base")
    finally:
        if engine is not None:
            engine.dispose()
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        get_settings.cache_clear()
        with admin_engine.begin() as connection:
            connection.execute(
                DropSchema(schema, cascade=True, if_exists=True)
            )
        admin_engine.dispose()
