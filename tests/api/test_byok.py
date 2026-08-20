import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from respx import MockRouter

from asknews_sdk.api.byok import AsyncByokAPI, ByokAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.byok import ApiKeyResponse
from asknews_sdk.utils import build_accept_header


class MockApiKeyResponse(ModelFactory[ApiKeyResponse]):
    ...


@pytest.fixture
def sync_byok_api(sync_api_client: APIClient):
    return ByokAPI(sync_api_client)


@pytest.fixture
def async_byok_api(async_api_client: AsyncAPIClient):
    return AsyncByokAPI(async_api_client)


def test_sync_set_byok_key(sync_byok_api: ByokAPI, response_mock: MockRouter):
    provider = "anthropic"
    mock_response = MockApiKeyResponse.build()

    mocked_route = response_mock.put(f"/v1/byok/{provider}").respond(
        content=mock_response.model_dump_json()
    )

    response = sync_byok_api.set_byok_key(provider=provider, api_key="sk-ant-test12345")

    assert isinstance(response, ApiKeyResponse)
    assert response.model_dump() == mock_response.model_dump()
    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == f"/v1/byok/{provider}"
    assert mocked_route.calls.last.request.method == "PUT"
    assert mocked_route.calls.last.request.headers["accept"] == build_accept_header(
        [(ApiKeyResponse.__content_type__, 1.0)]
    )
    assert mocked_route.calls.last.response.status_code == 200


def test_sync_get_byok_key(sync_byok_api: ByokAPI, response_mock: MockRouter):
    provider = "anthropic"
    mock_response = MockApiKeyResponse.build()

    mocked_route = response_mock.get(f"/v1/byok/{provider}").respond(
        content=mock_response.model_dump_json()
    )

    response = sync_byok_api.get_byok_key(provider=provider)

    assert isinstance(response, ApiKeyResponse)
    assert response.model_dump() == mock_response.model_dump()
    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == f"/v1/byok/{provider}"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.response.status_code == 200


def test_sync_delete_byok_key(sync_byok_api: ByokAPI, response_mock: MockRouter):
    provider = "anthropic"

    mocked_route = response_mock.delete(f"/v1/byok/{provider}").respond(status_code=204)

    sync_byok_api.delete_byok_key(provider=provider)

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == f"/v1/byok/{provider}"
    assert mocked_route.calls.last.request.method == "DELETE"
    assert mocked_route.calls.last.response.status_code == 204


@pytest.mark.asyncio
async def test_async_set_byok_key(async_byok_api: AsyncByokAPI, response_mock: MockRouter):
    provider = "google"
    mock_response = MockApiKeyResponse.build()

    mocked_route = response_mock.put(f"/v1/byok/{provider}").respond(
        content=mock_response.model_dump_json()
    )

    response = await async_byok_api.set_byok_key(provider=provider, api_key="AIzaSy-test12345")

    assert isinstance(response, ApiKeyResponse)
    assert response.model_dump() == mock_response.model_dump()
    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == f"/v1/byok/{provider}"
    assert mocked_route.calls.last.request.method == "PUT"
    assert mocked_route.calls.last.response.status_code == 200


@pytest.mark.asyncio
async def test_async_get_byok_key(async_byok_api: AsyncByokAPI, response_mock: MockRouter):
    provider = "google"
    mock_response = MockApiKeyResponse.build()

    mocked_route = response_mock.get(f"/v1/byok/{provider}").respond(
        content=mock_response.model_dump_json()
    )

    response = await async_byok_api.get_byok_key(provider=provider)

    assert isinstance(response, ApiKeyResponse)
    assert response.model_dump() == mock_response.model_dump()
    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == f"/v1/byok/{provider}"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.response.status_code == 200


@pytest.mark.asyncio
async def test_async_delete_byok_key(async_byok_api: AsyncByokAPI, response_mock: MockRouter):
    provider = "google"

    mocked_route = response_mock.delete(f"/v1/byok/{provider}").respond(status_code=204)

    await async_byok_api.delete_byok_key(provider=provider)

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == f"/v1/byok/{provider}"
    assert mocked_route.calls.last.request.method == "DELETE"
    assert mocked_route.calls.last.response.status_code == 204
