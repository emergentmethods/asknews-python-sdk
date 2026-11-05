# Setup and core concepts

Read this first. Every other recipe assumes the concepts here.

## Install

```bash
pip install asknews
```

Create an API key at https://my.asknews.app and export it:

```bash
export ASKNEWS_API_KEY="..."
```

An API key carries the scopes it was created with, so the client needs no
`scopes` argument. `scopes` applies only to OAuth client credentials
(`client_id` and `client_secret`).

```python
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
)
```

An async client with the same methods is available as `AsyncAskNewsSDK`.
Every method below is awaitable on it:

```python
from asknews_sdk import AsyncAskNewsSDK

async with AsyncAskNewsSDK(api_key=...) as ask:
    response = await ask.news.search_news(query="...")
```

## Which endpoint do I want?

| Need | Method |
|---|---|
| Fast, precise lookup when you already know the keywords or entities | `ask.news.search_news()` |
| Background / encyclopedic facts | `ask.wiki.search_wiki()` |
| Live X (Twitter) posts | `ask.chat.live_web_search(..., domains=["x.com"])` |
| Live Google / web results, LLM-distilled | `ask.chat.live_web_search()` |
| Podcast transcripts | `ask.news.search_news(..., podcasts="only")` |
| Iterative, multi-step research across all of the above | `ask.chat.get_deep_news()` |
| Scheduled monitoring that emails / webhooks a report | `ask.chat.create_alert()` |
| Give an LLM agent or assistant (Claude, ChatGPT, Cursor, LangChain) AskNews tools | The MCP server at `https://mcp.asknews.app`, see [16](16_using_the_mcp_server.md) |

Rule of thumb: if you can write the search parameters yourself, use
`search_news`. If you need an agent to *discover* what to search for next
(follow leads, identify unknown entities, reconcile sources), use DeepNews.

## The `search_news` mental model

A `search_news` call is a **filter** followed by a **ranking**:

1. **Hard filters** decide which articles are eligible. Time window,
   `entity_guarantee`, `string_guarantee`, `domain_url`, `categories`,
   `languages`, `countries`, `page_rank`, `sentiment`, and so on.
2. **`query`** ranks the eligible articles by relevance. It does not
   exclude anything by itself (beyond `similarity_score_threshold`).

Most bad results come from putting everything into `query` and no hard
filters. When you know the company, person, or keyword that *must* appear,
guarantee it, then use `query` to describe what you care about.

## Time: `hours_back`, timestamps, and `strategy`

- `hours_back` (default `24`) is the simplest window, relative to now.
- `start_timestamp` / `end_timestamp` (unix seconds) give an exact window
  and take precedence over `hours_back`. One request can span at most 160
  days.
- **One search covers every date.** Coverage goes back to 2023 and the
  window alone sets what is searched. The `historical` parameter is
  deprecated and has no effect, so leave it out. A window that starts within the last 48 hours costs 1 credit.
  One that starts further back costs 5: a `start_timestamp` more than 48
  hours ago, `hours_back` above 48, an `end_timestamp` on its own, or
  `strategy="news knowledge"`. See
  [02 Searching archive news](02_searching_archive_news.md).
- For a past window, pass both timestamps. An `end_timestamp` without a
  `start_timestamp` looks 160 days back from it.
- `strategy="latest news"` searches the last 48 hours and
  `strategy="news knowledge"` the last 150 days; both set `method="kw"`
  and replace the window you pass.
- `time_filter="crawl_date"` (default) filters on when AskNews ingested
  the article. `time_filter="pub_date"` filters on the publisher's date.
  Use `pub_date` when "it happened in the last 24 hours" matters, e.g. for
  monitoring and reports. `crawl_date` is best for "anything new since I
  last polled".

## `method`: `kw` vs `nl`

- `method="kw"` (the default) leans on keyword matching. Best when the query is
  a list of names, tickers, and terms.
- `method="nl"` leans on semantic meaning. Best when the query is a
  sentence or a paragraph, e.g. a forecasting question.
- `method="both"` blends the two. It cannot be paginated.

## Result order

Results are ranked by relevance. `sort_by="pub_date"` sorts the page a
search returned by date: you still get the best matches, arranged newest
first, not the newest matches. Shorten the window when recency matters.

A search with no `query` returns a page of articles from the window that
pass your filters, sorted by date within that page. It is not necessarily
the newest articles in the window.

## `return_type`: feeding an LLM vs feeding code

- `"string"` (default): `response.as_string`, a prompt-optimized block of
  `<doc>...</doc>` entries you can paste straight into an LLM prompt.
- `"dicts"`: `response.as_dicts`, a list of typed article objects
  (`title`, `article_url`, `pub_date`, `summary`, `key_points`,
  `entities`, `source_id`, `page_rank`, `sentiment`, ...).
- `"both"`: both of the above.

## Plan limits

- `n_articles`: Pay as you go, Pro and Spelunker accept up to 10 per
  request, the default; more returns a 400 error. Analyst and Enterprise
  return up to 30, and a larger value is reduced to 30 without an error.
- `domain_url` needs Analyst or Enterprise.
- `return_graphs` and `return_geo` need Spelunker, Analyst, Enterprise, or
  wallet access.
- DeepNews: the `"x"` source needs Spelunker or above, and `"reddit"`
  Analyst or above.

## Caching repeated queries

`try_cache="1h" | "6h" | "12h" | "24h" | "3d" | "7d"` reuses a cached
response for an identical query, which is much cheaper. Useful for
backtests and parameter sweeps. `response.hit_cache` tells you whether it
hit.

```python
response = ask.news.search_news(
    query="NVIDIA earnings guidance data center revenue",
    entity_guarantee=["Organization:NVIDIA"],
    hours_back=24,
    n_articles=5,
    return_type="both",
    try_cache="1h",
)

print(response.as_string)
for article in response.as_dicts:
    print(article.pub_date, article.source_id, article.title, article.article_url)
print("cache hit:", response.hit_cache)
```
