class NotFoundError(Exception):
    def __init__(self, message: str, code: str = "NOT_FOUND") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class ConflictError(Exception):
    def __init__(self, message: str, code: str = "CONFLICT") -> None:
        super().__init__(message)
        self.message = message
        self.code = code
