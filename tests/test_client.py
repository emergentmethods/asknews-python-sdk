import pytest
from httpx import Request
from respx.router import MockRouter

from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.errors import APIError
from asknews_sdk.response import APIResponse, AsyncAPIResponse
from tests.conftest import BASE_URL


def test_build_api_request(sync_api_client: APIClient):
    request = sync_api_client.build_api_request("GET", "/test")

    assert isinstance(request, Request)
    assert request.method == "GET"
    assert request.url == f"{BASE_URL}/test"
    assert request.headers.get("accept") == "application/json"
    assert request.headers.get("content-type") is None

    request = sync_api_client.build_api_request("POST", "/test", body={"data": "test"})

    assert isinstance(request, Request)
    assert request.method == "POST"
    assert request.url == f"{BASE_URL}/test"
    assert request.headers.get("accept") == "application/json"
    assert request.headers.get("content-type") == "application/json"
    assert request.content == b'{"data":"test"}'

    request = sync_api_client.build_api_request("POST", "/test", body="test")

    assert isinstance(request, Request)
    assert request.method == "POST"
    assert request.url == f"{BASE_URL}/test"
    assert request.headers.get("accept") == "application/json"
    assert request.headers.get("content-type") == "application/json"
    assert request.content == b'"test"'

    request = sync_api_client.build_api_request("POST", "/test", body=b"test")

    assert isinstance(request, Request)
    assert request.method == "POST"
    assert request.url == f"{BASE_URL}/test"
    assert request.headers.get("accept") == "application/json"
    assert request.headers.get("content-type") == "application/octet-stream"
    assert request.content == b"test"

    request = sync_api_client.build_api_request(
        "GET",
        "/test",
        accept=[
            ("application/json", 0.5),
            ("application/xml", 0.3),
        ]
    )

    assert isinstance(request, Request)
    assert request.method == "GET"
    assert request.url == f"{BASE_URL}/test"
    assert request.headers.get("accept") == "application/json; q=0.5, application/xml; q=0.3"
    assert request.headers.get("content-type") is None

    request = sync_api_client.build_api_request(
        "POST",
        "/test",
        body={"data": "test"},
        headers={"content-type": "application/vnd.api.test+json"}
    )

    assert isinstance(request, Request)
    assert request.method == "POST"
    assert request.url == f"{BASE_URL}/test"
    assert request.headers.get("accept") == "application/json"
    assert request.headers.get("content-type") == "application/vnd.api.test+json"
    assert request.content == b'{"data":"test"}'


def test_client_request(sync_api_client: APIClient, response_mock: MockRouter):
    response_mock.get("/test").respond(
        json={"status": "ok"},
        content_type="application/json",
    )

    response = sync_api_client.request("GET", "/test")

    assert isinstance(response, APIResponse)
    assert response.content == {"status": "ok"}
    assert response.status_code == 200
    assert response.content_type == "application/json"

    def streamed_content():
        yield b"Hello, world!"

    response_mock.get("/stream").respond(
        stream=streamed_content(),
        content_type="application/octet-stream",
    )

    response = sync_api_client.request("GET", "/stream", stream=True)

    assert isinstance(response, APIResponse)

    for chunk in response.content:
        assert isinstance(chunk, bytes)
        assert chunk == b"Hello, world!"

    assert response.status_code == 200
    assert response.content_type == "application/octet-stream"


async def test_async_client_request(async_api_client: AsyncAPIClient, response_mock: MockRouter):
    response_mock.get("/test").respond(
        json={"status": "ok"},
    )

    response = await async_api_client.request("GET", "/test")

    assert isinstance(response, AsyncAPIResponse)
    assert response.content == {"status": "ok"}
    assert response.status_code == 200
    assert response.content_type == "application/json"

    async def streamed_content():
        yield b"Hello, world!"

    response_mock.get("/stream").respond(
        stream=streamed_content(),
        content_type="application/octet-stream",
    )

    response = await async_api_client.request("GET", "/stream", stream=True)

    assert isinstance(response, AsyncAPIResponse)

    async for chunk in response.content:
        assert isinstance(chunk, bytes)
        assert chunk == b"Hello, world!"

    assert response.status_code == 200
    assert response.content_type == "application/octet-stream"


def test_client_request_with_auth(
    sync_api_client_with_auth: APIClient,
    response_mock: MockRouter,
):
    response_mock.get("/test").respond(
        json={"status": "ok"},
    )

    response = sync_api_client_with_auth.request("GET", "/test")

    assert isinstance(response, APIResponse)
    assert response.content == {"status": "ok"}
    assert response.status_code == 200
    assert response.content_type == "application/json"

    assert response.request.headers["authorization"] == "Bearer access_token"


async def test_async_client_request_with_auth(
    async_api_client_with_auth: AsyncAPIClient,
    response_mock: MockRouter,
):
    response_mock.get("/test").respond(
        json={"status": "ok"},
    )

    response = await async_api_client_with_auth.request("GET", "/test")

    assert isinstance(response, AsyncAPIResponse)
    assert response.content == {"status": "ok"}
    assert response.status_code == 200
    assert response.content_type == "application/json"

    assert response.request.headers["authorization"] == "Bearer access_token"


def test_sync_client_api_error(
    sync_api_client: APIClient,
    response_mock: MockRouter,
):
    response_mock.get("/test").respond(
        json={"code": 404000, "detail": "Not Found"},
        status_code=404,
    )

    with pytest.raises(APIError) as exc_info:
        sync_api_client.request("GET", "/test")

    assert exc_info.value.code == 404000
    assert exc_info.value.detail == "Not Found"


async def test_async_client_api_error(
    async_api_client: AsyncAPIClient,
    response_mock: MockRouter,
):
    response_mock.get("/test").respond(
        json={"code": 404000, "detail": "Not Found"},
        status_code=404,
    )

    with pytest.raises(APIError) as exc_info:
        await async_api_client.request("GET", "/test")

    assert exc_info.value.code == 404000
    assert exc_info.value.detail == "Not Found"
