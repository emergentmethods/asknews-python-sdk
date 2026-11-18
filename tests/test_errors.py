from collections import UserDict

import pytest
from httpx import HTTPStatusError, Request
from orjson import JSONDecodeError

from asknews_sdk.errors import (
    APIError,
    ConcurrencyLimitExceededError,
    ForbiddenError,
    RateLimitExceededError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    ValidationError,
    raise_from_response,
)
from asknews_sdk.response import APIResponse


# Exercise real response deserialization and error translation, not just the parser.
ERROR_BODIES = [
    pytest.param(b"Too Many Requests", "text/plain", id="plain-text"),
    pytest.param(b'"Too Many Requests"', "application/json", id="json-string"),
    pytest.param(b"[]", "application/json", id="json-list"),
    pytest.param(b"null", "application/json", id="json-null"),
    pytest.param(b"false", "application/json", id="json-bool"),
    pytest.param(b"429", "application/json", id="json-number"),
    pytest.param(b'{"detail":', "application/json", id="malformed-json"),
    pytest.param(b"Too Many Requests", None, id="missing-content-type"),
    pytest.param(b"", "application/json", id="empty"),
    pytest.param(b"<html>private proxy diagnostics</html>", "text/html", id="html"),
    pytest.param(b"<html>private proxy diagnostics</html>", "application/json", id="html-as-json"),
    pytest.param(b"\xff", "text/plain", id="invalid-utf8-text"),
    pytest.param(b"\xff", "application/json", id="invalid-utf8-json"),
    pytest.param(b"private proxy diagnostics" * 10000, "text/plain", id="large-body"),
]


@pytest.fixture(params=["sync", "async"])
def error_client(request, sync_api_client, async_api_client):
    return sync_api_client if request.param == "sync" else async_api_client


async def request_error(client, stream=False):
    from asknews_sdk.client import AsyncAPIClient

    if isinstance(client, AsyncAPIClient):
        return await client.request("GET", "/test", stream=stream)
    return client.request("GET", "/test", stream=stream)


@pytest.mark.parametrize("body,content_type", ERROR_BODIES)
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize(
    "status,error_type,detail",
    [
        (429, RateLimitExceededError, "Too Many Requests"),
        (503, ServiceUnavailableError, "Service Unavailable"),
        (502, APIError, "Bad Gateway"),
    ],
)
async def test_unstructured_http_errors(
    error_client, response_mock, body, content_type, stream, status, error_type, detail
):
    headers = {"Retry-After": "120"}
    if content_type:
        headers["Content-Type"] = content_type
    response_mock.get("/test").respond(status_code=status, content=body, headers=headers)

    with pytest.raises(error_type) as exc_info:
        await request_error(error_client, stream)

    error = exc_info.value
    assert type(error) is error_type
    assert error.code == status * 1000
    assert error.detail == detail
    assert error.response.status_code == status
    assert error.response.headers["retry-after"] == "120"
    assert error.response.body == body
    assert isinstance(error.__context__, HTTPStatusError)
    assert error.__context__.response.status_code == status
    assert "private proxy diagnostics" not in str(error)


INVALID_CODES = [None, True, False, 429001.0, "429001", "", [], {}, 0, -1, 429, 399999, 600000]


@pytest.mark.parametrize("field", ["code", "status_code"])
@pytest.mark.parametrize("value", INVALID_CODES)
async def test_invalid_codes_fall_back_to_http_status(error_client, response_mock, field, value):
    response_mock.get("/test").respond(status_code=429, json={field: value})
    with pytest.raises(RateLimitExceededError) as exc_info:
        await request_error(error_client)
    assert exc_info.value.code == 429000
    assert exc_info.value.response.status_code == 429


@pytest.mark.parametrize("payload", [{}, {"status_code": 500}, {"status_code": 429}])
async def test_missing_code_uses_real_http_status(error_client, response_mock, payload):
    response_mock.get("/test").respond(status_code=429, json=payload)
    with pytest.raises(RateLimitExceededError) as exc_info:
        await request_error(error_client)
    assert exc_info.value.code == 429000


@pytest.mark.parametrize(
    "status,code,error_type",
    [
        (429, 429000, RateLimitExceededError),
        (429, 429001, ConcurrencyLimitExceededError),
        (403, 403012, ForbiddenError),
        (404, 404000, ResourceNotFoundError),
        (500, 500123, APIError),
        (500, 429001, ConcurrencyLimitExceededError),
    ],
)
@pytest.mark.parametrize("retry_after", ["120", "Wed, 21 Oct 2026 07:28:00 GMT"])
async def test_structured_application_errors(
    error_client, response_mock, status, code, error_type, retry_after
):
    response_mock.get("/test").respond(
        status_code=status,
        # An invalid status_code must not break an otherwise valid application code.
        json={"code": code, "status_code": None, "detail": "Structured error message"},
        headers={"Retry-After": retry_after},
    )
    with pytest.raises(error_type) as exc_info:
        await request_error(error_client)
    error = exc_info.value
    assert type(error) is error_type
    assert error.code == code
    assert error.detail == "Structured error message"
    assert error.response.status_code == status
    assert error.response.headers["retry-after"] == retry_after


@pytest.mark.parametrize("detail", [None, "", True, 42, ["unexpected"], {"unexpected": "value"}])
async def test_invalid_detail_uses_safe_fallback(error_client, response_mock, detail):
    response_mock.get("/test").respond(status_code=429, json={"detail": detail})
    with pytest.raises(RateLimitExceededError) as exc_info:
        await request_error(error_client)
    assert exc_info.value.detail == "Too Many Requests"


async def test_structured_text_is_bounded_and_printable(error_client, response_mock):
    response_mock.get("/test").respond(
        status_code=429, json={"detail": "\n\r\x00\x1b\u202e" + "x" * 10000}
    )
    with pytest.raises(RateLimitExceededError) as exc_info:
        await request_error(error_client)
    assert exc_info.value.detail == " " * 5 + "x" * 1019


@pytest.mark.parametrize(
    "detail",
    [
        {"field": "query", "message": "required"},
        [{"loc": ["query", "n_articles"], "msg": "invalid value", "type": "value_error"}],
    ],
)
async def test_validation_details_remain_machine_readable(error_client, response_mock, detail):
    response_mock.get("/test").respond(status_code=422, json={"detail": detail})
    with pytest.raises(ValidationError) as exc_info:
        await request_error(error_client)
    assert exc_info.value.code == 422000
    assert exc_info.value.detail == detail


@pytest.mark.parametrize(
    "body,content_type,exception",
    [
        (b"{", "application/json", JSONDecodeError),
        (b"\xff", "text/plain", UnicodeDecodeError),
    ],
)
async def test_successful_response_decoding_stays_strict(
    error_client, response_mock, body, content_type, exception
):
    response_mock.get("/test").respond(
        status_code=200, content=body, headers={"Content-Type": content_type}
    )
    with pytest.raises(exception):
        await request_error(error_client)


def test_mapping_content_and_unknown_http_status():
    response = APIResponse(Request("GET", "https://example.com"), 599, {}, b"")
    response.content = UserDict({"code": 500123, "detail": "Mapped error"})
    with pytest.raises(APIError) as exc_info:
        raise_from_response(response)
    assert exc_info.value.code == 500123
    assert exc_info.value.detail == "Mapped error"
    assert exc_info.value.response is response

    response.content = None
    with pytest.raises(APIError) as exc_info:
        raise_from_response(response)
    assert exc_info.value.code == 599000
    assert exc_info.value.detail == "HTTP request failed"
