from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import AgentRunModel, utcnow
from app.repositories.company_repo import DEFAULT_COMPANY_ID
from app.repositories.exceptions import ConflictError, NotFoundError


def create_run(
    db: Session,
    *,
    objective_id: UUID,
    graph_version: str,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> AgentRunModel:
    existing = db.scalar(
        select(AgentRunModel).where(
            AgentRunModel.company_id == company_id,
            AgentRunModel.objective_id == objective_id,
            AgentRunModel.status.in_(("pending", "awaiting_approval", "running")),
        )
    )
    if existing is not None:
        raise ConflictError("An active run already exists for this objective")

    now = utcnow()
    run = AgentRunModel(
        id=uuid4(),
        company_id=company_id,
        objective_id=objective_id,
        status="pending",
        graph_version=graph_version,
        started_at=None,
        finished_at=None,
        error_code=None,
        approval_idempotency_key=None,
        created_at=now,
        updated_at=now,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_run(
    db: Session,
    run_id: UUID,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> AgentRunModel:
    run = db.scalar(
        select(AgentRunModel).where(
            AgentRunModel.id == run_id,
            AgentRunModel.company_id == company_id,
        )
    )
    if run is None:
        raise NotFoundError("Run not found")
    return run


def get_awaiting_approval_run(
    db: Session,
    objective_id: UUID,
    company_id: UUID = DEFAULT_COMPANY_ID,
    *,
    for_update: bool = False,
) -> AgentRunModel:
    query = (
        select(AgentRunModel)
        .where(
            AgentRunModel.company_id == company_id,
            AgentRunModel.objective_id == objective_id,
            AgentRunModel.status == "awaiting_approval",
        )
        .order_by(AgentRunModel.created_at.desc())
    )
    if for_update:
        query = query.with_for_update()
    run = db.scalar(query)
    if run is None:
        raise ConflictError("Objective has no plan awaiting approval")
    return run


def get_run_by_idempotency_key(
    db: Session,
    *,
    objective_id: UUID,
    idempotency_key: str,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> AgentRunModel | None:
    return db.scalar(
        select(AgentRunModel).where(
            AgentRunModel.company_id == company_id,
            AgentRunModel.objective_id == objective_id,
            AgentRunModel.approval_idempotency_key == idempotency_key,
        )
    )


def claim_approval(
    db: Session,
    *,
    objective_id: UUID,
    idempotency_key: str,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> AgentRunModel:
    existing = get_run_by_idempotency_key(
        db,
        objective_id=objective_id,
        idempotency_key=idempotency_key,
        company_id=company_id,
    )
    if existing is not None:
        return existing

    run = get_awaiting_approval_run(
        db,
        objective_id=objective_id,
        company_id=company_id,
        for_update=True,
    )
    if run.approval_idempotency_key is not None:
        raise ConflictError("Plan approval has already been claimed")

    run.approval_idempotency_key = idempotency_key
    run.updated_at = utcnow()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = get_run_by_idempotency_key(
            db,
            objective_id=objective_id,
            idempotency_key=idempotency_key,
            company_id=company_id,
        )
        if existing is not None:
            return existing
        raise ConflictError("Plan approval has already been claimed") from None
    db.refresh(run)
    return run


def update_run_status(
    db: Session,
    run_id: UUID,
    status: str,
    *,
    error_code: str | None = None,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> AgentRunModel:
    run = get_run(db, run_id=run_id, company_id=company_id)
    now = utcnow()
    run.status = status
    run.error_code = error_code
    if status == "running" and run.started_at is None:
        run.started_at = now
    if status in {"completed", "failed"}:
        run.finished_at = now
    run.updated_at = now
    db.commit()
    db.refresh(run)
    return run
