from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.runtime.contracts import PlanDraft, PlanItemDraft
from app.runtime.model_adapters import ModelAdapterError
from app.runtime.prompts import PromptLoader, PromptNotFoundError
from app.runtime.service import RuntimeService
from app.contracts.objectives import ObjectiveCreate
from app.repositories import event_repo, objective_repo, run_repo


def test_plan_draft_requires_two_to_five_items() -> None:
    item = PlanItemDraft(
        assigned_agent_slug="marketing-specialist",
        title="Draft a brief",
        instructions="Create a complete owner-readable brief.",
        deliverable_type="brief",
    )
    with pytest.raises(ValidationError):
        PlanDraft(work_items=[item])
    with pytest.raises(ValidationError):
        PlanDraft(work_items=[item] * 6)


def test_prompt_loader_renders_required_variables() -> None:
    loader = PromptLoader()
    rendered = loader.render(
        "v1.0.0",
        "specialist_work",
        agent_name="Marketing Specialist",
        agent_role="Marketing Specialist",
        company_name="Solo Company",
        company_mission="Launch carefully",
        working_rules=["Work sequentially"],
        agent_objective="Create launch assets",
        agent_responsibilities=["Messaging"],
        work_item_title="Draft launch brief",
        work_item_instructions="Prepare the brief",
        deliverable_type="marketing_brief",
        objective_context={"title": "Launch"},
        prior_artifacts=[],
    )
    assert "Marketing Specialist" in rendered
    assert "Draft launch brief" in rendered
    assert "$agent_name" not in rendered


def test_prompt_loader_rejects_missing_version(tmp_path: Path) -> None:
    loader = PromptLoader(root=tmp_path)
    with pytest.raises(PromptNotFoundError):
        loader.render("v9.9.9", "specialist_work")


def test_plan_assignment_rejects_unavailable_agent() -> None:
    plan = PlanDraft(
        work_items=[
            PlanItemDraft(
                assigned_agent_slug="chief-of-staff",
                title=f"Invalid assignment {index}",
                instructions="This assignment must be rejected.",
                deliverable_type="brief",
            )
            for index in range(2)
        ]
    )
    with pytest.raises(ModelAdapterError):
        RuntimeService._validate_plan_assignments(
            plan,
            {"marketing-specialist", "operations-manager"},
        )


def test_event_repository_bounds_owner_summary(db_session: Session) -> None:
    objective = objective_repo.create_objective(
        db_session,
        ObjectiveCreate(title="Bound summary", desired_outcome="Stay valid"),
    )
    run = run_repo.create_run(
        db_session,
        objective_id=objective.id,
        graph_version="p1-v1",
    )
    event = event_repo.append_event(
        db_session,
        run_id=run.id,
        event_type="run.created",
        summary="x" * 300,
    )
    assert len(event.summary) == 240
