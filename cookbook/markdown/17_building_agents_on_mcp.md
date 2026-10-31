# Building agents on the MCP server

This recipe builds a research agent on the AskNews MCP tools with LangChain.
The practices come from AskNews's own DeepNews agent, which runs on these
same tools in production. They apply to any framework or model.

## Best practices

1. **Load only the tools the task needs.** Every extra tool is a schema
   in the prompt and one more wrong choice the model can make. DeepNews
   maps the requested `sources` to tool names and drops the rest.
2. **Enforce hard constraints in code, not in the prompt.** If results
   must come from a time window, a set of languages, or before a backtest
   cutoff, rewrite the tool arguments before the call goes out. Models
   widen windows when they find nothing, and they write `since:` into X
   queries. DeepNews overrides the model's arguments for every news, web,
   and X call. A prompt instruction is a request. An interceptor is a
   guarantee.
3. **Retry rate limits in the client.** A rate-limited tool call comes back
   as a tool error with a "retry after N s" hint. Retry it with backoff
   instead of letting the model see the error and give up or improvise.
4. **Tell the model the current date** (or the backtest cutoff) in the
   user message. Otherwise "latest" means "latest in my training data".
5. **Teach the filters in the system prompt.** The biggest quality jump
   comes from the model refining searches with `entity_guarantee` and
   `string_guarantee` rather than rephrasing `query`. Keep names in
   `query` *and* guarantee them, and relax filters when a search returns
   nothing.
6. **State the search budget**: a minimum number of searches before
   answering and a maximum. Back the maximum with a hard limit on agent
   steps (`recursion_limit` in LangGraph).
7. **Fail fast if the MCP server is unreachable.** An agent with no tools
   answers from memory and sounds confident. Raise instead.
8. **Mix in your own tools.** MCP tools are ordinary tools once loaded.
   Add your database, CRM, or portfolio lookup next to them.
9. **Set timeouts to match the tools.** Searches return in seconds;
   `do_news_research` with `model="rich"` takes minutes.

```bash
pip install langchain langchain-anthropic langchain-mcp-adapters
```

`langchain-mcp-adapters` is the adapter AskNews tests the server against.

```python
import asyncio
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient


ASKNEWS_MCP_URL = "https://mcp.asknews.app"
```

## 1. Pick tools by source

The same source names DeepNews uses, mapped to MCP tool names.

```python
TOOLS_BY_SOURCE = {
    "asknews": "search_news",
    "podcasts": "search_podcasts",
    "google": "search_google",
    "x": "search_x_twitter",
    "wiki": "search_wikipedia",
}


def select_tools(tools: list, sources: list[str]) -> list:
    wanted = {TOOLS_BY_SOURCE[s] for s in sources}
    return [t for t in tools if t.name in wanted]
```

## 2. Enforce constraints with an interceptor

`langchain-mcp-adapters` runs interceptors around every tool call.
`request.override(args=...)` replaces the model's arguments before the
call is sent. This one enforces a time window (also the way to apply a
backtest cutoff), languages, and source quality, using each tool's own
argument names:

- `search_news` / `search_podcasts`: `start_datetime` / `end_datetime`
  (ISO 8601). `hours_back` is dropped so it cannot conflict.
- `search_google`: the same datetimes, `strict=True` so undated pages are
  dropped, and `engine="v1.5"` (the engine that supports datetimes).
- `search_x_twitter`: the same datetimes, and any `since:` / `until:` the
  model wrote into the expression is removed.

```python
@dataclass
class SearchConstraints:
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    languages: Optional[list[str]] = None
    page_rank: Optional[int] = None

    @classmethod
    def last_hours(cls, hours: int, as_of: Optional[datetime] = None, **kwargs):
        end = as_of or datetime.now(timezone.utc)
        return cls(start=end - timedelta(hours=hours), end=end, **kwargs)


class EnforceConstraints:
    def __init__(self, constraints: SearchConstraints):
        self.c = constraints

    def rewrite(self, name: str, args: dict) -> dict:
        args = dict(args)
        c = self.c
        window = {}
        if c.start:
            window["start_datetime"] = c.start.isoformat()
        if c.end:
            window["end_datetime"] = c.end.isoformat()

        if name in ("search_news", "search_podcasts"):
            if window:
                args.pop("hours_back", None)
                args.update(window)
            if c.languages:
                args["languages"] = c.languages
            if c.page_rank:
                args["page_rank"] = c.page_rank

        elif name == "search_google":
            args["strict"] = True
            if window:
                args.pop("lookback", None)
                args.update(window)
                args["engine"] = "v1.5"

        elif name == "search_x_twitter" and window:
            args.pop("lookback", None)
            args.update(window)
            expression = args.get("advanced_search_expression") or ""
            args["advanced_search_expression"] = re.sub(
                r"\b(since|until)(_time)?:\S+", "", expression
            ).strip()

        return args

    async def __call__(self, request, handler):
        return await handler(request.override(args=self.rewrite(request.name, request.args)))
```

## 3. Retry rate limits with an interceptor

```python
RETRY_AFTER = re.compile(r"retry.after\s+(\d+(?:\.\d+)?)\s*s", re.IGNORECASE)


class RetryOnRateLimit:
    def __init__(self, max_retries: int = 5, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.max_delay = max_delay

    async def __call__(self, request, handler):
        for attempt in range(self.max_retries + 1):
            result = await handler(request)
            if not getattr(result, "isError", False):
                return result
            text = " ".join(getattr(c, "text", "") for c in result.content)
            match = RETRY_AFTER.search(text)
            if not match or attempt == self.max_retries:
                return result
            await asyncio.sleep(min(float(match.group(1)) * 2**attempt, self.max_delay))
        return result
```

## 4. A system prompt that teaches the tools

Adapted from the DeepNews researcher prompt. The tool schemas already
describe each argument. The prompt adds *strategy*: how to refine, what
budget to spend, and how to cite.

```python
def research_system_prompt(sources: list[str], min_searches: int, max_searches: int) -> str:
    news_guidance = ""
    if "asknews" in sources or "podcasts" in sources:
        news_guidance = """
## Using news search filters

Refine follow-up searches with filters (entity_guarantee, string_guarantee, domain_url,
start_datetime/end_datetime, languages, reporting_voice, offset for the next page), not only by
rephrasing the query. If a filtered search returns little or nothing, relax or drop filters.

`query` is a fuzzy semantic lookup and names help it. `entity_guarantee` and `string_guarantee`
are hard constraints. When results must cover specific companies, people or places, keep the
names in `query` and also guarantee them, e.g.
query="Emirates Qatar Airways Lufthansa profit warning jet fuel",
entity_guarantee=["Organization:Emirates", "Organization:Qatar Airways", "Organization:Lufthansa"],
entity_guarantee_op="OR".

Results list entities like `Organization: Gazprom | Equinor`. To filter on one, pass it as
`Type:Value`, e.g. "Organization:Gazprom".
"""

    return f"""You are a research agent. Answer the user's question by searching iteratively.
Available sources: {", ".join(sources)}.

## Research process
1. Start with a broad search on the user's question.
2. Read the results. Identify gaps, conflicting claims, and leads worth following.
3. Run targeted follow-up searches to fill gaps, find more authoritative or more recent sources,
   and check multiple perspectives.
4. Run at least {min_searches} searches before answering, and no more than {max_searches}.
5. Then stop calling tools and write the answer.
{news_guidance}
## Answer
- Answer the question directly, with context.
- Cite every claim with a markdown link to its source URL.
- Present conflicting reports as conflicting, and say what remains unconfirmed.
"""
```

## 5. Optional: your own tools next to the MCP tools

```python
PORTFOLIO = {
    "Ramp": "Series E, owned since 2023, board seat",
    "Databricks": "Secondary position, no board seat",
}


@tool
def lookup_portfolio_position(company: str) -> str:
    """Look up our internal position in a portfolio company."""
    return PORTFOLIO.get(company, "Not a portfolio company")
```

## 6. Put it together

```python
async def build_research_agent(
    sources: list[str],
    constraints: SearchConstraints,
    min_searches: int = 3,
    max_searches: int = 8,
    extra_tools: Optional[list] = None,
):
    client = MultiServerMCPClient(
        {
            "asknews": {
                "transport": "streamable_http",
                "url": ASKNEWS_MCP_URL,
                "headers": {"X-API-Key": os.environ["ASKNEWS_API_KEY"]},
                "timeout": timedelta(seconds=60),
            }
        },
        tool_interceptors=[RetryOnRateLimit(), EnforceConstraints(constraints)],
    )

    try:
        mcp_tools = await client.get_tools()
    except Exception as e:
        raise RuntimeError(f"AskNews MCP server unavailable at {ASKNEWS_MCP_URL}") from e

    tools = select_tools(mcp_tools, sources) + (extra_tools or [])
    if not tools:
        raise RuntimeError(f"No AskNews tools available for sources {sources}")

    agent = create_agent(
        ChatAnthropic(model="claude-sonnet-5-5", max_tokens=8000),
        tools,
        system_prompt=research_system_prompt(sources, min_searches, max_searches),
    )
    # Each search costs ~2 graph steps (model call + tool call). Cap the run.
    run_config = {"recursion_limit": 2 * max_searches + 6}
    return agent, run_config


async def ask(question: str, as_of: Optional[datetime] = None) -> str:
    now = as_of or datetime.now(timezone.utc)
    agent, run_config = await build_research_agent(
        sources=["asknews", "x", "google"],
        constraints=SearchConstraints.last_hours(72, as_of=now, languages=["en"], page_rank=100000),
        extra_tools=[lookup_portfolio_position],
    )
    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"{question}\n\nThe current date and time is {now:%B %d %Y, %H:%M} UTC.",
                }
            ]
        },
        config=run_config,
    )

    # See what the agent actually searched for: the fastest way to debug quality.
    for message in result["messages"]:
        for call in getattr(message, "tool_calls", None) or []:
            print("tool call:", call["name"], call["args"])

    return result["messages"][-1].content


if __name__ == "__main__":
    print(asyncio.run(ask("What happened with our portfolio company Ramp this week, and does it affect our position?")))

    # Backtest: the same agent, with every search capped at a past date.
    cutoff = datetime(2026, 4, 15, 14, 0, tzinfo=timezone.utc)
    print(asyncio.run(ask("Will the ECB cut rates at its next meeting?", as_of=cutoff)))
```
