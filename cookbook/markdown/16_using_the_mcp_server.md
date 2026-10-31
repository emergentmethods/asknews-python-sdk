# Using the AskNews MCP server

AskNews runs a hosted [Model Context Protocol](https://modelcontextprotocol.io)
server at `https://mcp.asknews.app`. It exposes AskNews search as tools that
any MCP client can hand to an LLM: Claude (claude.ai, Claude Desktop, Claude
Code), ChatGPT, Cursor, LangChain/LangGraph agents, or your own client.

## MCP or SDK?

| Use the MCP server when... | Use the SDK when... |
|---|---|
| An **LLM decides** which searches to run and with what parameters | **Your code decides** the parameters |
| You want AskNews inside an existing assistant (Claude, ChatGPT, Cursor) | You run deterministic pipelines, backfills, or pagination loops |
| You are building your own agent and want ready-made, LLM-tuned tool schemas | You need alerts, full DeepNews controls, analytics, or index counts |

AskNews's own DeepNews agent (`get_deep_news(engine="v2.0")`) is built on
this MCP server. Its tools are the same ones you get here. If you want a
managed research agent, call DeepNews ([12 Deep research basics](12_deep_research_basics.md)).
If you want your own model, loop, and prompt, build on the MCP tools
([17 Building agents on the MCP server](17_building_agents_on_mcp.md)).

## Connection facts

- **URL:** `https://mcp.asknews.app` (always `https`).
- **Transport:** Streamable HTTP. The server is **stateless**: every request
  is authenticated on its own and can be served by any replica. You do not
  need session IDs, sticky routing, or a long-lived connection, and it is
  safe to open a client per request.
- **Auth, option 1 (API key):** send `X-API-Key: <your key>`. Use this for
  code, Claude Code, Cursor, and server-side agents.
- **Auth, option 2 (OAuth):** clients that support MCP OAuth (claude.ai,
  ChatGPT connectors) log in through the browser. Nothing to configure
  beyond the URL.
- **Do not send an API key as `Authorization: Bearer`.** Bearer tokens are
  verified as OAuth tokens, so an API key there is rejected. API keys only
  work in the `X-API-Key` header.
- **Health check:** `GET https://mcp.asknews.app/healthz`. MCP `ping` is not
  a health check on this server.

## The tools

| Tool | What it does | Key arguments |
|---|---|---|
| `search_news` | News (and podcast) search with every filter | `query`, `entity_guarantee`, `string_guarantee`, `hours_back` or `start_datetime`/`end_datetime`, `domain_url`, `page_rank`, `languages`, `podcasts`, `return_type`, `offset` |
| `search_podcasts` | Podcast transcripts only | Same as `search_news` |
| `search_google` | Live web search, LLM-distilled | `google_keywords`, `lookback`, `strict`, `domains`, `engine` |
| `search_x_twitter` | X advanced search, LLM-distilled | `advanced_search_expression`, `lookback` |
| `search_wikipedia` | Wikipedia chunks | `query`, `n_documents`, `neighbor_chunks`, `include_main_section`, `diversify` |
| `do_news_research` | A DeepNews run, as one tool call | `query`, `model` (`"fast"` or `"rich"`), `sources` |
| `search_asknews_docs` | Searches the AskNews developer docs | `keywords` |

## The MCP tools are not the SDK methods

The tools wrap the same API, but the names and defaults differ. Agents and
code generators mix these up, so be explicit:

| | SDK `ask.news.search_news()` | MCP `search_news` tool |
|---|---|---|
| `time_filter` default | `"crawl_date"` | `"pub_date"` |
| `string_guarantee_op` default | `"OR"` | `"AND"` |
| Exact time window | `start_timestamp` / `end_timestamp` (unix seconds) | `start_datetime` / `end_datetime` (ISO 8601) |
| Archive access | `historical=True` | No flag. Archive is searched automatically. Windows over 160 days must be split into several calls. |
| `return_type` | `"string"`, `"dicts"`, `"both"` | `"string"`, `"dicts"` |

| SDK method | MCP tool | Argument difference |
|---|---|---|
| `ask.chat.live_web_search(queries=[...])` | `search_google` | one `google_keywords` string |
| `ask.chat.live_web_search(queries=[...], domains=["x.com"])` | `search_x_twitter` | one `advanced_search_expression` string |
| `ask.wiki.search_wiki()` | `search_wikipedia` | defaults: `n_documents=5`, `diversify=0.5` |
| `ask.news.search_news(podcasts="only")` | `search_podcasts` | to filter by show, `domain_url` takes the show name slugified plus `.podcast`, e.g. `the-mckinsey.podcast` |
| `ask.chat.get_deep_news()` | `do_news_research` | only `fast` / `rich` presets, no depth or filter control |

Everything else from recipes 01-11 still applies: guarantee the entity or
string that must appear, and use `query` to rank.

## Connecting an assistant

**claude.ai / ChatGPT:** add a custom connector with the URL
`https://mcp.asknews.app` and sign in with your AskNews account when
prompted.

**Claude Code:**

```bash
claude mcp add --transport http asknews https://mcp.asknews.app \
  --header "X-API-Key: $ASKNEWS_API_KEY"
```

**JSON-configured clients (e.g. Cursor's `mcp.json`):**

```json
{
  "mcpServers": {
    "asknews": {
      "url": "https://mcp.asknews.app",
      "headers": { "X-API-Key": "<your AskNews API key>" }
    }
  }
}
```

Tip for coding assistants: the server's `search_asknews_docs` tool lets
Claude Code or Cursor look up AskNews API docs while it writes your
integration.

## Calling tools directly from Python

You don't need an LLM to use the server. Calling tools directly is the
quickest way to see exactly what an agent will receive, and to debug tool
arguments.

```bash
pip install "fastmcp>=4"
```

```python
import asyncio
import os

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


ASKNEWS_MCP_URL = "https://mcp.asknews.app"


def asknews_mcp_client(timeout: float = 120) -> Client:
    transport = StreamableHttpTransport(
        ASKNEWS_MCP_URL,
        headers={"X-API-Key": os.environ["ASKNEWS_API_KEY"]},
    )
    return Client(transport, timeout=timeout)


async def list_tools() -> None:
    async with asknews_mcp_client() as client:
        for tool in await client.list_tools():
            print(tool.name, "-", (tool.description or "").strip().split("\n")[0])
            print("   args:", ", ".join(tool.input_schema.get("properties", {})))


async def call_tools() -> None:
    async with asknews_mcp_client() as client:
        # Same pattern as recipe 09: entity guarantee + descriptive query.
        news = await client.call_tool(
            "search_news",
            {
                "query": "Ramp corporate spend management funding valuation product launch",
                "entity_guarantee": ["Organization:Ramp"],
                "hours_back": 72,
                "n_articles": 5,
                "return_type": "string",
            },
        )
        print(news.content[0].text)

        # An exact window uses ISO 8601 datetimes, not unix timestamps.
        archive = await client.call_tool(
            "search_news",
            {
                "query": "ECB interest rate decision",
                "start_datetime": "2026-01-01T00:00:00Z",
                "end_datetime": "2026-03-31T23:59:59Z",
                "return_type": "dicts",
            },
        )
        for article in archive.structured_content["as_dicts"]:
            print(article["pub_date"], article["title"])

        posts = await client.call_tool(
            "search_x_twitter",
            {"advanced_search_expression": "(from:tryramp OR @tryramp) min_faves:20", "lookback": 24},
        )
        print(posts.content[0].text)

        web = await client.call_tool(
            "search_google",
            {"google_keywords": "Ramp funding round", "lookback": 72, "strict": True, "engine": "v1.5"},
        )
        print(web.content[0].text)


asyncio.run(list_tools())
asyncio.run(call_tools())
```

## `do_news_research`: DeepNews as a single tool

For an assistant that should hand off whole research questions:

- `model="fast"`: one quick search and a one-sentence answer (~30 seconds).
  Good when the keywords are known.
- `model="rich"`: iterative research with a stronger model. **Takes several
  minutes**, so raise the client timeout or it will be cut off.

Put the time frame and the keywords in `query` ("in the last 24 hours",
"check X and news"). The tool only takes presets. For control over depth,
sources, and filters, call DeepNews through the SDK instead.

```python
async def research() -> None:
    async with asknews_mcp_client(timeout=600) as client:
        result = await client.call_tool(
            "do_news_research",
            {
                "query": "In the last 48 hours, what has been reported about shipping disruptions "
                "in the Strait of Hormuz? Check news and X.",
                "model": "rich",
                "sources": ["asknews", "x"],
            },
        )
        print(result.structured_content["overview"])
        for source in result.structured_content["sources"]:
            print(source["id"], source["url"])


asyncio.run(research())
```
