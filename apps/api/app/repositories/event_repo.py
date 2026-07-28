from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.contracts.events import EventType, RunEvent
from app.db.models import RunEventModel, utcnow
from app.repositories.company_repo import DEFAULT_COMPANY_ID


def append_event(
    db: Session,
    *,
    run_id: UUID,
    event_type: EventType,
    summary: str,
    payload_json: dict[str, Any] | None = None,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> RunEventModel:
    bounded_summary = summary.strip()[:240]
    next_sequence = (
        db.scalar(
            select(func.max(RunEventModel.sequence)).where(
                RunEventModel.run_id == run_id,
                RunEventModel.company_id == company_id,
            )
        )
        or 0
    ) + 1
    contract = RunEvent(
        id=uuid4(),
        company_id=company_id,
        run_id=run_id,
        sequence=next_sequence,
        event_type=event_type,
        summary=bounded_summary,
        payload_json=payload_json or {},
        created_at=utcnow(),
    )
    event = RunEventModel(**contract.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_run_events(
    db: Session,
    *,
    run_id: UUID,
    after_sequence: int = 0,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> list[RunEventModel]:
    return list(
        db.scalars(
            select(RunEventModel)
            .where(
                RunEventModel.run_id == run_id,
                RunEventModel.company_id == company_id,
                RunEventModel.sequence > after_sequence,
            )
            .order_by(RunEventModel.sequence.asc())
        )
    )
