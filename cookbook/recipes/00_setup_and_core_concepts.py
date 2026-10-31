# %% [markdown]
# # Setup and core concepts
#
# Read this first. Every other recipe assumes the concepts here.
#
# ## Install
#
# ```bash
# pip install asknews
# ```
#
# Create an API key at https://my.asknews.app and export it:
#
# ```bash
# export ASKNEWS_API_KEY="..."
# ```

# %%
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["news", "chat", "stories", "analytics"],
)

# %% [markdown]
# An async client with the same methods is available as `AsyncAskNewsSDK`.
# Every method below is awaitable on it:
#
# ```python
# from asknews_sdk import AsyncAskNewsSDK
#
# async with AsyncAskNewsSDK(api_key=..., scopes=[...]) as ask:
#     response = await ask.news.search_news(query="...")
# ```
#
# ## Which endpoint do I want?
#
# | Need | Method |
# |---|---|
# | Fast, precise lookup when you already know the keywords or entities | `ask.news.search_news()` |
# | Background / encyclopedic facts | `ask.wiki.search_wiki()` |
# | Live X (Twitter) posts | `ask.chat.live_web_search(..., domains=["x.com"])` |
# | Live Google / web results, LLM-distilled | `ask.chat.live_web_search()` |
# | Podcast transcripts | `ask.news.search_news(..., podcasts="only")` |
# | Iterative, multi-step research across all of the above | `ask.chat.get_deep_news()` |
# | Scheduled monitoring that emails / webhooks a report | `ask.chat.create_alert()` |
# | Give an LLM agent or assistant (Claude, ChatGPT, Cursor, LangChain) AskNews tools | The MCP server at `https://mcp.asknews.app`, see [16](16_using_the_mcp_server.md) |
#
# Rule of thumb: if you can write the search parameters yourself, use
# `search_news`. If you need an agent to *discover* what to search for next
# (follow leads, identify unknown entities, reconcile sources), use DeepNews.
#
# ## The `search_news` mental model
#
# A `search_news` call is a **filter** followed by a **ranking**:
#
# 1. **Hard filters** decide which articles are eligible. Time window,
#    `entity_guarantee`, `string_guarantee`, `domain_url`, `categories`,
#    `languages`, `countries`, `page_rank`, `sentiment`, and so on.
# 2. **`query`** ranks the eligible articles by relevance. It does not
#    exclude anything by itself (beyond `similarity_score_threshold`).
#
# Most bad results come from putting everything into `query` and no hard
# filters. When you know the company, person, or keyword that *must* appear,
# guarantee it, then use `query` to describe what you care about.
#
# ## Time: `hours_back`, `historical`, and timestamps
#
# - `hours_back` (default `24`) is the simplest window, relative to now.
# - `start_timestamp` / `end_timestamp` (unix seconds) give an exact window.
# - `historical=False` (default) searches the **live index: the most recent
#   ~48 hours**. Anything older needs `historical=True`. See
#   [02 Searching archive news](02_searching_archive_news.md).
# - `time_filter="crawl_date"` (default) filters on when AskNews ingested
#   the article. `time_filter="pub_date"` filters on the publisher's date.
#   Use `pub_date` when "it happened in the last 24 hours" matters, e.g. for
#   monitoring and reports. `crawl_date` is best for "anything new since I
#   last polled".
#
# ## `method`: `kw` vs `nl`
#
# - `method="kw"` (default) leans on keyword matching. Best when the query is
#   a list of names, tickers, and terms.
# - `method="nl"` leans on semantic meaning. Best when the query is a
#   sentence or a paragraph, e.g. a forecasting question.
# - `method="both"` blends the two.
#
# ## `return_type`: feeding an LLM vs feeding code
#
# - `"string"` (default): `response.as_string`, a prompt-optimized block of
#   `<doc>...</doc>` entries you can paste straight into an LLM prompt.
# - `"dicts"`: `response.as_dicts`, a list of typed article objects
#   (`title`, `article_url`, `pub_date`, `summary`, `key_points`,
#   `entities`, `source_id`, `page_rank`, `sentiment`, ...).
# - `"both"`: both of the above.
#
# ## `premium=True`
#
# Includes premium publisher content in the results. The examples in this
# cookbook set it wherever source quality matters.
#
# ## Caching repeated queries
#
# `try_cache="1h" | "6h" | "12h" | "24h" | "3d" | "7d"` reuses a cached
# response for an identical query, which is much cheaper. Useful for
# backtests and parameter sweeps. `response.hit_cache` tells you whether it
# hit.

# %%
response = ask.news.search_news(
    query="NVIDIA earnings guidance data center revenue",
    entity_guarantee=["Organization:NVIDIA"],
    hours_back=24,
    n_articles=5,
    return_type="both",
    premium=True,
    try_cache="1h",
)

print(response.as_string)
for article in response.as_dicts:
    print(article.pub_date, article.source_id, article.title, article.article_url)
print("cache hit:", response.hit_cache)
