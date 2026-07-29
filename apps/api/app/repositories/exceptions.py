from app.contracts.common import ErrorCode


class ApplicationError(Exception):
    status_code = 500

    def __init__(self, message: str, code: ErrorCode) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class NotFoundError(ApplicationError):
    status_code = 404

    def __init__(
        self, message: str, code: ErrorCode = "NOT_FOUND"
    ) -> None:
        super().__init__(message, code=code)


class ConflictError(ApplicationError):
    status_code = 409

    def __init__(
        self, message: str, code: ErrorCode = "STATE_CONFLICT"
    ) -> None:
        super().__init__(message, code=code)


class InternalError(ApplicationError):
    status_code = 500

    def __init__(
        self, message: str, code: ErrorCode = "INTERNAL_ERROR"
    ) -> None:
        super().__init__(message, code=code)


class UpstreamError(ApplicationError):
    status_code = 502


class RuntimeUnavailableError(ApplicationError):
    status_code = 503

    def __init__(
        self,
        message: str = "Runtime service is unavailable",
        code: ErrorCode = "RUNTIME_UNAVAILABLE",
    ) -> None:
        super().__init__(message, code=code)
