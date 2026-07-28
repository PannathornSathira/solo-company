from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ArtifactModel, utcnow
from app.repositories.company_repo import DEFAULT_COMPANY_ID
from app.runtime.contracts import ArtifactDraft


def create_artifact(
    db: Session,
    *,
    run_id: UUID,
    work_item_id: UUID | None,
    draft: ArtifactDraft,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> ArtifactModel:
    latest_version = (
        db.scalar(
            select(func.max(ArtifactModel.version)).where(
                ArtifactModel.company_id == company_id,
                ArtifactModel.run_id == run_id,
                ArtifactModel.work_item_id == work_item_id,
                ArtifactModel.artifact_type == draft.artifact_type,
            )
        )
        or 0
    )
    now = utcnow()
    artifact = ArtifactModel(
        id=uuid4(),
        company_id=company_id,
        run_id=run_id,
        work_item_id=work_item_id,
        artifact_type=draft.artifact_type,
        title=draft.title,
        content_markdown=draft.content_markdown,
        version=latest_version + 1,
        created_at=now,
        updated_at=now,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def list_run_artifacts(
    db: Session,
    *,
    run_id: UUID,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> list[ArtifactModel]:
    return list(
        db.scalars(
            select(ArtifactModel)
            .where(
                ArtifactModel.run_id == run_id,
                ArtifactModel.company_id == company_id,
            )
            .order_by(ArtifactModel.created_at.asc(), ArtifactModel.version.asc())
        )
    )
