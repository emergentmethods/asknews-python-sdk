from __future__ import annotations

from typing import Optional, Set, Type, Union

from httpx import AsyncClient, Client

from asknews_sdk.api import (
    AnalyticsAPI,
    AsyncAnalyticsAPI,
    AsyncChatAPI,
    AsyncNewsAPI,
    AsyncStoriesAPI,
    ChatAPI,
    NewsAPI,
    StoriesAPI,
)
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.base import PingResponse
from asknews_sdk.security import (
    AsyncTokenLoadHook,
    AsyncTokenSaveHook,
    TokenLoadHook,
    TokenSaveHook,
)
from asknews_sdk.types import CLIENT_DEFAULT, RequestAuth, Sentinel


DEFAULT_API_BASE_URL = "https://api.asknews.app"
DEFAULT_TOKEN_URL = "https://auth.asknews.app/oauth2/token"
DEFAULT_SCOPES = ["news", "stories", "chat", "analytics"]


class AskNewsSDK:
    """
    The AskNews SDK client for communicating with the AskNews API.

    Usage:

    ```python
    >>> with AskNewsSDK(client_id=..., client_secret=...) as sdk:
    >>>    stories_response = sdk.stories.get_stories(...)
    ```

    :param client_id: The client ID for your AskNews API application.
    :type client_id: str
    :param client_secret: The client secret for your AskNews API application.
    :type client_secret: str
    :param scopes: The scopes to request for your AskNews API application.
    :type scopes: Optional[Set[str]]
    :param base_url: The base URL for the AskNews API.
    :type base_url: str
    :param token_url: The token URL for the AskNews API.
    :type token_url: str
    :param verify_ssl: Whether or not to verify SSL certificates.
    :type verify_ssl: bool
    :param retries: The number of retries to attempt on connection errors.
    :type retries: int
    :param timeout: The timeout for requests.
    :type timeout: Optional[float]
    :param follow_redirects: Whether or not to follow redirects.
    :type follow_redirects: bool
    :param client: The HTTP client to use.
    :type client: Union[Type[Client], Client]
    :param kwargs: Additional keyword arguments to pass to the HTTP client.
    :type kwargs: Any
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        scopes: Optional[Set[str]] = DEFAULT_SCOPES,
        base_url: str = DEFAULT_API_BASE_URL,
        token_url: str = DEFAULT_TOKEN_URL,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        client: Union[Type[Client], Client] = Client,
        auth: Optional[RequestAuth | Sentinel] = CLIENT_DEFAULT,
        *,
        _token_load_hook: Optional[TokenLoadHook] = None,
        _token_save_hook: Optional[TokenSaveHook] = None,
        **kwargs,
    ) -> None:
        self.client = APIClient(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            base_url=base_url,
            token_url=token_url,
            verify_ssl=verify_ssl,
            retries=retries,
            timeout=timeout,
            follow_redirects=follow_redirects,
            client=client,
            auth=auth,
            _token_load_hook=_token_load_hook,
            _token_save_hook=_token_save_hook,
            **kwargs,
        )

        self.analytics = AnalyticsAPI(self.client)
        self.stories = StoriesAPI(self.client)
        self.news = NewsAPI(self.client)
        self.chat = ChatAPI(self.client)

    def __enter__(self) -> AskNewsSDK:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.client.__exit__(exc_type, exc, tb)

    def close(self) -> None:
        """
        Close the SDK
        """
        self.client.close()

    def ping(self) -> PingResponse:
        """
        Ping the AskNews API and get the version.

        :return: The response from the API.
        :rtype: PingResponse
        """
        response = self.client.request(method="GET", endpoint="/")
        return PingResponse.model_validate(response.content)


class AsyncAskNewsSDK:
    """
    The Async AskNews SDK client for communicating with the AskNews API.

    Usage:

    ```python
    >>> async with AskNewsSDK(client_id=..., client_secret=...) as sdk:
    >>>    stories_response = await sdk.stories.get_stories(...)
    ```

    :param client_id: The client ID for your AskNews API application.
    :type client_id: str
    :param client_secret: The client secret for your AskNews API application.
    :type client_secret: str
    :param scopes: The scopes to request for your AskNews API application.
    :type scopes: Optional[Set[str]]
    :param base_url: The base URL for the AskNews API.
    :type base_url: str
    :param token_url: The token URL for the AskNews API.
    :type token_url: str
    :param verify_ssl: Whether or not to verify SSL certificates.
    :type verify_ssl: bool
    :param retries: The number of retries to attempt on connection errors.
    :type retries: int
    :param timeout: The timeout for requests.
    :type timeout: Optional[float]
    :param follow_redirects: Whether or not to follow redirects.
    :type follow_redirects: bool
    :param client: The HTTP client to use.
    :type client: Union[Type[AsyncClient], AsyncClient]
    :param kwargs: Additional keyword arguments to pass to the HTTP client.
    :type kwargs: Any
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        scopes: Optional[Set[str]] = DEFAULT_SCOPES,
        base_url: str = DEFAULT_API_BASE_URL,
        token_url: str = DEFAULT_TOKEN_URL,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        client: Union[Type[AsyncClient], AsyncClient] = AsyncClient,
        auth: Optional[RequestAuth | Sentinel] = CLIENT_DEFAULT,
        *,
        _token_load_hook: Optional[AsyncTokenLoadHook] = None,
        _token_save_hook: Optional[AsyncTokenSaveHook] = None,
        **kwargs,
    ) -> None:
        self.client = AsyncAPIClient(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            base_url=base_url,
            token_url=token_url,
            verify_ssl=verify_ssl,
            retries=retries,
            timeout=timeout,
            follow_redirects=follow_redirects,
            client=client,
            auth=auth,
            _token_load_hook=_token_load_hook,
            _token_save_hook=_token_save_hook,
            **kwargs,
        )

        self.analytics = AsyncAnalyticsAPI(self.client)
        self.stories = AsyncStoriesAPI(self.client)
        self.news = AsyncNewsAPI(self.client)
        self.chat = AsyncChatAPI(self.client)

    async def __aenter__(self) -> AsyncAskNewsSDK:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.client.__aexit__(exc_type, exc, tb)

    async def close(self) -> None:
        """
        Close the SDK client.
        """
        await self.client.close()

    async def ping(self) -> PingResponse:
        """
        Ping the AskNews API and get the version.

        :return: The response from the API.
        :rtype: PingResponse
        """
        response = await self.client.request(method="GET", endpoint="/")
        return PingResponse.model_validate(response.content)
