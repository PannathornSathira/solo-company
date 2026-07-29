from fastapi import Request

from app.repositories.exceptions import RuntimeUnavailableError
from app.runtime.coordinator import RuntimeCoordinator
from app.runtime.service import RuntimeService


def get_runtime_service(request: Request) -> RuntimeService:
    service = getattr(request.app.state, "runtime_service", None)
    if service is None:
        raise RuntimeUnavailableError()
    return service


def get_runtime_coordinator(request: Request) -> RuntimeCoordinator:
    coordinator = getattr(
        request.app.state, "runtime_coordinator", None
    )
    if coordinator is None:
        raise RuntimeUnavailableError()
    return coordinator
