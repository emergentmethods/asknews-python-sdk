from inspect import signature
from typing import get_args, get_type_hints
from urllib.parse import parse_qs

import pytest
from respx import MockRouter

from asknews_sdk.api.distribution import AsyncDistributionAPI, DistributionAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.distribution import (
    DomainMetricsResponse,
    DomainMetricsTimeWindowResponse,
    TopNArticlesForDomainResponse,
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


TOP_N_PAYLOAD = {
    "data": [{"article_url": "https://example.com/news", "hit_count": 12}],
    "total_count": 1,
}


@pytest.mark.parametrize("metric", ["surface", "citation", "grounded"])
def test_sync_top_n_articles_serialization(sync_distribution_api, response_mock, metric):
    route = response_mock.get("/v1/distribution/articles/top_n_for_domains").respond(
        json=TOP_N_PAYLOAD
    )
    response = sync_distribution_api.get_top_n_articles_for_domains(
        DOMAIN_NAMES,
        limit=25,
        page=2,
        start_date=START_DATE,
        end_date=END_DATE,
        metric=metric,
        http_headers={"custom-header": "custom-value"},
    )
    request = route.calls.last.request
    assert request.method == "GET"
    assert request.headers["accept"] == TopNArticlesForDomainResponse.__content_type__
    assert request.headers["custom-header"] == "custom-value"
    assert parse_qs(request.url.query.decode()) == {
        "domain_names": DOMAIN_NAMES,
        "limit": ["25"],
        "page": ["2"],
        "start_date": [str(START_DATE)],
        "end_date": [str(END_DATE)],
        "metric": [metric],
    }
    assert response == TopNArticlesForDomainResponse(**TOP_N_PAYLOAD)
    assert response.data[0].article_id is None
    assert response.page == 1
    assert response.next_page is None


@pytest.mark.parametrize("metric", ["surface", "citation", "grounded"])
async def test_async_top_n_articles_serialization(async_distribution_api, response_mock, metric):
    payload = {
        "data": [
            {"article_url": "https://example.com/news", "article_id": "article-1", "hit_count": 5}
        ],
        "total_count": 3,
        "page": 2,
        "next_page": 3,
    }
    route = response_mock.get("/v1/distribution/articles/top_n_for_domains").respond(json=payload)
    response = await async_distribution_api.get_top_n_articles_for_domains(
        DOMAIN_NAMES,
        limit=1,
        page=2,
        start_date=START_DATE,
        end_date=END_DATE,
        metric=metric,
        http_headers={"custom-header": "custom-value"},
    )
    request = route.calls.last.request
    assert request.method == "GET"
    assert request.headers["accept"] == TopNArticlesForDomainResponse.__content_type__
    assert request.headers["custom-header"] == "custom-value"
    assert parse_qs(request.url.query.decode()) == {
        "domain_names": DOMAIN_NAMES,
        "limit": ["1"],
        "page": ["2"],
        "start_date": [str(START_DATE)],
        "end_date": [str(END_DATE)],
        "metric": [metric],
    }
    assert response == TopNArticlesForDomainResponse(**payload)


@pytest.mark.parametrize("use_async", [False, True])
async def test_top_n_articles_defaults(
    sync_distribution_api, async_distribution_api, response_mock, use_async
):
    payload = {"data": [], "total_count": 0, "next_page": None}
    route = response_mock.get("/v1/distribution/articles/top_n_for_domains").respond(json=payload)
    if use_async:
        response = await async_distribution_api.get_top_n_articles_for_domains(DOMAIN_NAMES)
    else:
        response = sync_distribution_api.get_top_n_articles_for_domains(DOMAIN_NAMES)
    assert response.data == []
    assert parse_qs(route.calls.last.request.url.query.decode()) == {
        "domain_names": DOMAIN_NAMES,
        "limit": ["10"],
        "page": ["1"],
        "metric": ["surface"],
    }


@pytest.mark.parametrize("api_type", [DistributionAPI, AsyncDistributionAPI])
def test_top_n_signature_matches_production_contract(api_type):
    from tests.api.test_chat_model_types import PRODUCTION_CONTRACT

    method = api_type.get_top_n_articles_for_domains
    params = signature(method).parameters
    assert set(params) - {"self", "http_headers"} == {
        param["name"] for param in PRODUCTION_CONTRACT["top_n_parameters"]
    }
    for param in PRODUCTION_CONTRACT["top_n_parameters"]:
        if not param["required"]:
            assert params[param["name"]].default == param["schema"].get("default")
    assert get_args(get_type_hints(method)["metric"]) == ("surface", "citation", "grounded")
