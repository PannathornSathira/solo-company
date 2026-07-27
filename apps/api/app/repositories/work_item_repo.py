from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.contracts.work_items import WorkItemStatus
from app.db.models import WorkItemModel, utcnow
from app.repositories.company_repo import DEFAULT_COMPANY_ID
from app.repositories.exceptions import ConflictError, NotFoundError

ALLOWED_WORK_ITEM_TRANSITIONS: dict[str, set[str]] = {
    "proposed": {"approved", "failed"},
    "approved": {"running", "failed", "proposed"},
    "running": {"review", "done", "failed"},
    "review": {"done", "running", "failed"},
    "done": set(),
    "failed": {"proposed", "approved"},
}


def validate_work_item_transition(
    old_status: str, new_status: WorkItemStatus
) -> None:
    if old_status == new_status:
        return
    allowed = ALLOWED_WORK_ITEM_TRANSITIONS.get(old_status, set())
    if new_status not in allowed:
        raise ConflictError(
            f"Cannot transition work item from '{old_status}' to '{new_status}'"
        )


def list_work_items(
    db: Session,
    objective_id: UUID | None = None,
    status: WorkItemStatus | None = None,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> list[WorkItemModel]:
    query = select(WorkItemModel).where(WorkItemModel.company_id == company_id)
    if objective_id is not None:
        query = query.where(WorkItemModel.objective_id == objective_id)
    if status is not None:
        query = query.where(WorkItemModel.status == status)
    query = query.order_by(
        WorkItemModel.objective_id.asc(), WorkItemModel.position.asc()
    )
    return list(db.scalars(query))


def get_work_item(
    db: Session, work_item_id: UUID, company_id: UUID = DEFAULT_COMPANY_ID
) -> WorkItemModel:
    work_item = db.scalar(
        select(WorkItemModel).where(
            WorkItemModel.id == work_item_id,
            WorkItemModel.company_id == company_id,
        )
    )
    if work_item is None:
        raise NotFoundError("Work item not found")
    return work_item


def update_work_item_status(
    db: Session,
    work_item_id: UUID,
    new_status: WorkItemStatus,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> WorkItemModel:
    work_item = get_work_item(
        db, work_item_id=work_item_id, company_id=company_id
    )
    validate_work_item_transition(work_item.status, new_status)
    work_item.status = new_status
    work_item.updated_at = utcnow()
    db.commit()
    db.refresh(work_item)
    return work_item
