import pytest
from httpx import AsyncByteStream, Request, Response, SyncByteStream

from asknews_sdk.response import APIResponse, EventSource


def test_api_response():
    response = Response(
        request=Request("GET", "https://example.com"),
        status_code=200,
        headers={"content-type": "application/json"},
        content=b'{"key": "value"}',
    )
    api_response = APIResponse.from_httpx_response(response)

    assert api_response.status_code == 200
    assert api_response.content == {"key": "value"}
    assert api_response.content_type == "application/json"
    assert api_response.stream is False

    response = Response(
        request=Request("GET", "https://example.com"),
        status_code=200,
        headers={"content-type": "text/plain"},
        content=b"Hello, World!",
    )
    api_response = APIResponse.from_httpx_response(response)

    assert api_response.status_code == 200
    assert api_response.content == "Hello, World!"
    assert api_response.content_type == "text/plain"
    assert api_response.stream is False

    class ResponseStream(SyncByteStream):
        def __iter__(self):
            yield b"Hello"
            yield b","
            yield b" "
            yield b"World"
            yield b"!"

    response = Response(
        request=Request("GET", "https://example.com"),
        status_code=200,
        headers={"content-type": "application/octet-stream"},
        stream=ResponseStream(),
    )
    api_response = APIResponse.from_httpx_response(response, stream=True)

    assert api_response.status_code == 200
    assert "".join(v.decode() for v in list(api_response.content)) == "Hello, World!"
    assert api_response.content_type == "application/octet-stream"
    assert api_response.stream is True


def test_event_source():
    def sse_events():
        yield b": This is a comment\n"
        yield b"data: Hello, World!\n"
        yield b"data: Goodbye, World!\n"
        yield b"\n"
        yield b"event: custom\n"
        yield b"id: 123\n"
        yield b"retry: 1\n"
        yield b"data: Hello, World!\n"
        yield b"data: Goodbye, World!\n"
        yield b"\n"
        yield b"event: last\n"
        yield b"data: Hello, World!\n"
        yield b"retry: incorrect\n"
        yield b"\n"


    event_source = EventSource(sse_events())
    events = list(event_source)

    assert len(events) == 3
    assert events[0].data == ["Hello, World!", "Goodbye, World!"]
    assert events[0].event == "message"
    assert events[0].id == ""
    assert events[0].retry == 0
    assert events[1].data == ["Hello, World!", "Goodbye, World!"]
    assert events[1].event == "custom"
    assert events[1].id == "123"
    assert events[1].retry == 1
    assert events[2].data == ["Hello, World!"]
    assert events[2].event == "last"
    assert events[2].id == ""
    assert events[2].retry == 0

    class SSEResponseStream(SyncByteStream):
        def __iter__(self):
            yield b"data: Hello, World!\n"
            yield b"data: Goodbye, World!\n"
            yield b"\n"
            yield b"event: custom\n"
            yield b"data: Hello, World!\n"
            yield b"data: Goodbye, World!\n"
            yield b"custom: Means nothing\n"
            yield b"\n"

    response = Response(
        request=Request("GET", "https://example.com"),
        status_code=200,
        headers={"content-type": "text/event-stream"},
        stream=SSEResponseStream(),
    )
    api_response = APIResponse.from_httpx_response(response, stream=True, stream_type="lines")

    event_source = EventSource.from_api_response(api_response)
    events = list(event_source)

    assert len(events) == 2
    assert events[0].data == ["Hello, World!", "Goodbye, World!"]
    assert events[0].event == "message"
    assert events[0].id == ""
    assert events[0].retry == 0
    assert events[1].data == ["Hello, World!", "Goodbye, World!"]
    assert events[1].event == "custom"
    assert events[1].id == ""
    assert events[1].retry == 0

    response = Response(
        request=Request("GET", "https://example.com"),
        status_code=200,
        headers={"content-type": "application/json"},
        stream=SSEResponseStream(),
    )
    api_response = APIResponse.from_httpx_response(response, stream=True, stream_type="lines")

    with pytest.raises(AssertionError):
        EventSource.from_api_response(api_response)


async def test_event_source_async():
    async def sse_events():
        yield b": This is a comment\n"
        yield b"data: Hello, World!\n"
        yield b"data: Goodbye, World!\n"
        yield b"\n"
        yield b"event: custom\n"
        yield b"id: 123\n"
        yield b"retry: 1\n"
        yield b"data: Hello, World!\n"
        yield b"data: Goodbye, World!\n"
        yield b"\n"
        yield b"event: last\n"
        yield b"data: Hello, World!\n"
        yield b"retry: incorrect\n"
        yield b"\n"

    event_source = EventSource(sse_events())
    events = [event async for event in event_source]

    assert len(events) == 3
    assert events[0].data == ["Hello, World!", "Goodbye, World!"]
    assert events[0].event == "message"
    assert events[0].id == ""
    assert events[0].retry == 0
    assert events[1].data == ["Hello, World!", "Goodbye, World!"]
    assert events[1].event == "custom"
    assert events[1].id == "123"
    assert events[1].retry == 1
    assert events[2].data == ["Hello, World!"]
    assert events[2].event == "last"
    assert events[2].id == ""
    assert events[2].retry == 0

    class SSEResponseStream(AsyncByteStream):
        async def __aiter__(self):
            yield b"data: Hello, World!\n"
            yield b"data: Goodbye, World!\n"
            yield b"\n"
            yield b"event: custom\n"
            yield b"data: Hello, World!\n"
            yield b"data: Goodbye, World!\n"
            yield b"custom: Means nothing\n"
            yield b"\n"

    response = Response(
        request=Request("GET", "https://example.com"),
        status_code=200,
        headers={"content-type": "text/event-stream"},
        stream=SSEResponseStream(),
    )
    api_response = APIResponse.from_httpx_response(
        response, stream=True, stream_type="lines", sync=False
    )

    event_source = EventSource.from_api_response(api_response)
    events = [event async for event in event_source]

    assert len(events) == 2
    assert events[0].data == ["Hello, World!", "Goodbye, World!"]
    assert events[0].event == "message"
    assert events[0].id == ""
    assert events[0].retry == 0
    assert events[1].data == ["Hello, World!", "Goodbye, World!"]
    assert events[1].event == "custom"
    assert events[1].id == ""
    assert events[1].retry == 0
