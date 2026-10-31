"""`stream_sources_inline` and the `chat.completion.source.batch` stream chunk.

The streams are the gateway's recorded engine-v2.0 fixtures (see
`tests/fixtures/research_canvas/README.md`), replayed through respx as SSE.
"""

import json
from inspect import isasyncgen, isgenerator
from pathlib import Path
from typing import AsyncIterator, Iterator, List

import pytest
from pydantic import TypeAdapter, ValidationError
from respx import MockRouter

from asknews_sdk.api.chat import AsyncChatAPI, ChatAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.base import Article
from asknews_sdk.dto.deepnews import (
    CreateDeepNewsRequest,
    CreateDeepNewsResponseStream,
    CreateDeepNewsResponseStreamChunkV2,
    CreateDeepNewsResponseStreamSource,
    CreateDeepNewsResponseStreamSourceBatch,
    CreateDeepNewsResponseStreamSourceBatchNewsEntry,
    CreateDeepNewsResponseStreamSourceBatchWebEntry,
    CreateDeepNewsResponseStreamV2,
)


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "research_canvas"
MESSAGES = [{"role": "user", "content": "query"}]


def _chunks(fixture: str) -> List[dict]:
    with (FIXTURES / fixture).open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _sse(fixture: str) -> Iterator[bytes]:
    for chunk in _chunks(fixture):
        yield ("data: " + json.dumps(chunk) + "\n\n").encode()
    yield b"data: [DONE]\n\n"


async def _async_sse(fixture: str) -> AsyncIterator[bytes]:
    for event in _sse(fixture):
        yield event


def _batches(fixture: str) -> List[dict]:
    return [c for c in _chunks(fixture) if c["object"] == "chat.completion.source.batch"]


@pytest.fixture
def sync_chat_api(sync_api_client: APIClient):
    return ChatAPI(sync_api_client)


@pytest.fixture
def async_chat_api(async_api_client: AsyncAPIClient):
    return AsyncChatAPI(async_api_client)


# --- request ------------------------------------------------------------------


def test_request_dto_defaults_stream_sources_inline_off():
    assert CreateDeepNewsRequest(messages=MESSAGES).stream_sources_inline is False
    payload = CreateDeepNewsRequest(messages=MESSAGES, stream_sources_inline=True).model_dump(
        mode="json"
    )
    assert payload["stream_sources_inline"] is True


def test_sync_get_deep_news_sends_stream_sources_inline(
    sync_chat_api: ChatAPI, response_mock: MockRouter
):
    route = response_mock.post("/v1/chat/deepnews").respond(
        stream=_sse("serial_v2_stream.jsonl"),
        headers={"content-type": CreateDeepNewsResponseStreamChunkV2.__content_type__},
    )

    list(
        sync_chat_api.get_deep_news(
            messages=MESSAGES, stream=True, engine="v2.0", stream_sources_inline=True
        )
    )

    payload = json.loads(route.calls.last.request.content)
    assert payload["stream_sources_inline"] is True
    assert payload["engine"] == "v2.0"


def test_sync_get_deep_news_defaults_stream_sources_inline_off(
    sync_chat_api: ChatAPI, response_mock: MockRouter
):
    route = response_mock.post("/v1/chat/deepnews").respond(
        stream=_sse("serial_v2_stream.jsonl"),
        headers={"content-type": CreateDeepNewsResponseStreamChunkV2.__content_type__},
    )

    list(sync_chat_api.get_deep_news(messages=MESSAGES, stream=True, engine="v2.0"))

    assert json.loads(route.calls.last.request.content)["stream_sources_inline"] is False


# --- stream parsing -----------------------------------------------------------


@pytest.mark.parametrize("fixture", ["serial_v2_stream.jsonl", "mixed_kind_wiki_v2_stream.jsonl"])
def test_sync_v2_stream_yields_typed_source_batches(
    sync_chat_api: ChatAPI, response_mock: MockRouter, fixture: str
):
    response_mock.post("/v1/chat/deepnews").respond(
        stream=_sse(fixture),
        headers={"content-type": CreateDeepNewsResponseStreamChunkV2.__content_type__},
    )

    stream = sync_chat_api.get_deep_news(
        messages=MESSAGES, stream=True, engine="v2.0", stream_sources_inline=True
    )
    assert isgenerator(stream)
    tokens = list(stream)

    assert len(tokens) == len(_chunks(fixture))
    batches = [t for t in tokens if isinstance(t, CreateDeepNewsResponseStreamSourceBatch)]
    assert [b.model_dump(mode="json") for b in batches] == [
        CreateDeepNewsResponseStreamSourceBatch.model_validate(b).model_dump(mode="json")
        for b in _batches(fixture)
    ]
    assert len(batches) == len(_batches(fixture))
    # The other chunk shapes still parse as before.
    assert any(isinstance(t, CreateDeepNewsResponseStreamChunkV2) for t in tokens)
    assert any(isinstance(t, CreateDeepNewsResponseStreamSource) for t in tokens)


@pytest.mark.parametrize("fixture", ["serial_v2_stream.jsonl", "mixed_kind_wiki_v2_stream.jsonl"])
async def test_async_v2_stream_yields_typed_source_batches(
    async_chat_api: AsyncChatAPI, response_mock: MockRouter, fixture: str
):
    response_mock.post("/v1/chat/deepnews").respond(
        stream=_async_sse(fixture),
        headers={"content-type": CreateDeepNewsResponseStreamChunkV2.__content_type__},
    )

    stream = await async_chat_api.get_deep_news(
        messages=MESSAGES, stream=True, engine="v2.0", stream_sources_inline=True
    )
    assert isasyncgen(stream)
    tokens = [token async for token in stream]

    assert len(tokens) == len(_chunks(fixture))
    batches = [t for t in tokens if isinstance(t, CreateDeepNewsResponseStreamSourceBatch)]
    assert len(batches) == len(_batches(fixture))
    assert [b.tool_call_id for b in batches] == [b["tool_call_id"] for b in _batches(fixture)]


def test_recorded_serial_batches_are_typed_and_refound_source_is_not_resent():
    first, second = (
        CreateDeepNewsResponseStreamSourceBatch.model_validate(b)
        for b in _batches("serial_v2_stream.jsonl")
    )

    assert first.object == "chat.completion.source.batch"
    assert (first.turn_index, first.call_index, first.calls_in_turn) == (0, 0, 1)
    assert (first.tool_call_id, first.tool_name, first.kind, first.status) == (
        "call-0",
        "search_news",
        "news",
        "ok",
    )
    assert first.source_ids == ["news:1", "news:2"]
    assert [type(e) for e in first.sources] == [
        CreateDeepNewsResponseStreamSourceBatchNewsEntry
    ] * 2
    assert [(e.kind, e.source_id, e.citation_number) for e in first.sources] == [
        ("news", "news:1", 1),
        ("news", "news:2", 2),
    ]
    assert str(first.sources[0].source.article_url) == "https://example.test/a1"
    assert first.sources[0].source.as_string_key == "[1]"

    # `news:2` is re-found by the second call: announced in source_ids, not re-sent.
    assert second.source_ids == ["news:3", "news:2"]
    assert [e.source_id for e in second.sources] == ["news:3"]
    assert second.sources[0].source.wikidata_entities["Person"][0].qid == "Q7259"


def test_recorded_mixed_batches_discriminate_entries_by_kind():
    batches = [
        CreateDeepNewsResponseStreamSourceBatch.model_validate(b)
        for b in _batches("mixed_kind_wiki_v2_stream.jsonl")
    ]

    assert [b.kind for b in batches] == ["web", "news", "wiki", "wiki"]
    web, news, wiki, _ = batches
    assert isinstance(web.sources[0], CreateDeepNewsResponseStreamSourceBatchWebEntry)
    assert isinstance(news.sources[0], CreateDeepNewsResponseStreamSourceBatchNewsEntry)
    # Same URL, two sources, two ids.
    assert str(web.sources[0].source.url) == str(news.sources[0].source.article_url)
    assert (web.sources[0].source_id, news.sources[0].source_id) == ("web:1", "news:2")
    # Wikipedia calls stream `web` entries under a `wiki` tool kind.
    assert all(isinstance(e, CreateDeepNewsResponseStreamSourceBatchWebEntry) for e in wiki.sources)


def test_batch_entry_rejects_unknown_kind():
    chunk = dict(_batches("serial_v2_stream.jsonl")[0])
    chunk["sources"] = [{**chunk["sources"][0], "kind": "podcast"}]

    with pytest.raises(ValidationError):
        CreateDeepNewsResponseStreamSourceBatch.model_validate(chunk)


def test_batch_chunk_round_trips_to_the_recorded_wire_shape():
    for recorded in _batches("mixed_kind_wiki_v2_stream.jsonl"):
        chunk = CreateDeepNewsResponseStreamSourceBatch.model_validate(recorded)
        dumped = chunk.model_dump(mode="json")
        assert dumped["source_ids"] == recorded["source_ids"]
        assert [e["source_id"] for e in dumped["sources"]] == [
            e["source_id"] for e in recorded["sources"]
        ]
        assert [e["kind"] for e in dumped["sources"]] == [e["kind"] for e in recorded["sources"]]


@pytest.mark.parametrize("union", [CreateDeepNewsResponseStream, CreateDeepNewsResponseStreamV2])
def test_both_stream_unions_accept_the_batch_discriminator(union):
    adapter = TypeAdapter(union)
    for recorded in _batches("serial_v2_stream.jsonl"):
        assert isinstance(
            adapter.validate_python(recorded), CreateDeepNewsResponseStreamSourceBatch
        )


# --- Article nullability ------------------------------------------------------


def test_article_cluster_metrics_are_optional_and_nullable():
    source = _batches("serial_v2_stream.jsonl")[0]["sources"][0]["source"]
    assert "centroid_distance" not in source and "cluster_probability" not in source

    article = Article.model_validate(source)
    assert article.centroid_distance is None and article.cluster_probability is None

    explicit = Article.model_validate(
        {**source, "centroid_distance": None, "cluster_probability": 0.5}
    )
    assert explicit.centroid_distance is None and explicit.cluster_probability == 0.5
