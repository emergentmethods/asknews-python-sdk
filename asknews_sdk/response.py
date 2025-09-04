from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Generic, Iterator, TypeVar

from httpx import Request, Response

from asknews_sdk.types import (
    AsyncResponseBody,
    AsyncResponseBodyStream,
    ResponseBody,
    ResponseBodyStream,
    ServerSentEvent,
    StreamType,
)
from asknews_sdk.utils import deserialize, is_async_iterator, is_iterator, parse_content_type


TResponseBody = TypeVar("TResponseBody", ResponseBody, AsyncResponseBody)
TResponseBodyStream = TypeVar("TResponseBodyStream", ResponseBodyStream, AsyncResponseBodyStream)


class BaseAPIResponse(Generic[TResponseBody]):
    def __init__(
        self,
        request: Request,
        status_code: int,
        headers: Dict,
        body: TResponseBody,
        stream: bool = False,
    ) -> None:
        self.request = request
        self.status_code = status_code
        self.headers = headers
        self.body: TResponseBody = body
        self.stream = stream
        self.content_type, *_ = parse_content_type(
            headers.get("content-type", "application/json")
        )
        self.content: Any = self._deserialize_body() if not self.stream else self.body

    def _deserialize_body(self) -> Any:
        if self.content_type == "application/octet-stream":
            return self.body
        elif (
            self.content_type == "application/json"
            and self.body
            and isinstance(self.body, bytes)
        ):
            return deserialize(self.body)
        elif self.content_type == "text/plain" and isinstance(self.body, bytes):
            return self.body.decode("utf-8")
        else:
            return self.body


class APIResponse(BaseAPIResponse[ResponseBody]):
    """
    API Response object returned by the APIClient.
    """
    @classmethod
    def from_httpx_response(
        cls,
        response: Response,
        stream: bool = False,
        stream_type: StreamType = "bytes",
    ) -> APIResponse:
        """
        Create an APIResponse object from an HTTPX Response object.

        :param response: HTTPX Response object
        :type response: Response
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: APIResponse object
        :rtype: APIResponse
        """
        response_body: ResponseBody

        if stream:
            if stream_type == "bytes":
                response_body = response.iter_bytes()
            elif stream_type == "lines":
                response_body = response.iter_lines()
            elif stream_type == "raw":
                response_body = response.iter_raw()
            else:
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


class AsyncAPIResponse(BaseAPIResponse[AsyncResponseBody]):
    """
    Async API Response object returned by the AsyncAPIClient.
    """
    @classmethod
    async def from_httpx_response(
        cls,
        response: Response,
        stream: bool = False,
        stream_type: StreamType = "bytes",
    ) -> AsyncAPIResponse:
        """
        Create an AsyncAPIResponse object from an HTTPX Response object.

        :param response: HTTPX Response object
        :type response: Response
        :param stream: Stream response content
        :type stream: bool
        :param stream_type: Stream type
        :type stream_type: StreamType
        :return: AsyncAPIResponse object
        :rtype: AsyncAPIResponse
        """
        response_body: AsyncResponseBody

        if stream:
            if stream_type == "bytes":
                response_body = response.aiter_bytes()
            elif stream_type == "lines":
                response_body = response.aiter_lines()
            elif stream_type == "raw":
                response_body = response.aiter_raw()
            else:
                raise ValueError(f"Invalid stream type: {stream_type}")
        else:
            response_body = await response.aread()

        return cls(
            request=response.request,
            status_code=response.status_code,
            headers=dict(response.headers.items()),
            body=response_body,
            stream=stream,
        )


class BaseEventSource(Generic[TResponseBodyStream]):
    def __init__(
        self,
        iterator: TResponseBodyStream,
        encoding: str = "utf-8"
    ) -> None:
        self.iterator: TResponseBodyStream = iterator
        self.encoding = encoding
        self.current_event = ServerSentEvent()

    def parse_line(self, line: str) -> None:
        if line.startswith(":"):
            return

        key, _, value = line.partition(":")

        if value.startswith(" "):
            value = value[1:]

        key, value = key.strip(), value.strip()

        if key == "event":
            self.current_event.event = value
        elif key == "data":
            self.current_event.data.append(value)
        elif key == "id":
            self.current_event.id = value
        elif key == "retry":
            try:
                self.current_event.retry = int(value)
            except ValueError:
                pass


class EventSource(BaseEventSource[ResponseBodyStream]):
    """
    EventSource object for streaming Server-Sent Events.
    """
    def __iter__(self) -> Iterator[ServerSentEvent]:
        assert is_iterator(self.iterator), "Iterator must be an synchronous iterator"

        for line in self.iterator:
            if isinstance(line, bytes):
                decoded_line = line.decode(self.encoding)
            else:
                decoded_line = str(line)

            if decoded_line := decoded_line.strip():
                self.parse_line(decoded_line)
            elif self.current_event.data:
                yield self.current_event
                self.current_event = ServerSentEvent()

    @classmethod
    def from_api_response(cls, response: APIResponse) -> EventSource:
        """
        Create an EventSource object from an APIResponse object.

        :param response: APIResponse object
        :type response: APIResponse
        :return: EventSource object
        :rtype: EventSource
        """
        assert response.content_type == "text/event-stream", \
            (
                "Response content type must be text/event-stream, "
                f"got: {response.content_type}"
            )
        return cls(response.content)


class AsyncEventSource(BaseEventSource[AsyncResponseBodyStream]):
    """
    AsyncEventSource object for streaming Server-Sent Events.
    """
    async def __aiter__(self) -> AsyncIterator[ServerSentEvent]:
        assert is_async_iterator(self.iterator), "Iterator must be an asynchronous iterator"

        async for line in self.iterator:
            if isinstance(line, bytes):
                decoded_line = line.decode(self.encoding)
            else:
                decoded_line = str(line)

            if decoded_line := decoded_line.strip():
                self.parse_line(decoded_line)
            elif self.current_event.data:
                yield self.current_event
                self.current_event = ServerSentEvent()

    @classmethod
    def from_api_response(cls, response: AsyncAPIResponse) -> AsyncEventSource:
        """
        Create an AsyncEventSource object from an AsyncAPIResponse object.

        :param response: AsyncAPIResponse object
        :type response: AsyncAPIResponse
        :return: AsyncEventSource object
        :rtype: AsyncEventSource
        """
        assert response.content_type == "text/event-stream", \
            (
                "Response content type must be text/event-stream, "
                f"got: {response.content_type}"
            )
        return cls(response.content)

# class EventSource(Generic[TResponseBodyStream]):
#     """
#     EventSource object for streaming Server-Sent Events.
#     """
#     def __init__(
#         self,
#         iterator: TResponseBodyStream,
#         encoding: str = "utf-8"
#     ) -> None:
#         self.iterator: TResponseBodyStream = iterator
#         self.encoding = encoding
#         self.current_event = ServerSentEvent()

#     def __iter__(self) -> Iterator[ServerSentEvent]:
#         assert is_iterator(self.iterator), "Iterator must be an synchronous iterator"

#         for line in self.iterator:
#             if isinstance(line, bytes):
#                 line = line.decode(self.encoding)

#             if line := line.strip():
#                 self.parse_line(line)
#             elif self.current_event.data:
#                 yield self.current_event
#                 self.current_event = ServerSentEvent()

#     async def __aiter__(self) -> AsyncIterator[ServerSentEvent]:
#         assert is_async_iterator(self.iterator), "Iterator must be an asynchronous iterator"

#         async for line in self.iterator:
#             if isinstance(line, bytes):
#                 line = line.decode(self.encoding)

#             if line := line.strip():
#                 self.parse_line(line)
#             elif self.current_event.data:
#                 yield self.current_event
#                 self.current_event = ServerSentEvent()

#     def parse_line(self, line: str) -> None:
#         if line.startswith(":"):
#             return

#         key, _, value = line.partition(":")

#         if value.startswith(" "):
#             value = value[1:]

#         key, value = key.strip(), value.strip()

#         if key == "event":
#             self.current_event.event = value
#         elif key == "data":
#             self.current_event.data.append(value)
#         elif key == "id":
#             self.current_event.id = value
#         elif key == "retry":
#             try:
#                 self.current_event.retry = int(value)
#             except ValueError:
#                 pass

#     @classmethod
#     def from_api_response(cls, response: APIResponse) -> EventSource:
#         """
#         Create an EventSource object from an APIResponse object.

#         :param response: APIResponse object
#         :type response: APIResponse
#         :return: EventSource object
#         :rtype: EventSource
#         """
#         assert response.content_type == "text/event-stream", \
#             (
#                 "Response content type must be text/event-stream, "
#                 f"got: {response.content_type}"
#             )
#         return cls(response.content)
