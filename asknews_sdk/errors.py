from typing import Dict, Optional

from asknews_sdk.response import APIResponse


class APIError(Exception):
    """
    AskNews API Error
    """
    code: int = 500000
    detail: str = "Internal Server Error"

    def __init__(
        self,
        response: APIResponse,
        detail: Optional[str] = None,
        code: Optional[int] = None
    ) -> None:
        self.response = response
        self.code = code or self.code
        self.detail = detail or self.detail

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.code} - {self.detail}"


class BadRequestError(APIError):
    code = 400000
    detail = "Bad Request"


class ResourceNotFoundError(APIError):
    code = 404000
    detail = "Resource Not Found"


class UnauthorizedError(APIError):
    code = 401000
    detail = "Unauthorized"


class ForbiddenError(APIError):
    code = 403000
    detail = "Forbidden"


class MethodNotAllowed(APIError):
    code = 405000
    detail = "Method Not Allowed"


class ValidationError(APIError):
    code = 422000
    detail: Dict = {}

    def __init__(
        self,
        response: APIResponse,
        detail: Optional[Dict] = None,
        code: Optional[int] = None
    ) -> None:
        self.response = response
        self.code = code or self.code
        self.detail = detail or self.detail

class ServiceUnavailableError(APIError):
    code = 503000
    detail = "Service Unavailable"


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


def raise_from_response(response: APIResponse) -> None:
    json: Dict = response.content
    code = json.get("code", json.get("status_code", 500) * 1000)
    detail = json.get("detail")

    raise ErrorMap.get(code, APIError)(response, detail, code)
