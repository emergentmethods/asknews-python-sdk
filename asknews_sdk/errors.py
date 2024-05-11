from typing import Optional


class APIError(Exception):
    code: int = 500000

    def __init__(self, detail: str, code: Optional[int] = None) -> None:
        self.code = code or self.code
        self.detail = detail

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.code} - {self.detail}"


class BadRequestError(APIError):
    code = 400000


class ResourceNotFoundError(APIError):
    code = 404000


class UnauthorizedError(APIError):
    code = 401000


class ForbiddenError(APIError):
    code = 403000


class MethodNotAllowed(APIError):
    code = 405000


class ValidationError(APIError):
    code = 422000
    detail: dict  # type: ignore

    def __init__(self, detail: dict, code: Optional[int] = None) -> None:
        self.code = code or self.code
        self.detail = detail


class ServiceUnavailableError(APIError):
    code = 503000


ErrorMap = {
    400000: BadRequestError,
    401000: UnauthorizedError,
    403000: ForbiddenError,
    403001: ForbiddenError,
    403002: ForbiddenError,
    403012: ForbiddenError,
    403011: ForbiddenError,
    404000: ResourceNotFoundError,
    405000: MethodNotAllowed,
    422000: ValidationError,
    500000: APIError,
    503000: ServiceUnavailableError,
}


def raise_from_json(json: dict) -> None:
    code = json.get("code", json.get("status_code", 500) * 1000)
    detail = json.get("detail")

    raise ErrorMap.get(code, APIError)(detail, code)
