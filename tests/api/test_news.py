from uuid import uuid4

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from respx import MockRouter

from asknews_sdk.api.news import AsyncNewsAPI, NewsAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.news import ArticleResponse, SearchResponse, SourceReportResponse
from asknews_sdk.errors import ResourceNotFoundError
from asknews_sdk.response import APIResponse, AsyncAPIResponse
from tests.test_wikidata_entities import build_article_payload


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

    response = sync_news_api.get_article(
        article_id,
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, ArticleResponse)
    assert response.__content_type__ == mock_article.__content_type__
    assert response.model_dump() == mock_article.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == f"/v1/news/{article_id}"
    assert mock_route.calls.last.request.headers["accept"] == ArticleResponse.__content_type__
    assert mock_route.calls.last.request.headers["custom-header"] == "custom-value"
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

    response = await async_news_api.get_article(
        article_id,
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, ArticleResponse)
    assert response.__content_type__ == mock_article.__content_type__
    assert response.model_dump() == mock_article.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == f"/v1/news/{article_id}"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == ArticleResponse.__content_type__
    assert mock_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mock_route.calls.last.response.status_code == 200

    mock_route = response_mock.get(f"/v1/news/{article_id}").respond(
        json={"code": ResourceNotFoundError.code, "detail": ResourceNotFoundError.detail},
        status_code=404
    )

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await async_news_api.get_article(article_id)

    assert isinstance(exc_info.value.response, AsyncAPIResponse)
    assert exc_info.value.code == ResourceNotFoundError.code
    assert exc_info.value.detail == ResourceNotFoundError.detail

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == f"/v1/news/{article_id}"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == ArticleResponse.__content_type__
    assert mock_route.calls.last.response.status_code == 404


@pytest.mark.parametrize("podcasts", ["include", "only", "none"])
def test_sync_news_api_search_news(
    sync_news_api: NewsAPI, response_mock: MockRouter, podcasts: str
):
    mock_search_response = MockSearchResponse.build()

    mock_route = response_mock.get("/v1/news/search").respond(
        content=mock_search_response.model_dump_json()
    )

    response = sync_news_api.search_news(
        "query",
        podcasts=podcasts,
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, SearchResponse)
    assert response.__content_type__ == mock_search_response.__content_type__
    assert response.model_dump() == mock_search_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/news/search"
    assert mock_route.calls.last.request.url.params["podcasts"] == podcasts
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == SearchResponse.__content_type__
    assert mock_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mock_route.calls.last.response.status_code == 200


async def test_async_news_api_search_news(async_news_api: AsyncNewsAPI, response_mock: MockRouter):
    mock_search_response = MockSearchResponse.build()

    mock_route = response_mock.get("/v1/news/search").respond(
        content=mock_search_response.model_dump_json()
    )

    response = await async_news_api.search_news(
        "query",
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, SearchResponse)
    assert response.__content_type__ == mock_search_response.__content_type__
    assert response.model_dump() == mock_search_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/news/search"
    assert mock_route.calls.last.request.url.params["podcasts"] == "include"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == SearchResponse.__content_type__
    assert mock_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mock_route.calls.last.response.status_code == 200


@pytest.mark.parametrize(
    "wikidata_entities",
    [
        None,
        {},
        {
            "Person": [
                {
                    "title": "Ada Lovelace",
                    "qid": "Q7259",
                    "relevance": 0.97,
                    "description": "English mathematician and writer",
                    "source_mention": "Lovelace",
                }
            ],
            "Organization": [{"title": "Analytical Engine", "qid": "Q332676", "relevance": 0.6}],
        },
    ],
)
async def test_async_news_api_search_news_wikidata_entities(
    async_news_api: AsyncNewsAPI, response_mock: MockRouter, wikidata_entities
):
    """`wikidata_entities` survives parsing of a structured search_news response."""
    mock_search_response = MockSearchResponse.build(as_string=None)
    payload = mock_search_response.model_dump(mode="json")
    payload["as_dicts"] = [build_article_payload(wikidata_entities=wikidata_entities)]

    mock_route = response_mock.get("/v1/news/search").respond(json=payload)

    response = await async_news_api.search_news("query", return_type="dicts")

    assert isinstance(response, SearchResponse)
    dumped_article = response.model_dump(mode="json", exclude_none=True)["as_dicts"][0]

    if wikidata_entities is None:
        assert response.as_dicts[0].wikidata_entities is None
        assert "wikidata_entities" not in dumped_article
    else:
        assert dumped_article["wikidata_entities"] == wikidata_entities

    assert mock_route.called


def test_sync_news_api_search_news_omitted_wikidata_entities(
    sync_news_api: NewsAPI, response_mock: MockRouter
):
    """An API response predating the property still parses, yielding None."""
    mock_search_response = MockSearchResponse.build(as_string=None)
    payload = mock_search_response.model_dump(mode="json")
    article_payload = build_article_payload()
    article_payload.pop("wikidata_entities", None)
    payload["as_dicts"] = [article_payload]

    mock_route = response_mock.get("/v1/news/search").respond(json=payload)

    response = sync_news_api.search_news("query", return_type="dicts")

    assert isinstance(response, SearchResponse)
    assert response.as_dicts[0].wikidata_entities is None
    assert mock_route.called


def test_sync_news_api_source_report(sync_news_api: NewsAPI, response_mock: MockRouter):
    mock_source_report_response = MockSourceReportResponse.build()

    mock_route = response_mock.get("/v1/sources").respond(
        content=mock_source_report_response.model_dump_json()
    )

    response = sync_news_api.get_sources_report(
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, SourceReportResponse)
    assert response.__content_type__ == mock_source_report_response.__content_type__
    assert response.model_dump() == mock_source_report_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/sources"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == SourceReportResponse.__content_type__
    assert mock_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mock_route.calls.last.response.status_code == 200


async def test_async_news_api_source_report(
    async_news_api: AsyncNewsAPI, response_mock: MockRouter
):
    mock_source_report_response = MockSourceReportResponse.build()

    mock_route = response_mock.get("/v1/sources").respond(
        content=mock_source_report_response.model_dump_json()
    )

    response = await async_news_api.get_sources_report(
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, SourceReportResponse)
    assert response.__content_type__ == mock_source_report_response.__content_type__
    assert response.model_dump() == mock_source_report_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/sources"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == SourceReportResponse.__content_type__
    assert mock_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert mock_route.calls.last.response.status_code == 200
