from fastapi import HTTPException, Request, status

from app.runtime.service import RuntimeService


def get_runtime_service(request: Request) -> RuntimeService:
    service = getattr(request.app.state, "runtime_service", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Runtime service is unavailable",
        )
    return service
