from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.contracts.work_items import WorkItemStatus
from app.db.models import AgentDefinitionModel, WorkItemModel, utcnow
from app.repositories.company_repo import DEFAULT_COMPANY_ID
from app.repositories.exceptions import ConflictError, NotFoundError
from app.runtime.contracts import PlanDraft

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
    *,
    commit: bool = True,
) -> WorkItemModel:
    work_item = get_work_item(
        db, work_item_id=work_item_id, company_id=company_id
    )
    validate_work_item_transition(work_item.status, new_status)
    work_item.status = new_status
    work_item.updated_at = utcnow()
    if commit:
        db.commit()
        db.refresh(work_item)
    else:
        db.flush()
    return work_item


def replace_proposed_work_items(
    db: Session,
    *,
    objective_id: UUID,
    plan: PlanDraft,
    agents_by_slug: dict[str, AgentDefinitionModel],
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> list[WorkItemModel]:
    existing = list_work_items(
        db, objective_id=objective_id, company_id=company_id
    )
    if any(item.status != "proposed" for item in existing):
        raise ConflictError("Only a proposed plan can be replaced")

    db.execute(
        delete(WorkItemModel).where(
            WorkItemModel.objective_id == objective_id,
            WorkItemModel.company_id == company_id,
            WorkItemModel.status == "proposed",
        )
    )
    now = utcnow()
    work_items = []
    for position, draft in enumerate(plan.work_items, start=1):
        agent = agents_by_slug.get(draft.assigned_agent_slug)
        if agent is None or not agent.enabled:
            raise ConflictError(
                f"Plan assigned unavailable specialist '{draft.assigned_agent_slug}'"
            )
        work_item = WorkItemModel(
            id=uuid4(),
            company_id=company_id,
            objective_id=objective_id,
            parent_id=None,
            assigned_agent_id=agent.id,
            title=draft.title,
            instructions=draft.instructions,
            deliverable_type=draft.deliverable_type,
            status="proposed",
            position=position,
            created_at=now,
            updated_at=now,
        )
        db.add(work_item)
        work_items.append(work_item)
    db.commit()
    for work_item in work_items:
        db.refresh(work_item)
    return work_items


def approve_work_items(
    db: Session,
    *,
    objective_id: UUID,
    company_id: UUID = DEFAULT_COMPANY_ID,
    commit: bool = True,
) -> list[WorkItemModel]:
    work_items = list_work_items(
        db, objective_id=objective_id, company_id=company_id
    )
    if not 2 <= len(work_items) <= 5:
        raise ConflictError("Plan must contain between two and five work items")
    if any(item.status != "proposed" for item in work_items):
        raise ConflictError("Only proposed work items can be approved")
    now = utcnow()
    for work_item in work_items:
        work_item.status = "approved"
        work_item.updated_at = now
    if commit:
        db.commit()
        for work_item in work_items:
            db.refresh(work_item)
    else:
        db.flush()
    return work_items


def get_next_approved_work_item(
    db: Session,
    *,
    objective_id: UUID,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> WorkItemModel | None:
    return db.scalar(
        select(WorkItemModel)
        .where(
            WorkItemModel.objective_id == objective_id,
            WorkItemModel.company_id == company_id,
            WorkItemModel.status == "approved",
        )
        .order_by(WorkItemModel.position.asc())
    )


def get_running_work_item(
    db: Session,
    *,
    objective_id: UUID,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> WorkItemModel | None:
    return db.scalar(
        select(WorkItemModel)
        .where(
            WorkItemModel.objective_id == objective_id,
            WorkItemModel.company_id == company_id,
            WorkItemModel.status == "running",
        )
        .order_by(WorkItemModel.position.asc())
    )


def get_failed_work_item(
    db: Session,
    *,
    objective_id: UUID,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> WorkItemModel | None:
    return db.scalar(
        select(WorkItemModel)
        .where(
            WorkItemModel.objective_id == objective_id,
            WorkItemModel.company_id == company_id,
            WorkItemModel.status == "failed",
        )
        .order_by(WorkItemModel.position.asc())
    )
