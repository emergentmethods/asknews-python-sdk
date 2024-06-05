from datetime import datetime
from typing import Dict, Literal, Optional, Union

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.sentiment import FinanceResponse


class AnalyticsAPI(BaseAPI):
    """
    Analytics API

    https://docs.asknews.app/en/reference#tag--analytics
    """

    def get_asset_sentiment(
        self,
        asset: Literal[
            "bitcoin",
            "ethereum",
            "cardano",
            "uniswap",
            "ripple",
            "solana",
            "polkadot",
            "polygon",
            "chainlink",
            "tether",
            "dogecoin",
            "monero",
            "tron",
            "binance",
            "aave",
            "tesla",
            "microsoft",
            "amazon",
        ],
        metric: Literal[
            "news_positive",
            "news_negative",
            "news_total",
            "news_positive_weighted",
            "news_negative_weighted",
            "news_total_weighted",
        ] = "news_positive",
        date_from: Optional[Union[datetime, str]] = None,
        date_to: Optional[Union[datetime, str]] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> FinanceResponse:
        """
        Get the timeseries sentiment for an asset.

        https://docs.asknews.app/en/reference#get-/v1/analytics/finance/sentiment

        :param slug: The asset slug.
        :type slug: str
        :param metric: The sentiment metric.
        :type metric: str
        :param date_from: The start date in ISO format.
        :type date_from: Optional[Union[str, datetime]]
        :param date_to: The end date in ISO format.
        :type date_to: Optional[Union[str, datetime]]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The sentiment response.
        :rtype: FinanceResponse
        """
        if isinstance(date_from, datetime):
            date_from = date_from.isoformat()
        if isinstance(date_to, datetime):
            date_to = date_to.isoformat()

        response = self.client.request(
            method="GET",
            endpoint="/v1/analytics/finance/sentiment",
            query={
                "asset": asset,
                "metric": metric,
                "date_from": date_from,
                "date_to": date_to,
            },
            headers=http_headers,
            accept=[(FinanceResponse.__content_type__, 1.0)],
        )
        return FinanceResponse.model_validate(response.content)


class AsyncAnalyticsAPI(BaseAPI):
    """
    Analytics API

    https://docs.asknews.app/en/reference#tag--analytics
    """

    async def get_asset_sentiment(
        self,
        asset: Literal[
            "bitcoin",
            "ethereum",
            "cardano",
            "uniswap",
            "ripple",
            "solana",
            "polkadot",
            "polygon",
            "chainlink",
            "tether",
            "dogecoin",
            "monero",
            "tron",
            "binance",
            "aave",
            "tesla",
            "microsoft",
            "amazon",
        ],
        metric: Literal[
            "news_positive",
            "news_negative",
            "news_total",
            "news_positive_weighted",
            "news_negative_weighted",
            "news_total_weighted",
        ] = "news_positive",
        date_from: Optional[Union[datetime, str]] = None,
        date_to: Optional[Union[datetime, str]] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> FinanceResponse:
        """
        Get the timeseries sentiment for an asset.

        https://docs.asknews.app/en/reference#get-/v1/analytics/finance/sentiment

        :param slug: The asset slug.
        :type slug: str
        :param metric: The sentiment metric.
        :type metric: str
        :param date_from: The start date in ISO format.
        :type date_from: Optional[Union[str, datetime]]
        :param date_to: The end date in ISO format.
        :type date_to: Optional[Union[str, datetime]]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The sentiment response.
        :rtype: FinanceResponse
        """
        if isinstance(date_from, datetime):
            date_from = date_from.isoformat()
        if isinstance(date_to, datetime):
            date_to = date_to.isoformat()

        response = await self.client.request(
            method="GET",
            endpoint="/v1/analytics/finance/sentiment",
            query={
                "asset": asset,
                "metric": metric,
                "date_from": date_from,
                "date_to": date_to,
            },
            headers=http_headers,
            accept=[(FinanceResponse.__content_type__, 1.0)],
        )
        return FinanceResponse.model_validate(response.content)
