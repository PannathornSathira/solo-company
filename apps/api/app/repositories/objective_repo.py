from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.contracts.objectives import ObjectiveCreate, ObjectiveStatus
from app.db.models import ObjectiveModel, utcnow
from app.repositories.company_repo import DEFAULT_COMPANY_ID, seed_default_company_if_empty
from app.repositories.exceptions import ConflictError, NotFoundError

ALLOWED_OBJECTIVE_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"planning", "awaiting_approval", "failed"},
    "planning": {"awaiting_approval", "draft", "failed"},
    "awaiting_approval": {"approved", "planning", "draft", "failed"},
    "approved": {"running", "failed"},
    "running": {"completed", "failed"},
    "completed": set(),
    "failed": {"draft", "planning"},
}


def validate_objective_transition(
    old_status: str, new_status: ObjectiveStatus
) -> None:
    if old_status == new_status:
        return
    allowed = ALLOWED_OBJECTIVE_TRANSITIONS.get(old_status, set())
    if new_status not in allowed:
        raise ConflictError(
            f"Cannot transition objective from '{old_status}' to '{new_status}'"
        )


def list_objectives(
    db: Session, company_id: UUID = DEFAULT_COMPANY_ID
) -> list[ObjectiveModel]:
    return list(
        db.scalars(
            select(ObjectiveModel)
            .where(ObjectiveModel.company_id == company_id)
            .order_by(ObjectiveModel.created_at.desc())
        )
    )


def get_objective(
    db: Session, objective_id: UUID, company_id: UUID = DEFAULT_COMPANY_ID
) -> ObjectiveModel:
    objective = db.scalar(
        select(ObjectiveModel).where(
            ObjectiveModel.id == objective_id,
            ObjectiveModel.company_id == company_id,
        )
    )
    if objective is None:
        raise NotFoundError("Objective not found")
    return objective


def create_objective(
    db: Session,
    create_data: ObjectiveCreate,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> ObjectiveModel:
    seed_default_company_if_empty(db)
    objective = ObjectiveModel(
        id=uuid4(),
        company_id=company_id,
        title=create_data.title,
        desired_outcome=create_data.desired_outcome,
        context=create_data.context,
        constraints=create_data.constraints,
        status="draft",
        created_at=utcnow(),
        updated_at=utcnow(),
    )
    db.add(objective)
    db.commit()
    db.refresh(objective)
    return objective


def update_objective_status(
    db: Session,
    objective_id: UUID,
    new_status: ObjectiveStatus,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> ObjectiveModel:
    objective = get_objective(
        db, objective_id=objective_id, company_id=company_id
    )
    validate_objective_transition(objective.status, new_status)
    objective.status = new_status
    objective.updated_at = utcnow()
    db.commit()
    db.refresh(objective)
    return objective
