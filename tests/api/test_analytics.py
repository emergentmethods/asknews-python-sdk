from datetime import datetime, timedelta
from urllib.parse import parse_qs

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from respx import MockRouter

from asknews_sdk.api.analytics import AnalyticsAPI, AsyncAnalyticsAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.sentiment import FinanceResponse


class MockFinanceResponse(ModelFactory[FinanceResponse]):
    ...


@pytest.fixture
def sync_analytics_api(sync_api_client: APIClient):
    return AnalyticsAPI(sync_api_client)


@pytest.fixture
def async_analytics_api(async_api_client: AsyncAPIClient):
    return AsyncAnalyticsAPI(async_api_client)


def test_sync_analytics_api_get_asset_sentiment(
    sync_analytics_api: AnalyticsAPI, response_mock: MockRouter
):
    asset = "bitcoin"
    date_from = datetime.now() - timedelta(days=1)
    date_to = datetime.now()
    mock_response = MockFinanceResponse.build()

    mock_route = response_mock.get("/v1/analytics/finance/sentiment").respond(content=mock_response.model_dump_json())

    response = sync_analytics_api.get_asset_sentiment(
        asset,
        date_from=date_from,
        date_to=date_to,
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, FinanceResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/analytics/finance/sentiment"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == FinanceResponse.__content_type__
    assert mock_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert parse_qs(mock_route.calls.last.request.url.query.decode()) == {
        "asset": [asset],
        "metric": ["news_positive"],
        "date_from": [date_from.isoformat()],
        "date_to": [date_to.isoformat()],
    }


async def test_async_analytics_api_get_asset_sentiment(
    async_analytics_api: AsyncAnalyticsAPI, response_mock: MockRouter
):
    asset = "bitcoin"
    date_from = datetime.now() - timedelta(days=1)
    date_to = datetime.now()
    mock_response = MockFinanceResponse.build()

    mock_route = response_mock.get("/v1/analytics/finance/sentiment").respond(content=mock_response.model_dump_json())

    response = await async_analytics_api.get_asset_sentiment(
        asset,
        date_from=date_from,
        date_to=date_to,
        http_headers={
            "custom-header": "custom-value",
        }
    )

    assert isinstance(response, FinanceResponse)
    assert response.__content_type__ == mock_response.__content_type__
    assert response.model_dump() == mock_response.model_dump()

    assert mock_route.called
    assert mock_route.calls.last.request.url.path == "/v1/analytics/finance/sentiment"
    assert mock_route.calls.last.request.method == "GET"
    assert mock_route.calls.last.request.headers["accept"] == FinanceResponse.__content_type__
    assert mock_route.calls.last.request.headers["custom-header"] == "custom-value"
    assert parse_qs(response_mock.calls.last.request.url.query.decode()) == {
        "asset": [asset],
        "metric": ["news_positive"],
        "date_from": [date_from.isoformat()],
        "date_to": [date_to.isoformat()],
    }
