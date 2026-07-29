from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import RunRetryRequestModel, utcnow
from app.repositories.company_repo import DEFAULT_COMPANY_ID


def get_retry_request_by_key(
    db: Session,
    *,
    run_id: UUID,
    idempotency_key: str,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> RunRetryRequestModel | None:
    return db.scalar(
        select(RunRetryRequestModel).where(
            RunRetryRequestModel.run_id == run_id,
            RunRetryRequestModel.company_id == company_id,
            RunRetryRequestModel.idempotency_key == idempotency_key,
        )
    )


def get_latest_retry_request(
    db: Session,
    *,
    run_id: UUID,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> RunRetryRequestModel | None:
    return db.scalar(
        select(RunRetryRequestModel)
        .where(
            RunRetryRequestModel.run_id == run_id,
            RunRetryRequestModel.company_id == company_id,
        )
        .order_by(RunRetryRequestModel.created_at.desc())
    )


def create_retry_request(
    db: Session,
    *,
    run_id: UUID,
    idempotency_key: str,
    retry_target: str,
    work_item_id: UUID | None,
    company_id: UUID = DEFAULT_COMPANY_ID,
) -> RunRetryRequestModel:
    now = utcnow()
    request = RunRetryRequestModel(
        id=uuid4(),
        company_id=company_id,
        run_id=run_id,
        idempotency_key=idempotency_key,
        retry_target=retry_target,
        work_item_id=work_item_id,
        created_at=now,
        updated_at=now,
    )
    db.add(request)
    db.flush()
    return request
