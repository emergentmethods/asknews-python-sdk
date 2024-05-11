from __future__ import annotations

import asyncio
import threading
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from asgiref.typing import ASGIApplication
from authlib.integrations.httpx_client import AsyncOAuth2Client, OAuth2Client
from httpx import AsyncClient, Client, HTTPStatusError

from asknews_sdk.errors import raise_from_json
from asknews_sdk.security import (
    AsyncTokenLoadHook,
    AsyncTokenSaveHook,
    InjectToken,
    OAuthToken,
    TokenLoadHook,
    TokenSaveHook,
)
from asknews_sdk.utils import (
    build_accept_header,
    build_url,
    deserialize,
    determine_content_type,
    serialize,
)
from asknews_sdk.version import __version__

USER_AGENT = f"asknews-sdk-python/{__version__}"


class StreamType(str, Enum):
    bytes = "bytes"
    lines = "lines"
    raw = "raw"


class APIRequest:
    """
    API Request object used by the APIClient.
    """

    def __init__(
        self,
        base_url: str,
        method: str,
        endpoint: str,
        body: Optional[Any] = None,
        query: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        accept: Optional[List[tuple[str, float]]] = None,
    ) -> None:
        self.base_url = base_url
        self.method = method
        self.endpoint = endpoint
        self.query = query
        self.params = params
        self.accept = accept
        self.url = build_url(
            base_url=self.base_url,
            endpoint=self.endpoint,
            query=self.query,
            params=self.params,
        )
        self.headers = headers or {}
        self.content_type = self.headers.pop(
            "Content-Type", determine_content_type(body)
        )
        self.body = serialize(body) if body and not isinstance(body, bytes) else None
        self.accept = accept or [
            (
                self.content_type
                if "json" in self.content_type
                else "application/json",
                1.0,
            )
        ]
        self.headers["Content-Type"] = self.content_type
        self.headers["Accept"] = build_accept_header(self.accept)


class APIResponse:
    """
    API Response object returned by the APIClient.
    """

    def __init__(
        self,
        request: APIRequest,
        status_code: int,
        headers: Dict,
        body: bytes,
        stream: bool = False,
    ) -> None:
        self.request = request
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.stream = stream
        self.content_type = headers.get("Content-Type", "application/json")
        self.content = self.deserialize_body() if not self.stream else self.body

    def deserialize_body(self) -> Any:
        if self.content_type == "application/octet-stream":
            return self.body
        elif self.content_type == "application/json":
            return deserialize(self.body)
        elif self.content_type == "text/plain":
            return self.body.decode("utf-8")
        else:
            return self.body


class BaseAPIClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: Optional[Set[str]],
        base_url: str,
        token_url: str,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        *,
        _mock_server: Optional[Union[ASGIApplication, Callable[..., Any]]] = None,
        _token_save_hook: Optional[Union[TokenSaveHook, AsyncTokenSaveHook]] = None,
        _token_load_hook: Optional[Union[TokenLoadHook, AsyncTokenLoadHook]] = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = {"offline", "openid", *(scopes or set())}
        self.base_url = base_url
        self.token_url = token_url
        self.verify_ssl = verify_ssl
        self.retries = retries
        self.timeout = timeout
        self.follow_redirects = follow_redirects

        self._mock_server = _mock_server
        self._token_save_hook = _token_save_hook
        self._token_load_hook = _token_load_hook

        self._token = OAuthToken()

    def _get_oauth_client(
        self, client: Union[OAuth2Client, AsyncOAuth2Client]
    ) -> Union[OAuth2Client, AsyncOAuth2Client]:
        return client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=" ".join(self.scopes) if self.scopes else None,
            token_endpoint_auth_method="client_secret_basic",
            token_type="Bearer",
        )

    def _get_http_client(
        self, client: Union[Client, AsyncClient]
    ) -> Union[Client, AsyncClient]:
        return client(
            base_url=self.base_url,
            verify=self.verify_ssl,
            timeout=self.timeout,
            auth=InjectToken(self._token),
            follow_redirects=self.follow_redirects,
            headers={"User-Agent": USER_AGENT},
        )

    def _reset_token(self) -> None:
        """
        Reset the current token.
        """
        self._token.reset_token()


class APIClient(BaseAPIClient):
    """
    Sync HTTP API Client

    :param client_id: Client ID
    :type client_id: str
    :param client_secret: Client secret
    :type client_secret: str
    :param scopes: OAuth scopes
    :type scopes: Set[str]
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

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: Optional[Set[str]],
        base_url: str,
        token_url: str,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        *,
        _mock_server: Optional[Callable[..., Any]] = None,
        _token_save_hook: Optional[TokenSaveHook] = None,
        _token_load_hook: Optional[TokenLoadHook] = None,
    ) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            base_url=base_url,
            token_url=token_url,
            verify_ssl=verify_ssl,
            retries=retries,
            timeout=timeout,
            follow_redirects=follow_redirects,
            _mock_server=_mock_server,
            _token_save_hook=_token_save_hook,
            _token_load_hook=_token_load_hook,
        )

        self._oauth_client = self._get_oauth_client(OAuth2Client)
        self._client = self._get_http_client(Client)
        self._token_lock = threading.Lock()

    def close(self) -> None:
        """
        Close the Client.
        """
        self._client.close()

    def __enter__(self) -> APIClient:
        if self._token_load_hook:
            self._token.set_token(self._token_load_hook())

        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

        if exc:
            raise exc

    def _get_token(self) -> None:
        self._token.set_token(
            self._oauth_client.fetch_token(
                self.token_url,
                grant_type="client_credentials",
            )
        )

        if self._token_save_hook:
            self._token_save_hook(self._token.token_info)

    def _ensure_valid_token(self, force: bool = False) -> None:
        """
        Ensure a valid access token is available.

        :param force: Force the token to be refreshed
        :type force: bool
        """
        with self._token_lock:
            if force:
                self._reset_token()

            if self._token.is_expired:
                self._get_token()

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
        stream_type: StreamType = StreamType.bytes,
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
        # TODO: Add logic for getting a new token if
        # a 401 is returned from the API up to one time
        self._ensure_valid_token()

        request = APIRequest(
            base_url=self.base_url,
            method=method,
            endpoint=endpoint,
            body=body,
            query=query,
            headers=headers,
            params=params,
            accept=accept,
        )

        response = self._client.request(
            method=request.method,
            url=request.url,
            content=request.body,
            headers=request.headers,
        )
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            raise_from_json(e.response.json())

        if stream:
            if stream_type == StreamType.bytes:
                response_body = response.aiter_bytes()
            elif stream_type == StreamType.lines:
                response_body = response.aiter_lines()
            elif stream_type == StreamType.raw:
                response_body = response.aiter_raw()
        else:
            response_body = response.content

        return APIResponse(
            request=request,
            status_code=response.status_code,
            headers=dict(response.headers.items()),
            body=response_body,
            stream=stream,
        )


class AsyncAPIClient(BaseAPIClient):
    """
    Base Async HTTP API Client

    :param client_id: Client ID
    :type client_id: str
    :param client_secret: Client secret
    :type client_secret: str
    :param scopes: OAuth scopes
    :type scopes: Set[str]
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

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: Optional[Set[str]],
        base_url: str,
        token_url: str,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        *,
        _mock_server: Optional[ASGIApplication] = None,
        _token_save_hook: Optional[AsyncTokenSaveHook] = None,
        _token_load_hook: Optional[AsyncTokenLoadHook] = None,
    ) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            base_url=base_url,
            token_url=token_url,
            verify_ssl=verify_ssl,
            retries=retries,
            timeout=timeout,
            follow_redirects=follow_redirects,
            _mock_server=_mock_server,
            _token_save_hook=_token_save_hook,
            _token_load_hook=_token_load_hook,
        )

        self._oauth_client = self._get_oauth_client(AsyncOAuth2Client)
        self._client = self._get_http_client(AsyncClient)
        self._token_lock = asyncio.Lock()

    async def close(self) -> None:
        """
        Close the Client.
        """
        await self._client.aclose()

    async def __aenter__(self) -> AsyncAPIClient:
        if self._token_load_hook:
            self._token.set_token(await self._token_load_hook())

        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

        if exc:
            raise exc

    async def _get_token(self) -> None:
        self._token.set_token(
            await self._oauth_client.fetch_token(
                self.token_url,
                grant_type="client_credentials",
            )
        )

        if self._token_save_hook:
            await self._token_save_hook(self._token.token_info)

    async def _ensure_valid_token(self, force: bool = False) -> None:
        """
        Ensure a valid access token is available.

        :param force: Force the token to be refreshed
        :type force: bool
        """
        async with self._token_lock:
            if force:
                self._reset_token()

            if self._token.is_expired:
                await self._get_token()

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
        stream_type: StreamType = StreamType.bytes,
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
        # TODO: Add logic for getting a new token if
        # a 401 is returned from the API up to one time
        await self._ensure_valid_token()

        request = APIRequest(
            base_url=self.base_url,
            method=method,
            endpoint=endpoint,
            body=body,
            query=query,
            headers=headers,
            params=params,
            accept=accept,
        )

        response = await self._client.request(
            method=request.method,
            url=request.url,
            content=request.body,
            headers=request.headers,
        )
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            raise_from_json(e.response.json())

        if stream:
            if stream_type == StreamType.bytes:
                response_body = response.aiter_bytes()
            elif stream_type == StreamType.lines:
                response_body = response.aiter_lines()
            elif stream_type == StreamType.raw:
                response_body = response.aiter_raw()
        else:
            response_body = response.content

        return APIResponse(
            request=request,
            status_code=response.status_code,
            headers=dict(response.headers.items()),
            body=response_body,
            stream=stream,
        )
