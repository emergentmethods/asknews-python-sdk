from urllib.parse import parse_qs

import pytest
from respx import MockRouter

from asknews_sdk.api.distribution import AsyncDistributionAPI, DistributionAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.distribution import (
    DomainMetricsResponse, DomainMetricsTimeWindowResponse,
    HitShareResponse, TopNArticlesForDomainResponse,
)
from asknews_sdk.sdk import AskNewsSDK, AsyncAskNewsSDK


DOMAIN_NAMES = ["example.com", "example.org"]
START_DATE = 1_700_000_000
END_DATE = 1_700_086_400


@pytest.fixture
def sync_distribution_api(sync_api_client: APIClient):
    return DistributionAPI(sync_api_client)


@pytest.fixture
def async_distribution_api(async_api_client: AsyncAPIClient):
    return AsyncDistributionAPI(async_api_client)


def test_sync_sdk_exposes_distribution_api():
    with AskNewsSDK(auth=None) as sdk:
        assert isinstance(sdk.distribution, DistributionAPI)


@pytest.mark.asyncio
async def test_async_sdk_exposes_distribution_api():
    async with AsyncAskNewsSDK(auth=None) as sdk:
        assert isinstance(sdk.distribution, AsyncDistributionAPI)


def test_sync_get_domain_metrics(sync_distribution_api: DistributionAPI, response_mock: MockRouter):
    payload = {"surfaces": 12, "citations": 7, "full_text": 3}
    mock_route = response_mock.get("/v1/distribution/stats/metrics").respond(json=payload)

    response = sync_distribution_api.get_domain_metrics(
        DOMAIN_NAMES,
        start_date=START_DATE,
        end_date=END_DATE,
        http_headers={"custom-header": "custom-value"},
    )

    assert response == DomainMetricsResponse(**payload)
    request = mock_route.calls.last.request
    assert request.method == "GET"
    assert request.headers["accept"] == DomainMetricsResponse.__content_type__
    assert request.headers["custom-header"] == "custom-value"
    assert parse_qs(request.url.query.decode()) == {
        "domain_names": DOMAIN_NAMES,
        "start_date": [str(START_DATE)],
        "end_date": [str(END_DATE)],
    }


def test_sync_get_domain_metrics_timeseries(
    sync_distribution_api: DistributionAPI, response_mock: MockRouter
):
    payload = {
        "data": [{"day": "2026-08-01", "surfaces": 5, "citations": 3, "full_text": 1}],
        "total_surfaces": 5,
        "total_citations": 3,
        "total_full_text": 1,
    }
    mock_route = response_mock.get("/v1/distribution/stats/metrics_timeseries").respond(
        json=payload
    )

    response = sync_distribution_api.get_domain_metrics_timeseries(DOMAIN_NAMES)

    assert response == DomainMetricsTimeWindowResponse(**payload)
    request = mock_route.calls.last.request
    assert request.method == "GET"
    assert request.headers["accept"] == DomainMetricsTimeWindowResponse.__content_type__
    assert parse_qs(request.url.query.decode()) == {"domain_names": DOMAIN_NAMES}


@pytest.mark.asyncio
async def test_async_get_domain_metrics(
    async_distribution_api: AsyncDistributionAPI, response_mock: MockRouter
):
    payload = {"surfaces": 12, "citations": 7, "full_text": 3}
    mock_route = response_mock.get("/v1/distribution/stats/metrics").respond(json=payload)

    response = await async_distribution_api.get_domain_metrics(
        DOMAIN_NAMES, start_date=START_DATE, end_date=END_DATE
    )

    assert response == DomainMetricsResponse(**payload)
    assert parse_qs(mock_route.calls.last.request.url.query.decode()) == {
        "domain_names": DOMAIN_NAMES,
        "start_date": [str(START_DATE)],
        "end_date": [str(END_DATE)],
    }


@pytest.mark.asyncio
async def test_async_get_domain_metrics_timeseries(
    async_distribution_api: AsyncDistributionAPI, response_mock: MockRouter
):
    payload = {
        "data": [{"day": "2026-08-01", "surfaces": 5, "citations": 3, "full_text": 1}],
        "total_surfaces": 5,
        "total_citations": 3,
        "total_full_text": 1,
    }
    mock_route = response_mock.get("/v1/distribution/stats/metrics_timeseries").respond(
        json=payload
    )

    response = await async_distribution_api.get_domain_metrics_timeseries(DOMAIN_NAMES)

    assert response == DomainMetricsTimeWindowResponse(**payload)
    assert parse_qs(mock_route.calls.last.request.url.query.decode()) == {
        "domain_names": DOMAIN_NAMES
    }


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("custom", [False, True])
async def test_get_domain_hit_share(
    is_async, custom, sync_distribution_api, async_distribution_api, response_mock
):
    payload = {"data": [{"domain": "example.com", "hit_share": 0.25}], "total_share": 0.25}
    route = response_mock.get("/v1/distribution/stats/hit_share").respond(json=payload)
    api = async_distribution_api if is_async else sync_distribution_api
    kwargs = {"start_date": START_DATE, "end_date": END_DATE, "is_publisher": False} if custom else {}
    result = api.get_domain_hit_share(
        DOMAIN_NAMES, **kwargs, http_headers={"custom-header": "custom-value"}
    )
    response = await result if is_async else result
    assert isinstance(response, HitShareResponse)
    assert response == HitShareResponse(**payload)
    assert response.data[0].domain == "example.com"
    assert response.data[0].hit_share == 0.25
    request = route.calls.last.request
    assert request.method == "GET"
    assert request.headers["accept"] == "application/json"
    assert request.headers["custom-header"] == "custom-value"
    expected = {"domain_names": DOMAIN_NAMES, "is_publisher": ["False" if custom else "True"]}
    if custom:
        expected.update(start_date=[str(START_DATE)], end_date=[str(END_DATE)])
    assert parse_qs(request.url.query.decode()) == expected


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("metric", [None, "surface", "citation", "grounded"])
async def test_get_top_n_articles_for_domains(
    is_async, metric, sync_distribution_api, async_distribution_api, response_mock
):
    payload = {
        "data": [{"article_url": "https://example.com/story", "article_id": "article-1", "hit_count": 42}],
        "total_count": 80, "page": 2, "next_page": 3,
    }
    route = response_mock.get("/v1/distribution/articles/top_n_for_domains").respond(json=payload)
    api = async_distribution_api if is_async else sync_distribution_api
    kwargs = {} if metric is None else {
        "limit": 25, "page": 2, "start_date": START_DATE, "end_date": END_DATE, "metric": metric,
    }
    result = api.get_top_n_articles_for_domains(
        DOMAIN_NAMES, **kwargs, http_headers={"custom-header": "custom-value"}
    )
    response = await result if is_async else result
    assert isinstance(response, TopNArticlesForDomainResponse)
    assert response == TopNArticlesForDomainResponse(**payload)
    assert response.data[0].article_id == "article-1"
    assert response.data[0].hit_count == 42
    request = route.calls.last.request
    assert request.method == "GET"
    assert request.headers["accept"] == "application/json"
    assert request.headers["custom-header"] == "custom-value"
    expected = {"domain_names": DOMAIN_NAMES, "limit": ["10"], "page": ["1"], "metric": ["surface"]}
    if metric is not None:
        expected.update(limit=["25"], page=["2"], metric=[metric],
                        start_date=[str(START_DATE)], end_date=[str(END_DATE)])
    assert parse_qs(request.url.query.decode()) == expected
