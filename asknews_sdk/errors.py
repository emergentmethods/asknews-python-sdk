from collections.abc import Mapping
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

from asknews_sdk.response import APIResponse, AsyncAPIResponse


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


class RequestTimeoutError(APIError):
    code = 408000
    detail = "Request Timeout"


class RateLimitExceededError(APIError):
    code = 429000
    detail = "Rate Limit Exceeded"


class ConcurrencyLimitExceededError(APIError):
    code = 429001
    detail = "Concurrency Limit Exceeded"

class ValidationError(APIError):
    code = 422000
    detail: Dict = {}  # type: ignore[assignment]

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
    408000: RequestTimeoutError,
    422000: ValidationError,
    429000: RateLimitExceededError,
    429001: ConcurrencyLimitExceededError,
    500000: APIError,
    503000: ServiceUnavailableError,
}


def raise_from_response(response: Union[APIResponse, AsyncAPIResponse]) -> None:
    content = response.content
    code = response.status_code * 1000
    detail: Any
    try:
        detail = HTTPStatus(response.status_code).phrase
    except ValueError:
        detail = "HTTP request failed"

    if isinstance(content, Mapping):
        application_code = content.get("code")
        # Application errors use a six-digit HTTP-status prefix + subcode.
        # Do not coerce strings, floats, booleans or container values.
        if type(application_code) is int and 400000 <= application_code < 600000:
            code = application_code

        structured_detail = content.get("detail")
        if isinstance(structured_detail, str) and structured_detail:
            # Keep structured messages useful without allowing unbounded or
            # control-character-filled text into exception messages/logs.
            detail = "".join(
                char if char.isprintable() else " " for char in structured_detail[:1024]
            )
        elif code == 422000 and isinstance(structured_detail, (dict, list)):
            # Preserve the existing machine-readable validation error contract.
            detail = structured_detail

    # Never echo arbitrary proxy bodies (including HTML) into the error detail.
    # The original body, HTTP status and headers remain available on response.

    raise ErrorMap.get(code, APIError)(response, detail, code)
