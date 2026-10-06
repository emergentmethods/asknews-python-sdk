from urllib.parse import parse_qs

import pytest
from respx import MockRouter

from asknews_sdk.api.distribution import AsyncDistributionAPI, DistributionAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.distribution import DomainMetricsResponse, DomainMetricsTimeWindowResponse
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
