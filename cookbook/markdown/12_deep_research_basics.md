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
| `engine` | `"v2.0"` is the current engine that streams Anthropic-style tool use events (preferred); `"v1.5"` streams XML tags for tool use events. |
| `search_depth`, `max_depth` | How much research to do. See [13 Deep research depth](13_deep_research_depth.md). |
| `filter_params` | Defaults applied to the agent's AskNews searches (e.g. `hours_back`, `languages`). |
| `stream` | Stream the agent's thinking, tool calls, text, and sources as they happen. |
| `inline_citations` | `"markdown_link"` (default), `"numbered"`, or `"none"`. |
| `return_sources` / `only_cited_sources` | Return the sources, optionally only those cited. |
| `cutoff_datetime` | Knowledge cutoff across all tools (for backtests). |
| `stream_sources_inline` | Whether to stream source objects as tools are used (default `False`). Else, stream all source objects at the end of the response.|

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
