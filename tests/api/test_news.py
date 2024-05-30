from uuid import uuid4

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from respx import MockRouter

from asknews_sdk.api.news import AsyncNewsAPI, NewsAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.news import ArticleResponse, SearchResponse, SourceReportResponse
from asknews_sdk.errors import ResourceNotFoundError
from asknews_sdk.response import APIResponse


class MockArticleResponse(ModelFactory[ArticleResponse]):
    ...

class MockSearchResponse(ModelFactory[SearchResponse]):
    ...

class MockSourceReportResponse(ModelFactory[SourceReportResponse]):
    ...


@pytest.fixture
def sync_news_api(sync_api_client: APIClient):
    return NewsAPI(sync_api_client)


@pytest.fixture
def async_news_api(async_api_client: AsyncAPIClient):
    return AsyncNewsAPI(async_api_client)


def test_sync_news_api_get_article(sync_news_api: NewsAPI, response_mock: MockRouter):
    article_id = uuid4()
    mock_article = MockArticleResponse.build(article_id=article_id)

    mock_route = response_mock.get(f"/v1/news/{article_id}").respond(
        content=mock_article.model_dump_json()
    )

    response = sync_news_api.get_article(article_id)

    assert isinstance(response, ArticleResponse)
    assert response.__content_type__ == mock_article.__content_type__
    assert response.model_dump() == mock_article.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == f"/v1/news/{article_id}"
    assert mock_route.calls.last.request.headers["accept"] == ArticleResponse.__content_type__
    assert mock_route.calls.last.response.status_code == 200

    mock_route = response_mock.get(f"/v1/news/{article_id}").respond(
        json={"code": ResourceNotFoundError.code, "detail": ResourceNotFoundError.detail},
        status_code=404
    )

    with pytest.raises(ResourceNotFoundError) as exc_info:
        sync_news_api.get_article(article_id)

    assert isinstance(exc_info.value.response, APIResponse)
    assert exc_info.value.code == ResourceNotFoundError.code
    assert exc_info.value.detail == ResourceNotFoundError.detail

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == f"/v1/news/{article_id}"
    assert mock_route.calls.last.request.headers["accept"] == ArticleResponse.__content_type__
    assert mock_route.calls.last.response.status_code == 404


async def test_async_news_api_get_article(async_news_api: AsyncNewsAPI, response_mock: MockRouter):
    article_id = uuid4()
    mock_article = MockArticleResponse.build(article_id=article_id)

    mock_route = response_mock.get(f"/v1/news/{article_id}").respond(
        content=mock_article.model_dump_json()
    )

    response = await async_news_api.get_article(article_id)

    assert isinstance(response, ArticleResponse)
    assert response.__content_type__ == mock_article.__content_type__
    assert response.model_dump() == mock_article.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == f"/v1/news/{article_id}"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == ArticleResponse.__content_type__
    assert mock_route.calls.last.response.status_code == 200

    mock_route = response_mock.get(f"/v1/news/{article_id}").respond(
        json={"code": ResourceNotFoundError.code, "detail": ResourceNotFoundError.detail},
        status_code=404
    )

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await async_news_api.get_article(article_id)

    assert isinstance(exc_info.value.response, APIResponse)
    assert exc_info.value.code == ResourceNotFoundError.code
    assert exc_info.value.detail == ResourceNotFoundError.detail

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == f"/v1/news/{article_id}"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == ArticleResponse.__content_type__
    assert mock_route.calls.last.response.status_code == 404


def test_sync_news_api_search_news(sync_news_api: NewsAPI, response_mock: MockRouter):
    mock_search_response = MockSearchResponse.build()

    mock_route = response_mock.get("/v1/news/search").respond(
        content=mock_search_response.model_dump_json()
    )

    response = sync_news_api.search_news(query="query")

    assert isinstance(response, SearchResponse)
    assert response.__content_type__ == mock_search_response.__content_type__
    assert response.model_dump() == mock_search_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/news/search"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == SearchResponse.__content_type__
    assert mock_route.calls.last.response.status_code == 200


async def test_async_news_api_search_news(async_news_api: AsyncNewsAPI, response_mock: MockRouter):
    mock_search_response = MockSearchResponse.build()

    mock_route = response_mock.get("/v1/news/search").respond(
        content=mock_search_response.model_dump_json()
    )

    response = await async_news_api.search_news(query="query")

    assert isinstance(response, SearchResponse)
    assert response.__content_type__ == mock_search_response.__content_type__
    assert response.model_dump() == mock_search_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/news/search"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == SearchResponse.__content_type__
    assert mock_route.calls.last.response.status_code == 200


def test_sync_news_api_source_report(sync_news_api: NewsAPI, response_mock: MockRouter):
    mock_source_report_response = MockSourceReportResponse.build()

    mock_route = response_mock.get("/v1/sources").respond(
        content=mock_source_report_response.model_dump_json()
    )

    response = sync_news_api.get_sources_report()

    assert isinstance(response, SourceReportResponse)
    assert response.__content_type__ == mock_source_report_response.__content_type__
    assert response.model_dump() == mock_source_report_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/sources"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == SourceReportResponse.__content_type__
    assert mock_route.calls.last.response.status_code == 200


async def test_async_news_api_source_report(
    async_news_api: AsyncNewsAPI, response_mock: MockRouter
):
    mock_source_report_response = MockSourceReportResponse.build()

    mock_route = response_mock.get("/v1/sources").respond(
        content=mock_source_report_response.model_dump_json()
    )

    response = await async_news_api.get_sources_report()

    assert isinstance(response, SourceReportResponse)
    assert response.__content_type__ == mock_source_report_response.__content_type__
    assert response.model_dump() == mock_source_report_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/sources"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == SourceReportResponse.__content_type__
    assert mock_route.calls.last.response.status_code == 200
