import os
from typing import TypedDict
from uuid import uuid4

import pytest
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.config import get_settings
from app.runtime.model_adapters import GeminiModelAdapter


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
