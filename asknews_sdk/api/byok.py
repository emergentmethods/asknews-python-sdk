from typing import Dict, Optional

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.byok import ApiKeyResponse, Provider, UpsertApiKeyRequest


class ByokAPI(BaseAPI[APIClient]):
    """
    Bring Your Own Key (BYOK) API

    https://docs.asknews.app/en/reference#tag--byok
    """

    def set_byok_key(
        self,
        provider: Provider,
        api_key: str,
        *,
        http_headers: Optional[Dict] = None,
    ) -> ApiKeyResponse:
        """
        Store or update a BYOK API key for a provider.

        https://docs.asknews.app/en/reference#put-/v1/byok/{provider}

        :param provider: The provider name (e.g. "anthropic", "google").
        :type provider: str
        :param api_key: The API key to store.
        :type api_key: str
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The stored key hint response.
        :rtype: ApiKeyResponse
        """
        response = self.client.request(
            method="PUT",
            endpoint=f"/v1/byok/{provider}",
            body=UpsertApiKeyRequest(api_key=api_key).model_dump(mode="json"),
            headers={
                **(http_headers or {}),
                "Content-Type": UpsertApiKeyRequest.__content_type__,
            },
            accept=[(ApiKeyResponse.__content_type__, 1.0)],
        )
        return ApiKeyResponse.model_validate(response.content)

    def get_byok_key(
        self,
        provider: Provider,
        *,
        http_headers: Optional[Dict] = None,
    ) -> ApiKeyResponse:
        """
        Get the stored BYOK API key hint for a provider.

        https://docs.asknews.app/en/reference#get-/v1/byok/{provider}

        :param provider: The provider name (e.g. "anthropic", "google").
        :type provider: str
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The key hint response.
        :rtype: ApiKeyResponse
        """
        response = self.client.request(
            method="GET",
            endpoint=f"/v1/byok/{provider}",
            headers=http_headers,
            accept=[(ApiKeyResponse.__content_type__, 1.0)],
        )
        return ApiKeyResponse.model_validate(response.content)

    def delete_byok_key(
        self,
        provider: Provider,
        *,
        http_headers: Optional[Dict] = None,
    ) -> None:
        """
        Delete the stored BYOK API key for a provider.

        https://docs.asknews.app/en/reference#delete-/v1/byok/{provider}

        :param provider: The provider name (e.g. "anthropic", "google").
        :type provider: str
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: None
        :rtype: None
        """
        self.client.request(
            method="DELETE",
            endpoint=f"/v1/byok/{provider}",
            headers=http_headers,
        )


class AsyncByokAPI(BaseAPI[AsyncAPIClient]):
    """
    Bring Your Own Key (BYOK) API (async)

    https://docs.asknews.app/en/reference#tag--byok
    """

    async def set_byok_key(
        self,
        provider: Provider,
        api_key: str,
        *,
        http_headers: Optional[Dict] = None,
    ) -> ApiKeyResponse:
        """
        Store or update a BYOK API key for a provider.

        https://docs.asknews.app/en/reference#put-/v1/byok/{provider}

        :param provider: The provider name (e.g. "anthropic", "google").
        :type provider: str
        :param api_key: The API key to store.
        :type api_key: str
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The stored key hint response.
        :rtype: ApiKeyResponse
        """
        response = await self.client.request(
            method="PUT",
            endpoint=f"/v1/byok/{provider}",
            body=UpsertApiKeyRequest(api_key=api_key).model_dump(mode="json"),
            headers={
                **(http_headers or {}),
                "Content-Type": UpsertApiKeyRequest.__content_type__,
            },
            accept=[(ApiKeyResponse.__content_type__, 1.0)],
        )
        return ApiKeyResponse.model_validate(response.content)

    async def get_byok_key(
        self,
        provider: Provider,
        *,
        http_headers: Optional[Dict] = None,
    ) -> ApiKeyResponse:
        """
        Get the stored BYOK API key hint for a provider.

        https://docs.asknews.app/en/reference#get-/v1/byok/{provider}

        :param provider: The provider name (e.g. "anthropic", "google").
        :type provider: str
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The key hint response.
        :rtype: ApiKeyResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint=f"/v1/byok/{provider}",
            headers=http_headers,
            accept=[(ApiKeyResponse.__content_type__, 1.0)],
        )
        return ApiKeyResponse.model_validate(response.content)

    async def delete_byok_key(
        self,
        provider: Provider,
        *,
        http_headers: Optional[Dict] = None,
    ) -> None:
        """
        Delete the stored BYOK API key for a provider.

        https://docs.asknews.app/en/reference#delete-/v1/byok/{provider}

        :param provider: The provider name (e.g. "anthropic", "google").
        :type provider: str
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: None
        :rtype: None
        """
        await self.client.request(
            method="DELETE",
            endpoint=f"/v1/byok/{provider}",
            headers=http_headers,
        )
