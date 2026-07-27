import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.contracts.common import Error, Health
from app.db.session import get_session_factory
from app.repositories.agent_repo import seed_default_agents_if_empty
from app.repositories.exceptions import ConflictError, NotFoundError
from app.routers import agents, company, objectives

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        factory = get_session_factory()
        with factory() as db:
            seed_default_agents_if_empty(db)
    except Exception as exc:
        logger.warning(
            "Could not connect to database during startup seeding (is PostgreSQL running?): %s",
            exc,
        )
    yield


app = FastAPI(
    title="Solo Company API",
    version="0.1.0",
    description="Phase 1 modular-monolith API.",
    lifespan=lifespan,
)


@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    error_data = Error(code=exc.code, message=exc.message, details={})
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_data.model_dump(mode="json"),
    )


@app.exception_handler(ConflictError)
def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    error_data = Error(code=exc.code, message=exc.message, details={})
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_data.model_dump(mode="json"),
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    error_data = Error(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": jsonable_encoder(exc.errors())},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_data.model_dump(mode="json"),
    )


app.include_router(company.router)
app.include_router(agents.router)
app.include_router(objectives.router)


@app.get(
    "/api/health",
    tags=["system"],
    response_model=Health,
    operation_id="getHealth",
    summary="Check API health",
)
def health() -> Health:
    return Health(status="ok")
