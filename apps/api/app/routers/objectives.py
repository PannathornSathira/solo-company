from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.contracts.objectives import Objective, ObjectiveCreate
from app.contracts.work_items import WorkItem, WorkItemStatus
from app.db.session import get_db
from app.repositories import objective_repo, work_item_repo

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
