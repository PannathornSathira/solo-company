from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.contracts.events import EventType, RunEvent
from app.db.models import AgentRunModel, RunEventModel, utcnow
from app.repositories.company_repo import DEFAULT_COMPANY_ID


def append_event(
    db: Session,
    *,
    run_id: UUID,
    event_type: EventType,
    summary: str,
    payload_json: dict[str, Any] | None = None,
    company_id: UUID = DEFAULT_COMPANY_ID,
    commit: bool = True,
) -> RunEventModel:
    bounded_summary = summary.strip()[:240]
    db.scalar(
        select(AgentRunModel.id)
        .where(
            AgentRunModel.id == run_id,
            AgentRunModel.company_id == company_id,
        )
        .with_for_update()
    )
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
    if commit:
        db.commit()
        db.refresh(event)
    else:
        db.flush()
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


def event_exists(
    db: Session,
    *,
    run_id: UUID,
    event_type: EventType,
    company_id: UUID = DEFAULT_COMPANY_ID,
    work_item_id: UUID | None = None,
) -> bool:
    events = list(
        db.scalars(
            select(RunEventModel).where(
                RunEventModel.run_id == run_id,
                RunEventModel.company_id == company_id,
                RunEventModel.event_type == event_type,
            )
        )
    )
    if work_item_id is None:
        return bool(events)
    return any(
        event.payload_json.get("work_item_id") == str(work_item_id)
        for event in events
    )


def latest_event_sequence(
    db: Session,
    *,
    run_id: UUID,
    event_type: EventType,
    company_id: UUID = DEFAULT_COMPANY_ID,
    work_item_id: UUID | None = None,
) -> int:
    events = list(
        db.scalars(
            select(RunEventModel)
            .where(
                RunEventModel.run_id == run_id,
                RunEventModel.company_id == company_id,
                RunEventModel.event_type == event_type,
            )
            .order_by(RunEventModel.sequence.desc())
        )
    )
    if work_item_id is not None:
        events = [
            event
            for event in events
            if event.payload_json.get("work_item_id")
            == str(work_item_id)
        ]
    return events[0].sequence if events else 0
