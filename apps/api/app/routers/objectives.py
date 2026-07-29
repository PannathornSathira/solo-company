from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.contracts.objectives import Objective, ObjectiveCreate
from app.contracts.runtime import AgentRun, Plan, PlanRevision
from app.contracts.work_items import WorkItem, WorkItemStatus
from app.db.session import get_db
from app.repositories import objective_repo, work_item_repo
from app.runtime.dependencies import get_runtime_service
from app.runtime.dependencies import get_runtime_coordinator
from app.runtime.coordinator import RuntimeCoordinator
from app.runtime.service import RuntimeService

router = APIRouter(tags=["work"])


@router.get(
    "/api/objectives",
    response_model=list[Objective],
    operation_id="listObjectives",
    summary="List objectives newest first",
)
def list_objectives(db: Session = Depends(get_db)) -> list[Objective]:
    objectives = objective_repo.list_objectives(db)
    return [Objective.model_validate(obj) for obj in objectives]


@router.post(
    "/api/objectives",
    response_model=Objective,
    status_code=status.HTTP_201_CREATED,
    operation_id="createObjective",
    summary="Create a new objective",
)
def create_objective(
    create_data: ObjectiveCreate, db: Session = Depends(get_db)
) -> Objective:
    objective = objective_repo.create_objective(db, create_data=create_data)
    return Objective.model_validate(objective)


@router.get(
    "/api/objectives/{objective_id}",
    response_model=Objective,
    operation_id="getObjective",
    summary="Get objective details",
)
def get_objective(
    objective_id: UUID, db: Session = Depends(get_db)
) -> Objective:
    objective = objective_repo.get_objective(db, objective_id=objective_id)
    return Objective.model_validate(objective)


@router.post(
    "/api/objectives/{objective_id}/plan",
    response_model=Plan,
    status_code=status.HTTP_201_CREATED,
    operation_id="createPlan",
    summary="Create a proposed sequential work plan",
)
def create_plan(
    objective_id: UUID,
    runtime: RuntimeService = Depends(get_runtime_service),
) -> Plan:
    return runtime.create_plan(objective_id)


@router.post(
    "/api/objectives/{objective_id}/plan/revise",
    response_model=Plan,
    operation_id="revisePlan",
    summary="Revise a proposed work plan",
)
def revise_plan(
    objective_id: UUID,
    revision: PlanRevision,
    runtime: RuntimeService = Depends(get_runtime_service),
) -> Plan:
    return runtime.revise_plan(objective_id, revision.feedback)


@router.post(
    "/api/objectives/{objective_id}/plan/approve",
    response_model=AgentRun,
    status_code=status.HTTP_201_CREATED,
    operation_id="approvePlan",
    summary="Approve and execute the proposed plan",
)
def approve_plan(
    objective_id: UUID,
    idempotency_key: str = Header(
        min_length=1,
        max_length=128,
        alias="Idempotency-Key",
    ),
    runtime: RuntimeService = Depends(get_runtime_service),
    coordinator: RuntimeCoordinator = Depends(get_runtime_coordinator),
) -> AgentRun:
    result = runtime.approve_plan(objective_id, idempotency_key)
    if result.should_schedule:
        coordinator.submit(result.run.id)
    return result.run


@router.get(
    "/api/work-items",
    response_model=list[WorkItem],
    operation_id="listWorkItems",
    summary="List work items ordered by objective and position",
)
def list_work_items(
    objective_id: UUID | None = Query(default=None),
    status_filter: WorkItemStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[WorkItem]:
    work_items = work_item_repo.list_work_items(
        db, objective_id=objective_id, status=status_filter
    )
    return [WorkItem.model_validate(item) for item in work_items]
