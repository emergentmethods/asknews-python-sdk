from typing import Dict, List, Optional

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.distribution import DomainMetricsResponse, DomainMetricsTimeWindowResponse


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
