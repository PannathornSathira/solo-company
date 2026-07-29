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
from app.repositories.exceptions import ApplicationError
from app.routers import agents, company, objectives, runs
from app.runtime.coordinator import RuntimeCoordinator
from app.runtime.factory import create_production_runtime

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    runtime_context = None
    created_runtime = False
    runtime_coordinator = None
    created_coordinator = False
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
        if getattr(app.state, "runtime_coordinator", None) is None:
            runtime_coordinator = RuntimeCoordinator(
                app.state.runtime_service
            )
            app.state.runtime_coordinator = runtime_coordinator
            created_coordinator = True
            runtime_coordinator.recover_incomplete_runs()
    except Exception as exc:
        logger.warning(
            "Could not initialize database-backed runtime "
            "(is PostgreSQL running?): %s",
            exc,
        )
    try:
        yield
    finally:
        if created_coordinator and runtime_coordinator is not None:
            runtime_coordinator.shutdown()
            del app.state.runtime_coordinator
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


@app.exception_handler(ApplicationError)
def application_error_handler(
    request: Request, exc: ApplicationError
) -> JSONResponse:
    error_data = Error(code=exc.code, message=exc.message, details={})
    return JSONResponse(
        status_code=exc.status_code,
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


@app.exception_handler(Exception)
def unexpected_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.exception(
        "Unhandled API error method=%s path=%s",
        request.method,
        request.url.path,
    )
    error_data = Error(
        code="INTERNAL_ERROR",
        message="An unexpected internal error occurred",
        details={},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
