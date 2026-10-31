# Deep research (DeepNews) basics

`ask.chat.get_deep_news()` runs a research agent. It decides what to
search, reads the results, follows leads, searches again, and writes a
cited answer. Use it when you cannot write the right search parameters
up front: unknown entities, multi-hop questions, reconciling conflicting
sources, or reports that cover many things.

The pieces you control:

| Parameter | What it does |
|---|---|
| `messages` | The task. Chat format; the last user message is the request. |
| `sources` | Which tools the agent may use (see below). Default `["asknews"]`. |
| `model` | The LLM driving the agent. |
| `engine` | `"v2.0"` is the current engine; `"v1.5"` is the previous one (and the one alerts use). |
| `search_depth`, `max_depth` | How much research to do. See [13 Deep research depth](13_deep_research_depth.md). |
| `filter_params` | Defaults applied to the agent's AskNews searches (e.g. `hours_back`, `languages`). |
| `stream` | Stream the agent's thinking, tool calls, text, and sources as they happen. |
| `stream_sources_inline` | Engine `v2.0` streams only: also emit each tool call's sources as a batch right after the call, not just at the end. See below. |
| `inline_citations` | `"markdown_link"` (default), `"numbered"`, or `"none"`. |
| `return_sources` / `only_cited_sources` | Return the sources, optionally only those cited. |
| `cutoff_datetime` | Knowledge cutoff across all tools (for backtests). |

Sources:

| Source | Tool the agent gets |
|---|---|
| `"asknews"` | News search (the `search_news` filters, incl. entity/string guarantees) |
| `"google"` | Live web search |
| `"x"` | X (Twitter) advanced search |
| `"wiki"` | Wikipedia |
| `"podcasts"` | Podcast search |
| `"reddit"` | Reddit threads |
| `"graph"` | News knowledge graph |
| `"charts"` | Chart generation from news data |
| `"full_text_discovery"` | Full article text |

Best practices:

- Give the agent only the sources the task needs. Each extra source is an
  extra tool the agent may spend depth on.
- Stream while you develop. Watching the tool calls is the fastest way to
  see whether the agent is searching the way you intended, and to learn
  the tool names and parameters it uses (useful for prompting, see
  [14 Prompting deep research](14_prompting_deep_research.md)).
- Start with small depth and raise it only when the answer is missing
  things.

```python
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["chat", "news"],
)
```

## Non-streaming

```python
response = ask.chat.get_deep_news(
    messages=[{"role": "user", "content": "What has Emirates said about fuel costs?"}],
    sources=["asknews", "wiki"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=1,
    max_depth=3,
    stream=False,
    return_sources=True,
)

print(response.choices[0].message.content)

for article in response.sources.news:
    print("news:", article.title, article.article_url)
for page in response.sources.web:
    print("web:", page.title, page.url)

print(
    f"prompt tokens: {response.usage.prompt_tokens}, "
    f"completion tokens: {response.usage.completion_tokens}, "
    f"tool usage: {response.usage.tool_usage}"
)
```

## Streaming (engine v2.0)

With `engine="v2.0"` the stream yields two kinds of messages:

- `CreateDeepNewsResponseStreamChunkV2`: Anthropic-style events. Content
  blocks are `thinking`, `tool_use` (the agent's tool calls, with their
  input JSON), and `text` (the answer).
- `CreateDeepNewsResponseStreamSource`: a source the agent retrieved
  (news, web, graph, or chart), sent as it arrives.

The last chunk carries the final `usage`.

```python
from asknews_sdk.dto.deepnews import (
    AnthropicInputJsonDelta,
    AnthropicTextDelta,
    AnthropicThinkingBlock,
    AnthropicThinkingDelta,
    AnthropicToolUseBlock,
    ContentBlockDeltaEvent,
    ContentBlockStartEvent,
    ContentBlockStopEvent,
    CreateDeepNewsResponseStreamChunkV2,
    CreateDeepNewsResponseStreamSource,
    CreateDeepNewsResponseStreamSourcesChartSource,
    CreateDeepNewsResponseStreamSourcesNewsSource,
    CreateDeepNewsResponseStreamSourcesWebSource,
)


stream = ask.chat.get_deep_news(
    messages=[{"role": "user", "content": "What are analysts saying about AI chip export controls?"}],
    sources=["asknews", "google", "x"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=2,
    max_depth=5,
    stream=True,
    return_sources=True,
)

answer = []
sources = {"news": [], "web": [], "charts": []}
block_types = {}
last_chunk = None

for message in stream:
    if isinstance(message, CreateDeepNewsResponseStreamChunkV2):
        last_chunk = message
        event = message.choices[0].delta

        if isinstance(event, ContentBlockStartEvent):
            block_types[event.index] = type(event.content_block)
            if isinstance(event.content_block, AnthropicThinkingBlock):
                print("\n<thinking>", end="", flush=True)
            elif isinstance(event.content_block, AnthropicToolUseBlock):
                print(f"\n<tool_use name={event.content_block.name!r}>", end="", flush=True)

        elif isinstance(event, ContentBlockDeltaEvent):
            delta = event.delta
            if isinstance(delta, AnthropicTextDelta):
                answer.append(delta.text)
                print(delta.text, end="", flush=True)
            elif isinstance(delta, AnthropicThinkingDelta):
                print(delta.thinking, end="", flush=True)
            elif isinstance(delta, AnthropicInputJsonDelta):
                print(delta.partial_json, end="", flush=True)  # tool call arguments

        elif isinstance(event, ContentBlockStopEvent):
            block_type = block_types.pop(event.index, None)
            if block_type is AnthropicThinkingBlock:
                print("</thinking>")
            elif block_type is AnthropicToolUseBlock:
                print("</tool_use>")

    elif isinstance(message, CreateDeepNewsResponseStreamSource):
        source = message.source
        if isinstance(source, CreateDeepNewsResponseStreamSourcesNewsSource):
            sources["news"].append(source.data)
        elif isinstance(source, CreateDeepNewsResponseStreamSourcesWebSource):
            sources["web"].append(source.data)
        elif isinstance(source, CreateDeepNewsResponseStreamSourcesChartSource):
            sources["charts"].append(source.data)  # a Plotly figure spec

final_answer = "".join(answer)
if last_chunk is not None:
    print("\nusage:", last_chunk.usage)
```

## Streaming sources per tool call (`stream_sources_inline`)

By default the stream sends every retrieved source as
`CreateDeepNewsResponseStreamSource` messages at the end, after the
answer. For a progressive UI (a source panel that fills while the agent
is still researching) or for resolving citations as they arrive, set
`stream_sources_inline=True`. The agent then also emits one
`CreateDeepNewsResponseStreamSourceBatch` message per research tool call,
after that turn's tool calls finish and before the next agent output.

Requirements: `stream=True` and `engine="v2.0"`. With other engines, or
without streaming, the flag has no effect.

What a batch carries:

| Field | Meaning |
|---|---|
| `turn_index`, `call_index`, `calls_in_turn` | Which agent turn and which call in that turn (for ordering parallel calls). |
| `tool_call_id`, `tool_name` | The tool call it belongs to; `tool_call_id` matches the `id` of the `tool_use` content block. |
| `kind` | The tool's kind: `news`, `web`, `wiki`, `x`, `reddit`, `podcast`, `graph`, `chart`, `full_text`, or `other`. |
| `status` | `ok`, `empty`, `error`, `timed_out`, or `skipped`. |
| `source_ids` | Every source the call returned, by id. Ids are opaque and unique within one stream. |
| `sources` | Only the sources not sent in an earlier batch, each with its own `kind` (`news`, `web`, `graph`, or `chart`), `source_id`, typed `source`, and optional `citation_number`. |

Two things to get right:

- Dedupe by `source_id`. When a later call re-finds a source, its id is
  listed in `source_ids` but it is not re-sent in `sources`. Keep a dict
  keyed by `source_id` and resolve `source_ids` against it.
- Switch on the entry's `kind`, not the batch's. A `search_wikipedia` call
  streams `kind="wiki"` at the batch level with `web` entries inside.

The final `CreateDeepNewsResponseStreamSource` messages are still emitted
at the end, unchanged, so code that only reads those keeps working.

```python
from asknews_sdk.dto.deepnews import (
    CreateDeepNewsResponseStreamSourceBatch,
    CreateDeepNewsResponseStreamSourceBatchChartEntry,
    CreateDeepNewsResponseStreamSourceBatchGraphEntry,
    CreateDeepNewsResponseStreamSourceBatchNewsEntry,
    CreateDeepNewsResponseStreamSourceBatchWebEntry,
)


stream = ask.chat.get_deep_news(
    messages=[{"role": "user", "content": "What are analysts saying about AI chip export controls?"}],
    sources=["asknews", "google", "wiki"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=2,
    max_depth=5,
    stream=True,
    stream_sources_inline=True,
    inline_citations="numbered",
    return_sources=True,
)

answer = []
seen = {}  # source_id -> entry; a source is sent in full only once per stream
calls = []  # (turn_index, call_index, tool_name, status, source_ids)

for message in stream:
    if isinstance(message, CreateDeepNewsResponseStreamChunkV2):
        event = message.choices[0].delta
        if isinstance(event, ContentBlockDeltaEvent) and isinstance(event.delta, AnthropicTextDelta):
            answer.append(event.delta.text)
            print(event.delta.text, end="", flush=True)

    elif isinstance(message, CreateDeepNewsResponseStreamSourceBatch):
        calls.append((message.turn_index, message.call_index, message.tool_name, message.status, message.source_ids))
        for entry in message.sources:
            if entry.source_id in seen:
                continue
            seen[entry.source_id] = entry
            tag = f"[{entry.citation_number}] " if entry.citation_number is not None else ""
            if isinstance(entry, CreateDeepNewsResponseStreamSourceBatchNewsEntry):
                print(f"\n  + {tag}news: {entry.source.title} {entry.source.article_url}")
            elif isinstance(entry, CreateDeepNewsResponseStreamSourceBatchWebEntry):
                print(f"\n  + {tag}web: {entry.source.title} {entry.source.url}")
            elif isinstance(entry, CreateDeepNewsResponseStreamSourceBatchGraphEntry):
                print(f"\n  + {tag}graph: {entry.source}")  # a URL
            elif isinstance(entry, CreateDeepNewsResponseStreamSourceBatchChartEntry):
                print(f"\n  + {tag}chart: {entry.source.query}")  # .chart_json holds the Plotly figure
        print(
            f"\n  <{message.tool_name} turn={message.turn_index} call={message.call_index + 1}/"
            f"{message.calls_in_turn} status={message.status} "
            f"sources={len(message.source_ids)} new={len(message.sources)}>"
        )

    elif isinstance(message, CreateDeepNewsResponseStreamSource):
        pass  # the final per-source messages still arrive; `seen` already has them

# Which sources each call returned, resolved against what was streamed earlier.
for turn_index, call_index, tool_name, status, source_ids in calls:
    titles = [getattr(seen[sid].source, "title", seen[sid].kind) for sid in source_ids if sid in seen]
    print(f"turn {turn_index} call {call_index} {tool_name} ({status}): {titles}")

# `citation_number` lines up with the numbered citations in the answer.
by_citation = {e.citation_number: e for e in seen.values() if e.citation_number is not None}
print(sorted(by_citation))
```

The async client takes the same flag:

```python
import asyncio
from asknews_sdk import AsyncAskNewsSDK
from asknews_sdk.dto.deepnews import CreateDeepNewsResponseStreamSourceBatch

async def main():
    async with AsyncAskNewsSDK(api_key=..., scopes=["chat"]) as ask:
        stream = await ask.chat.get_deep_news(
            messages=[{"role": "user", "content": "What are analysts saying about AI chip export controls?"}],
            sources=["asknews", "google"],
            engine="v2.0",
            search_depth=2,
            max_depth=5,
            stream=True,
            stream_sources_inline=True,
        )
        seen = {}
        async for message in stream:
            if isinstance(message, CreateDeepNewsResponseStreamSourceBatch):
                for entry in message.sources:
                    seen.setdefault(entry.source_id, entry)
                print(message.tool_name, message.status, len(seen), "sources so far")

asyncio.run(main())
```

## Constraining the agent's news searches

`filter_params` sets defaults for every AskNews search the agent makes.
Use it to enforce things the agent should not decide on its own, such as
recency, languages, or source quality.

```python
response = ask.chat.get_deep_news(
    messages=[{"role": "user", "content": "Summarize today's most important AI policy developments."}],
    sources=["asknews", "x", "google"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=3,
    max_depth=6,
    filter_params={
        "hours_back": 24,
        "time_filter": "pub_date",
        "languages": ["en"],
        "page_rank": 100000,
        "n_articles": 5,
    },
    stream=False,
)
```

## Async

`AsyncAskNewsSDK` has the same method. Use it to run several research
tasks concurrently.

```python
import asyncio
from asknews_sdk import AsyncAskNewsSDK

async def main():
    async with AsyncAskNewsSDK(api_key=..., scopes=["chat"]) as ask:
        questions = ["...", "...", "..."]
        results = await asyncio.gather(*[
            ask.chat.get_deep_news(
                messages=[{"role": "user", "content": q}],
                sources=["asknews", "google"],
                engine="v2.0",
                search_depth=2,
                max_depth=4,
            )
            for q in questions
        ])

asyncio.run(main())
```
