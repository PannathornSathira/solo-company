import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.contracts.common import Error, Health
from app.config import get_settings
from app.db.session import get_session_factory
from app.repositories.agent_repo import seed_default_agents_if_empty
from app.repositories.exceptions import ConflictError, NotFoundError
from app.routers import agents, company, objectives, runs
from app.runtime.factory import create_production_runtime

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    runtime_context = None
    created_runtime = False
    try:
        factory = get_session_factory()
        with factory() as db:
            seed_default_agents_if_empty(db)
        if getattr(app.state, "runtime_service", None) is None:
            runtime_service, runtime_context = create_production_runtime(
                get_settings()
            )
            app.state.runtime_service = runtime_service
            created_runtime = True
    except Exception as exc:
        logger.warning(
            "Could not initialize database-backed runtime "
            "(is PostgreSQL running?): %s",
            exc,
        )
    try:
        yield
    finally:
        if created_runtime:
            del app.state.runtime_service
        if runtime_context is not None:
            runtime_context.__exit__(None, None, None)


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
app.include_router(runs.router)


@app.get(
    "/api/health",
    tags=["system"],
    response_model=Health,
    operation_id="getHealth",
    summary="Check API health",
)
def health() -> Health:
    return Health(status="ok")
