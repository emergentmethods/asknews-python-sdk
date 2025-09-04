from __future__ import annotations

from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)

from httpx import AsyncClient, Client, HTTPStatusError, Request, Response

from asknews_sdk.errors import raise_from_response
from asknews_sdk.response import APIResponse, AsyncAPIResponse
from asknews_sdk.security import (
    APIKey,
    AsyncTokenLoadHook,
    AsyncTokenSaveHook,
    OAuth2ClientCredentials,
    TokenLoadHook,
    TokenSaveHook,
)
from asknews_sdk.types import CLIENT_DEFAULT, RequestAuth, Sentinel, StreamType
from asknews_sdk.utils import (
    build_accept_header,
    build_url,
    determine_content_type,
    serialize,
)
from asknews_sdk.version import __version__


USER_AGENT = f"asknews-sdk-python/{__version__}"

TClient = TypeVar("TClient", Client, AsyncClient)
TResponse = TypeVar("TResponse", APIResponse, AsyncAPIResponse)

class BaseAPIClient(Generic[TClient, TResponse]):
    client_cls: Type[TClient]
    response_cls: Type[TResponse]

    def __init__(
        self,
        client_id: Optional[str],
        client_secret: Optional[str],
        scopes: Optional[Set[str]],
        api_key: Optional[str],
        base_url: str,
        token_url: str,
        verify_ssl: bool,
        retries: int,
        timeout: Optional[float],
        follow_redirects: bool,
        client: Union[Type[TClient], TClient],
        user_agent: str,
        auth: Optional[Union[RequestAuth, Sentinel]],
        *,
        _token_save_hook: Optional[Union[TokenSaveHook, AsyncTokenSaveHook]] = None,
        _token_load_hook: Optional[Union[TokenLoadHook, AsyncTokenLoadHook]] = None,
        **kwargs,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = {"offline", "openid", *(scopes or set())}
        self.api_key = api_key
        self.base_url = base_url
        self.token_url = token_url
        self.verify_ssl = verify_ssl
        self.retries = retries
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self._client_auth: Optional[RequestAuth] = None

        if auth:
            if auth is CLIENT_DEFAULT:
                if self.api_key is not None:
                    self._client_auth = APIKey(
                        api_key=self.api_key,
                    )
                elif self.client_id is not None and self.client_secret is not None:
                    self._client_auth = OAuth2ClientCredentials(
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                        token_url=self.token_url,
                        scopes=self.scopes,
                        _token_load_hook=_token_load_hook,
                        _token_save_hook=_token_save_hook,
                    )
                else:
                    raise ValueError(
                        "Either api_key or client_id and client_secret are "
                        "required for authentication. To explicitly disable "
                        "authentication, set auth=None.",
                    )
            else:
                assert not isinstance(auth, Sentinel)
                self._client_auth = auth

        self._client: TClient
        if isinstance(client, type):
            self._client = client(
                base_url=self.base_url,
                verify=self.verify_ssl,
                timeout=self.timeout,
                auth=self._client_auth,
                follow_redirects=self.follow_redirects,
                headers={"User-Agent": user_agent},
                **kwargs,
            )
        else:
            self._client = client

    def build_api_request(
        self,
        method: str,
        endpoint: str,
        body: Optional[Any] = None,
        query: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        accept: Optional[List[tuple[str, float]]] = None,
    ) -> Request:
        headers = headers or {}
        content_type = headers.pop("content-type", determine_content_type(body)) if body else None

        if content_type:
            headers["content-type"] = content_type

        headers["accept"] = build_accept_header(accept or [("application/json", 1.0)])

        return Request(
            method=method,
            url=build_url(
                base_url=self.base_url,
                endpoint=endpoint,
                query=query,
                params=params,
            ),
            content=serialize(body) if body and not isinstance(body, bytes) else body,
            headers=headers,
        )


class APIClient(BaseAPIClient[Client, APIResponse]):
    """
    Sync HTTP API Client

    :param client_id: Client ID
    :type client_id: Optional[str]
    :param client_secret: Client secret
    :type client_secret: Optional[str]
    :param scopes: OAuth scopes
    :type scopes: Optional[Set[str]]
    :param api_key: API key
    :type api_key: Optional[str]
    :param base_url: Base URL
    :type base_url: str
    :param token_url: Token URL
    :type token_url: str
    :param verify_ssl: Verify SSL certificate
    :type verify_ssl: bool
    :param retries: Default number of retries
    :type retries: int
    :param timeout: Request timeout
    :type timeout: Optional[float]
    :param follow_redirects: Follow redirects
    :type follow_redirects: bool
    """
    client_cls = Client
    response_cls = APIResponse

    def __init__(
        self,
        client_id: Optional[str],
        client_secret: Optional[str],
        scopes: Optional[Set[str]],
        api_key: Optional[str],
        base_url: str,
        token_url: str,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        client: Union[Type[Client], Client] = Client,
        user_agent: str = USER_AGENT,
        auth: Optional[Union[RequestAuth, Sentinel]] = CLIENT_DEFAULT,
        *,
        _token_save_hook: Optional[TokenSaveHook] = None,
        _token_load_hook: Optional[TokenLoadHook] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            api_key=api_key,
            base_url=base_url,
            token_url=token_url,
            verify_ssl=verify_ssl,
            retries=retries,
            timeout=timeout,
            follow_redirects=follow_redirects,
            client=client,
            user_agent=user_agent,
            auth=auth,
            _token_save_hook=_token_save_hook,
            _token_load_hook=_token_load_hook,
            **kwargs,
        )

    def close(self) -> None:
        """
        Close the Client.
        """
        self._client.close()

    def __enter__(self) -> APIClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

        if exc:
            raise exc

    def request(
        self,
        method: str,
        endpoint: str,
        body: Optional[Any] = None,
        query: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        accept: Optional[List[tuple[str, float]]] = None,
        stream: bool = False,
        stream_type: StreamType = "bytes",
    ) -> APIResponse:
        """
        Send an HTTP request.

        :param method: HTTP method
        :type method: str
        :param endpoint: API endpoint
        :type endpoint: str
        :param body: Request body
        :type body: Optional[Any]
        :param query: Query parameters
        :type query: Optional[Dict]
        :param headers: Request headers
        :type headers: Optional[Dict]
        :param params: Path parameters
        :type params: Optional[Dict]
        :param accept: Accept header
        :type accept: Optional[List[tuple[str, float]]]
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: APIResponse object
        :rtype: APIResponse
        """
        response: Response = self._client.send(
            self.build_api_request(
                method=method,
                endpoint=endpoint,
                body=body,
                query=query,
                headers=headers,
                params=params,
                accept=accept,
            ),
            stream=stream,
        )
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            if stream:
                response.read()

            raise_from_response(
                self.response_cls.from_httpx_response(
                    response=e.response,
                    stream=False,
                )
            )

        return self.response_cls.from_httpx_response(
            response=response,
            stream=stream,
            stream_type=stream_type,
        )


class AsyncAPIClient(BaseAPIClient[AsyncClient, AsyncAPIResponse]):
    """
    Base Async HTTP API Client

    :param client_id: Client ID
    :type client_id: Optional[str]
    :param client_secret: Client secret
    :type client_secret: Optional[str]
    :param scopes: OAuth scopes
    :type scopes: Optional[Set[str]]
    :param api_key: API key
    :type api_key: Optional[str]
    :param base_url: Base URL
    :type base_url: str
    :param token_url: Token URL
    :type token_url: str
    :param verify_ssl: Verify SSL certificate
    :type verify_ssl: bool
    :param retries: Default number of retries
    :type retries: int
    :param timeout: Request timeout
    :type timeout: Optional[float]
    :param follow_redirects: Follow redirects
    :type follow_redirects: bool
    """
    client_cls = AsyncClient
    response_cls = AsyncAPIResponse

    def __init__(
        self,
        client_id: Optional[str],
        client_secret: Optional[str],
        scopes: Optional[Set[str]],
        api_key: Optional[str],
        base_url: str,
        token_url: str,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        client: Union[Type[AsyncClient], AsyncClient] = AsyncClient,
        user_agent: str = USER_AGENT,
        auth: Optional[Union[RequestAuth, Sentinel]] = CLIENT_DEFAULT,
        *,
        _token_save_hook: Optional[AsyncTokenSaveHook] = None,
        _token_load_hook: Optional[AsyncTokenLoadHook] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            api_key=api_key,
            base_url=base_url,
            token_url=token_url,
            verify_ssl=verify_ssl,
            retries=retries,
            timeout=timeout,
            follow_redirects=follow_redirects,
            client=client,
            user_agent=user_agent,
            auth=auth,
            _token_save_hook=_token_save_hook,
            _token_load_hook=_token_load_hook,
            **kwargs,
        )

    async def close(self) -> None:
        """
        Close the Client.
        """
        await self._client.aclose()

    async def __aenter__(self) -> AsyncAPIClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

        if exc:
            raise exc

    async def request(
        self,
        method: str,
        endpoint: str,
        body: Optional[Any] = None,
        query: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        accept: Optional[List[tuple[str, float]]] = None,
        stream: bool = False,
        stream_type: StreamType = "bytes",
    ) -> AsyncAPIResponse:
        """
        Send an HTTP request.

        :param method: HTTP method
        :type method: str
        :param endpoint: API endpoint
        :type endpoint: str
        :param body: Request body
        :type body: Optional[Any]
        :param query: Query parameters
        :type query: Optional[Dict]
        :param headers: Request headers
        :type headers: Optional[Dict]
        :param params: Path parameters
        :type params: Optional[Dict]
        :param accept: Accept header
        :type accept: Optional[List[tuple[str, float]]]
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: AsyncAPIResponse object
        :rtype: AsyncAPIResponse
        """
        response: Response = await self._client.send(
            self.build_api_request(
                method=method,
                endpoint=endpoint,
                body=body,
                query=query,
                headers=headers,
                params=params,
                accept=accept,
            ),
            stream=stream,
        )

        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            if stream:
                await response.aread()

            raise_from_response(
                await self.response_cls.from_httpx_response(
                    response=e.response,
                    stream=False,
                )
            )

        return await self.response_cls.from_httpx_response(
            response=response,
            stream=stream,
            stream_type=stream_type,
        )
