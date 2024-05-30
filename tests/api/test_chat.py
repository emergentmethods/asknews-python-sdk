from inspect import isasyncgen, isgenerator

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from respx import MockRouter

from asknews_sdk.api.chat import AsyncChatAPI, ChatAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.chat import (
    CreateChatCompletionResponse,
    CreateChatCompletionResponseStream,
    HeadlineQuestionsResponse,
    ListModelResponse,
)
from asknews_sdk.utils import build_accept_header


class MockCreateChatCompletionResponse(ModelFactory[CreateChatCompletionResponse]):
    ...


class MockCreateChatCompletionResponseStream(ModelFactory[CreateChatCompletionResponseStream]):
    ...


class MockListModelResponse(ModelFactory[ListModelResponse]):
    ...


class MockHeadlineQuestionsResponse(ModelFactory[HeadlineQuestionsResponse]):
    ...


@pytest.fixture
def sync_chat_api(sync_api_client: APIClient):
    return ChatAPI(sync_api_client)


@pytest.fixture
def async_chat_api(async_api_client: AsyncAPIClient):
    return AsyncChatAPI(async_api_client)


def test_sync_chat_api_get_chat_completions(sync_chat_api: ChatAPI, response_mock: MockRouter):
    mock_response = MockCreateChatCompletionResponse.build()

    mocked_route = response_mock.post("/v1/openai/chat/completions").respond(
        content=mock_response.model_dump_json()
    )

    response = sync_chat_api.get_chat_completions(
        messages=[{"role": "user", "content": "Hello"}],
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, CreateChatCompletionResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/openai/chat/completions"
    assert mocked_route.calls.last.request.method == "POST"
    assert mocked_route.calls.last.request.headers["accept"] == build_accept_header(
        [
            (CreateChatCompletionResponse.__content_type__, 1.0),
            (CreateChatCompletionResponseStream.__content_type__, 1.0),
        ]
    )
    assert mocked_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mocked_route.calls.last.response.status_code == 200


def test_sync_chat_api_get_chat_completions_stream(
    sync_chat_api: ChatAPI, response_mock: MockRouter
):
    mock_chunk = MockCreateChatCompletionResponseStream.build()

    def _stream():
        yield ("data: " + mock_chunk.model_dump_json() + "\n").encode()
        yield b"\n"
        yield "data: [DONE]\n".encode()

    mocked_route = response_mock.post("/v1/openai/chat/completions").respond(
        stream=_stream(),
        headers={"content-type": CreateChatCompletionResponseStream.__content_type__}
    )

    response = sync_chat_api.get_chat_completions(
        messages=[{"role": "user", "content": "Hello"}],
        stream=True,
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isgenerator(response)

    for chunk in response:
        assert isinstance(chunk, CreateChatCompletionResponseStream)
        assert chunk.__content_type__ == mock_chunk.__content_type__
        assert chunk.model_dump() == mock_chunk.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/openai/chat/completions"
    assert mocked_route.calls.last.request.method == "POST"
    assert mocked_route.calls.last.request.headers["accept"] == build_accept_header(
        [
            (CreateChatCompletionResponse.__content_type__, 1.0),
            (CreateChatCompletionResponseStream.__content_type__, 1.0),
        ]
    )
    assert mocked_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mocked_route.calls.last.response.status_code == 200


async def test_async_chat_api_get_chat_completions(
    async_chat_api: AsyncChatAPI, response_mock: MockRouter
):
    mock_response = MockCreateChatCompletionResponse.build()

    mocked_route = response_mock.post("/v1/openai/chat/completions").respond(
        content=mock_response.model_dump_json()
    )

    response = await async_chat_api.get_chat_completions(
        messages=[{"role": "user", "content": "Hello"}],
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, CreateChatCompletionResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/openai/chat/completions"
    assert mocked_route.calls.last.request.method == "POST"
    assert mocked_route.calls.last.request.headers["accept"] == build_accept_header(
        [
            (CreateChatCompletionResponse.__content_type__, 1.0),
            (CreateChatCompletionResponseStream.__content_type__, 1.0),
        ]
    )
    assert mocked_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mocked_route.calls.last.response.status_code == 200


async def test_async_chat_api_get_chat_completions_stream(
    async_chat_api: AsyncChatAPI, response_mock: MockRouter
):
    mock_chunk = MockCreateChatCompletionResponseStream.build()

    async def _stream():
        yield ("data: " + mock_chunk.model_dump_json() + "\n").encode()
        yield b"\n"
        yield "data: [DONE]\n".encode()

    mocked_route = response_mock.post("/v1/openai/chat/completions").respond(
        stream=_stream(),
        headers={"content-type": CreateChatCompletionResponseStream.__content_type__}
    )

    response = await async_chat_api.get_chat_completions(
        messages=[{"role": "user", "content": "Hello"}],
        stream=True,
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isasyncgen(response)

    async for chunk in response:
        assert isinstance(chunk, CreateChatCompletionResponseStream)
        assert chunk.__content_type__ == mock_chunk.__content_type__
        assert chunk.model_dump() == mock_chunk.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/openai/chat/completions"
    assert mocked_route.calls.last.request.method == "POST"
    assert mocked_route.calls.last.request.headers["accept"] == build_accept_header(
        [
            (CreateChatCompletionResponse.__content_type__, 1.0),
            (CreateChatCompletionResponseStream.__content_type__, 1.0),
        ]
    )
    assert mocked_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mocked_route.calls.last.response.status_code == 200


def test_sync_chat_api_list_chat_models(sync_chat_api: ChatAPI, response_mock: MockRouter):
    mock_response = MockListModelResponse.build()

    mocked_route = response_mock.get("/v1/openai/models").respond(
        content=mock_response.model_dump_json()
    )

    response = sync_chat_api.list_chat_models(
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, ListModelResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/openai/models"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.request.headers["accept"] == ListModelResponse.__content_type__
    assert mocked_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mocked_route.calls.last.response.status_code == 200


async def test_async_chat_api_list_chat_models(
    async_chat_api: AsyncChatAPI, response_mock: MockRouter
):
    mock_response = MockListModelResponse.build()

    mocked_route = response_mock.get("/v1/openai/models").respond(
        content=mock_response.model_dump_json()
    )

    response = await async_chat_api.list_chat_models(
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, ListModelResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/openai/models"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.request.headers["accept"] == ListModelResponse.__content_type__
    assert mocked_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mocked_route.calls.last.response.status_code == 200


def test_sync_chat_api_get_headline_questions(sync_chat_api: ChatAPI, response_mock: MockRouter):
    mock_response = MockHeadlineQuestionsResponse.build()

    mocked_route = response_mock.get("/v1/chat/questions").respond(
        content=mock_response.model_dump_json()
    )

    response = sync_chat_api.get_headline_questions(
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, HeadlineQuestionsResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/chat/questions"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.request.headers["accept"] == HeadlineQuestionsResponse.__content_type__
    assert mocked_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mocked_route.calls.last.response.status_code == 200


async def test_async_chat_api_get_headline_questions(
    async_chat_api: AsyncChatAPI, response_mock: MockRouter
):
    mock_response = MockHeadlineQuestionsResponse.build()

    mocked_route = response_mock.get("/v1/chat/questions").respond(
        content=mock_response.model_dump_json()
    )

    response = await async_chat_api.get_headline_questions(
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, HeadlineQuestionsResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/chat/questions"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.request.headers["accept"] == HeadlineQuestionsResponse.__content_type__
    assert mocked_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mocked_route.calls.last.response.status_code == 200
