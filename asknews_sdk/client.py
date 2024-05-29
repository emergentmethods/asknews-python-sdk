from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Type,
    Union,
)

from httpx import AsyncClient, Client, HTTPStatusError, Request, Response

from asknews_sdk.errors import raise_from_json
from asknews_sdk.security import (
    AsyncTokenLoadHook,
    AsyncTokenSaveHook,
    OAuth2ClientCredentials,
    TokenLoadHook,
    TokenSaveHook,
)
from asknews_sdk.types import RequestAuth, StreamType
from asknews_sdk.utils import (
    build_accept_header,
    build_url,
    deserialize,
    determine_content_type,
    serialize,
)
from asknews_sdk.version import __version__


CLIENT_DEFAULT = object()

USER_AGENT = f"asknews-sdk-python/{__version__}"


class APIResponse:
    """
    API Response object returned by the APIClient.
    """
    def __init__(
        self,
        request: Request,
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
        self.content_type = headers.get("content-type", "application/json")
        self.content = self._deserialize_body() if not self.stream else self.body

    def _deserialize_body(self) -> Any:
        if self.content_type == "application/octet-stream":
            return self.body
        elif self.content_type == "application/json":
            return deserialize(self.body)
        elif self.content_type == "text/plain":
            return self.body.decode("utf-8")
        else:
            return self.body

    @classmethod
    def from_httpx_response(
        cls,
        response: Response,
        stream: bool = False,
        stream_type: StreamType = "bytes",
        sync: bool = True,
    ) -> APIResponse:
        """
        Create an APIResponse object from an HTTPX Response object.

        :param response: HTTPX Response object
        :type response: Response
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :param sync: Synchronous or asynchronous
        :type sync: bool
        :return: APIResponse object
        :rtype: APIResponse
        """
        if stream:
            match stream_type:
                case "bytes":
                    response_body = response.iter_bytes() if sync else response.aiter_bytes()
                case "lines":
                    response_body = response.iter_lines() if sync else response.aiter_lines()
                case "raw":
                    response_body = response.iter_raw() if sync else response.aiter_raw()
                case _:
                    raise ValueError(f"Invalid stream type: {stream_type}")
        else:
            response_body = response.content

        return cls(
            request=response.request,
            status_code=response.status_code,
            headers=dict(response.headers.items()),
            body=response_body,
            stream=stream,
        )

class BaseAPIClient:
    def __init__(
        self,
        client_id: Optional[str],
        client_secret: Optional[str],
        scopes: Optional[Set[str]],
        base_url: str,
        token_url: str,
        verify_ssl: bool,
        retries: int,
        timeout: Optional[float],
        follow_redirects: bool,
        client: Union[
            Union[Type[Client], Client],
            Union[Type[AsyncClient], AsyncClient],
        ],
        user_agent: str,
        auth: Optional[RequestAuth],
        *,
        _token_save_hook: Optional[Union[TokenSaveHook, AsyncTokenSaveHook]] = None,
        _token_load_hook: Optional[Union[TokenLoadHook, AsyncTokenLoadHook]] = None,
        **kwargs,
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
        self._client_auth = None

        if auth:
            if auth is CLIENT_DEFAULT:
                self._client_auth = OAuth2ClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    token_url=self.token_url,
                    scopes=self.scopes,
                    _token_load_hook=_token_load_hook,
                    _token_save_hook=_token_save_hook,
                )
            else:
                self._client_auth = auth

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
        client_id: Optional[str],
        client_secret: Optional[str],
        scopes: Optional[Set[str]],
        base_url: str,
        token_url: str,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        client: Union[Type[Client], Client] = Client,
        user_agent: str = USER_AGENT,
        auth: Optional[RequestAuth] = CLIENT_DEFAULT,
        *,
        _token_save_hook: Optional[TokenSaveHook] = None,
        _token_load_hook: Optional[TokenLoadHook] = None,
        **kwargs,
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
        response = self._client.send(
            self.build_api_request(
                method=method,
                endpoint=endpoint,
                body=body,
                query=query,
                headers=headers,
                params=params,
                accept=accept,
            )
        )
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            raise_from_json(e.response.json())

        return APIResponse.from_httpx_response(
            response=response,
            stream=stream,
            stream_type=stream_type,
            sync=True,
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
        client_id: Optional[str],
        client_secret: Optional[str],
        scopes: Optional[Set[str]],
        base_url: str,
        token_url: str,
        verify_ssl: bool = True,
        retries: int = 3,
        timeout: Optional[float] = None,
        follow_redirects: bool = True,
        client: Union[Type[AsyncClient], AsyncClient] = AsyncClient,
        user_agent: str = USER_AGENT,
        auth: Optional[RequestAuth] = CLIENT_DEFAULT,
        *,
        _token_save_hook: Optional[AsyncTokenSaveHook] = None,
        _token_load_hook: Optional[AsyncTokenLoadHook] = None,
        **kwargs,
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
        response = await self._client.send(
            self.build_api_request(
                method=method,
                endpoint=endpoint,
                body=body,
                query=query,
                headers=headers,
                params=params,
                accept=accept,
            )
        )

        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            raise_from_json(e.response.json())

        return APIResponse.from_httpx_response(
            response=response,
            stream=stream,
            stream_type=stream_type,
            sync=False,
        )
