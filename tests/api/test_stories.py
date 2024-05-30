from urllib.parse import parse_qs
from uuid import uuid4

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from respx import MockRouter

from asknews_sdk.api.stories import AsyncStoriesAPI, StoriesAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.stories import StoriesResponse, StoryResponse


class MockStoryResponse(ModelFactory[StoryResponse]):
    ...


class MockStoriesResponse(ModelFactory[StoriesResponse]):
    ...


@pytest.fixture
def sync_stories_api(sync_api_client: APIClient):
    return StoriesAPI(sync_api_client)


@pytest.fixture
def async_stories_api(async_api_client: AsyncAPIClient):
    return AsyncStoriesAPI(async_api_client)


def test_sync_stories_api_get_story(sync_stories_api: StoriesAPI, response_mock: MockRouter):
    story_id = uuid4()
    mock_response = MockStoryResponse.build()

    mocked_route = response_mock.get(f"/v1/stories/{story_id}").respond(
        content=mock_response.model_dump_json()
    )

    response = sync_stories_api.get_story(story_id)

    assert isinstance(response, StoryResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == f"/v1/stories/{story_id}"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.request.headers["accept"] == StoryResponse.__content_type__
    assert parse_qs(mocked_route.calls.last.request.url.query.decode()) == {
        "expand_updates": ["True"],
        "max_updates": ["11"],
        "max_articles": ["5"],
        "reddit": ["0"],
        "citation_method": ["brackets"],
        "condense_auxillary_updates": ["False"],
    }
    assert mocked_route.calls.last.response.status_code == 200


async def test_async_stories_api_get_story(
    async_stories_api: AsyncStoriesAPI, response_mock: MockRouter
):
    story_id = uuid4()
    mock_response = MockStoryResponse.build()

    mocked_route = response_mock.get(f"/v1/stories/{story_id}").respond(
        content=mock_response.model_dump_json()
    )

    response = await async_stories_api.get_story(story_id)

    assert isinstance(response, StoryResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == f"/v1/stories/{story_id}"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.request.headers["accept"] == StoryResponse.__content_type__
    assert parse_qs(mocked_route.calls.last.request.url.query.decode()) == {
        "expand_updates": ["True"],
        "max_updates": ["11"],
        "max_articles": ["5"],
        "reddit": ["0"],
        "citation_method": ["brackets"],
        "condense_auxillary_updates": ["False"],
    }
    assert mocked_route.calls.last.response.status_code == 200


def test_sync_stories_api_search_stories(sync_stories_api: StoriesAPI, response_mock: MockRouter):
    query = "bitcoin"
    mock_response = MockStoriesResponse.build()

    mocked_route = response_mock.get("/v1/stories").respond(content=mock_response.model_dump_json())

    response = sync_stories_api.search_stories(query=query)

    assert isinstance(response, StoriesResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/stories"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.request.headers["accept"] == StoriesResponse.__content_type__
    assert parse_qs(mocked_route.calls.last.request.url.query.decode()) == {
        "query": [query],
        "limit": ["50"],
        "expand_updates": ["False"],
        "max_updates": ["11"],
        "max_articles": ["5"],
        "reddit": ["0"],
        "method": ["kw"],
        "provocative": ["all"],
        "obj_type": ["story"],
        "citation_method": ["brackets"],
    }
    assert mocked_route.calls.last.response.status_code == 200


async def test_async_stories_api_search_stories(
    async_stories_api: AsyncStoriesAPI, response_mock: MockRouter
):
    query = "bitcoin"
    mock_response = MockStoriesResponse.build()

    mocked_route = response_mock.get("/v1/stories").respond(content=mock_response.model_dump_json())

    response = await async_stories_api.search_stories(query=query)

    assert isinstance(response, StoriesResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mocked_route.called
    assert mocked_route.calls.last.request.url.path == "/v1/stories"
    assert mocked_route.calls.last.request.method == "GET"
    assert mocked_route.calls.last.request.headers["accept"] == StoriesResponse.__content_type__
    assert parse_qs(mocked_route.calls.last.request.url.query.decode()) == {
        "query": [query],
        "limit": ["50"],
        "expand_updates": ["False"],
        "max_updates": ["11"],
        "max_articles": ["5"],
        "reddit": ["0"],
        "method": ["kw"],
        "provocative": ["all"],
        "obj_type": ["story"],
        "citation_method": ["brackets"],
    }
    assert mocked_route.calls.last.response.status_code == 200

