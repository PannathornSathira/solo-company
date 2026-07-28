from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.contracts.events import RunEvent
from app.contracts.runtime import AgentRun, Artifact
from app.db.session import get_db
from app.repositories import artifact_repo, event_repo, run_repo

router = APIRouter(tags=["runs"])


@router.get(
    "/api/runs/{run_id}",
    response_model=AgentRun,
    operation_id="getRun",
    summary="Get run details",
)
def get_run(run_id: UUID, db: Session = Depends(get_db)) -> AgentRun:
    return AgentRun.model_validate(run_repo.get_run(db, run_id))


@router.get(
    "/api/runs/{run_id}/events",
    response_model=list[RunEvent],
    operation_id="listRunEvents",
    summary="List persisted run events",
)
def list_run_events(
    run_id: UUID,
    after_sequence: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[RunEvent]:
    run = run_repo.get_run(db, run_id)
    events = event_repo.list_run_events(
        db,
        run_id=run.id,
        after_sequence=after_sequence,
        company_id=run.company_id,
    )
    return [RunEvent.model_validate(event) for event in events]


@router.get(
    "/api/runs/{run_id}/artifacts",
    response_model=list[Artifact],
    operation_id="listRunArtifacts",
    summary="List persisted run artifacts",
)
def list_run_artifacts(
    run_id: UUID,
    db: Session = Depends(get_db),
) -> list[Artifact]:
    run = run_repo.get_run(db, run_id)
    artifacts = artifact_repo.list_run_artifacts(
        db, run_id=run.id, company_id=run.company_id
    )
    return [Artifact.model_validate(artifact) for artifact in artifacts]
