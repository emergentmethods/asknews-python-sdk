from typing import Dict, List, Literal, Optional

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.distribution import (
    DomainMetricsResponse,
    DomainMetricsTimeWindowResponse,
    TopNArticlesForDomainResponse,
)


class DistributionAPI(BaseAPI[APIClient]):
    """Distribution API."""

    def get_domain_metrics(
        self,
        domain_names: List[str],
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> DomainMetricsResponse:
        """Get raw publisher metric event counts for domains."""
        response = self.client.request(
            method="GET",
            endpoint="/v1/distribution/stats/metrics",
            query={
                "domain_names": domain_names,
                "start_date": start_date,
                "end_date": end_date,
            },
            headers=http_headers,
            accept=[(DomainMetricsResponse.__content_type__, 1.0)],
        )
        return DomainMetricsResponse.model_validate(response.content)

    def get_domain_metrics_timeseries(
        self,
        domain_names: List[str],
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> DomainMetricsTimeWindowResponse:
        """Get raw publisher metric event counts per day for domains."""
        response = self.client.request(
            method="GET",
            endpoint="/v1/distribution/stats/metrics_timeseries",
            query={
                "domain_names": domain_names,
                "start_date": start_date,
                "end_date": end_date,
            },
            headers=http_headers,
            accept=[(DomainMetricsTimeWindowResponse.__content_type__, 1.0)],
        )
        return DomainMetricsTimeWindowResponse.model_validate(response.content)

    def get_top_n_articles_for_domains(
        self,
        domain_names: List[str],
        limit: int = 10,
        page: int = 1,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        metric: Literal["surface", "citation", "grounded"] = "surface",
        *,
        http_headers: Optional[Dict] = None,
    ) -> TopNArticlesForDomainResponse:
        """Get top domain articles ranked by raw counts for the selected metric.

        :param domain_names: Domain names to filter by.
        :param limit: Page size (1–100), defaults to 10.
        :param page: Page number (1-based), defaults to 1.
        :param start_date: Start timestamp in seconds since epoch.
        :param end_date: End timestamp in seconds since epoch.
        :param metric: Ranking metric: surface, citation, or grounded.
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/distribution/articles/top_n_for_domains",
            query={
                "domain_names": domain_names,
                "limit": limit,
                "page": page,
                "start_date": start_date,
                "end_date": end_date,
                "metric": metric,
            },
            headers=http_headers,
            accept=[(TopNArticlesForDomainResponse.__content_type__, 1.0)],
        )
        return TopNArticlesForDomainResponse.model_validate(response.content)


class AsyncDistributionAPI(BaseAPI[AsyncAPIClient]):
    """Distribution API (async)."""

    async def get_domain_metrics(
        self,
        domain_names: List[str],
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> DomainMetricsResponse:
        """Get raw publisher metric event counts for domains."""
        response = await self.client.request(
            method="GET",
            endpoint="/v1/distribution/stats/metrics",
            query={
                "domain_names": domain_names,
                "start_date": start_date,
                "end_date": end_date,
            },
            headers=http_headers,
            accept=[(DomainMetricsResponse.__content_type__, 1.0)],
        )
        return DomainMetricsResponse.model_validate(response.content)

    async def get_domain_metrics_timeseries(
        self,
        domain_names: List[str],
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> DomainMetricsTimeWindowResponse:
        """Get raw publisher metric event counts per day for domains."""
        response = await self.client.request(
            method="GET",
            endpoint="/v1/distribution/stats/metrics_timeseries",
            query={
                "domain_names": domain_names,
                "start_date": start_date,
                "end_date": end_date,
            },
            headers=http_headers,
            accept=[(DomainMetricsTimeWindowResponse.__content_type__, 1.0)],
        )
        return DomainMetricsTimeWindowResponse.model_validate(response.content)

    async def get_top_n_articles_for_domains(
        self,
        domain_names: List[str],
        limit: int = 10,
        page: int = 1,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        metric: Literal["surface", "citation", "grounded"] = "surface",
        *,
        http_headers: Optional[Dict] = None,
    ) -> TopNArticlesForDomainResponse:
        """Get top domain articles ranked by raw counts for the selected metric.

        :param domain_names: Domain names to filter by.
        :param limit: Page size (1–100), defaults to 10.
        :param page: Page number (1-based), defaults to 1.
        :param start_date: Start timestamp in seconds since epoch.
        :param end_date: End timestamp in seconds since epoch.
        :param metric: Ranking metric: surface, citation, or grounded.
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/distribution/articles/top_n_for_domains",
            query={
                "domain_names": domain_names,
                "limit": limit,
                "page": page,
                "start_date": start_date,
                "end_date": end_date,
                "metric": metric,
            },
            headers=http_headers,
            accept=[(TopNArticlesForDomainResponse.__content_type__, 1.0)],
        )
        return TopNArticlesForDomainResponse.model_validate(response.content)
