from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contracts.company import Company, CompanyUpdate
from app.db.session import get_db
from app.repositories import company_repo

router = APIRouter(tags=["company"])


@router.get(
    "/api/company",
    response_model=Company,
    operation_id="getCompany",
    summary="Get the seeded company",
)
def get_company(db: Session = Depends(get_db)) -> Company:
    company_model = company_repo.get_company(db)
    return Company.model_validate(company_model)


@router.patch(
    "/api/company",
    response_model=Company,
    operation_id="updateCompany",
    summary="Update company details",
)
def update_company(
    update_data: CompanyUpdate, db: Session = Depends(get_db)
) -> Company:
    company_model = company_repo.update_company(db, update_data)
    return Company.model_validate(company_model)
