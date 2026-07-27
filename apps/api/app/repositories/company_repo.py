from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.contracts.company import CompanyUpdate
from app.db.models import CompanyModel, utcnow
from app.repositories.exceptions import NotFoundError

DEFAULT_COMPANY_ID = UUID("20000000-0000-4000-8000-000000000001")


def seed_default_company_if_empty(db: Session) -> CompanyModel:
    company = db.scalar(
        select(CompanyModel).where(CompanyModel.id == DEFAULT_COMPANY_ID)
    )
    if company is None:
        company = CompanyModel(
            id=DEFAULT_COMPANY_ID,
            name="Solo Company",
            description="Owner console for a single AI-assisted company.",
            mission="Accelerate autonomous business operations with AI specialists.",
            working_rules=[
                "Specialist work is sequential. Every deliverable must be validated before the next item begins."
            ],
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    return company


def get_company(
    db: Session, company_id: UUID = DEFAULT_COMPANY_ID
) -> CompanyModel:
    company = db.scalar(select(CompanyModel).where(CompanyModel.id == company_id))
    if company is None:
        if company_id == DEFAULT_COMPANY_ID:
            return seed_default_company_if_empty(db)
        raise NotFoundError("Company not found")
    return company


def update_company(
    db: Session, update_data: CompanyUpdate, company_id: UUID = DEFAULT_COMPANY_ID
) -> CompanyModel:
    company = get_company(db, company_id=company_id)
    if update_data.name is not None:
        company.name = update_data.name
    if update_data.description is not None:
        company.description = update_data.description
    if update_data.mission is not None:
        company.mission = update_data.mission
    if update_data.working_rules is not None:
        company.working_rules = update_data.working_rules
    company.updated_at = utcnow()
    db.commit()
    db.refresh(company)
    return company
