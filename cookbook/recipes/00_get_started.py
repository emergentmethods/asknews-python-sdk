# %% [markdown]
# # Get started: setup and core concepts
#
# **Use this when** you are starting with the SDK, or choosing which AskNews
# endpoint fits your task. Every other recipe builds on the concepts here.
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
#
# An API key carries the scopes it was created with, so the client needs no
# `scopes` argument. `scopes` applies only to OAuth client credentials
# (`client_id` and `client_secret`).

# %%
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
)

# %% [markdown]
# An async client with the same methods is available as `AsyncAskNewsSDK`.
# Every method below is awaitable on it:
#
# ```python
# from asknews_sdk import AsyncAskNewsSDK
#
# async with AsyncAskNewsSDK(api_key=...) as ask:
#     response = await ask.news.search_news(query="...")
# ```
#
# ## Which endpoint do I want?
#
# | Need | Method | Recipes |
# |---|---|---|
# | Articles on a topic, current or historical, for your code or LLM to read | `ask.news.search_news()` | [01 Search live news](01_search_live_news.md), [02 Search historical news](02_search_historical_news.md), [03 Paginate news search results](03_paginate_news_search.md), [04 Build LLM context from news](04_build_llm_context.md), [09 Monitor a company](09_monitor_a_company.md), [10 Monitor a person](10_monitor_a_person.md), [11 Monitor a product, brand, or industry](11_monitor_a_product_brand_or_industry.md) |
# | Background / encyclopedic facts | `ask.wiki.search_wiki()` | [05 Search Wikipedia for background](05_search_wikipedia.md) |
# | Live X (Twitter) posts | `ask.chat.live_web_search(..., domains=["x.com"])` | [06 Search X (Twitter)](06_search_x_twitter.md) |
# | Live Google / web results, LLM-distilled | `ask.chat.live_web_search()` | [07 Search the live web (Google)](07_search_the_live_web.md) |
# | Podcast transcripts | `ask.news.search_news(..., podcasts="only")` | [08 Search podcasts](08_search_podcasts.md) |
# | A researched, cited answer to a question that takes more than one search | `ask.chat.get_deep_news()` | [12 Run deep research (DeepNews)](12_run_deep_research.md), [13 Set deep research depth](13_set_deep_research_depth.md), [14 Prompt deep research](14_prompt_deep_research.md) |
# | Research or a condition check on a schedule, delivered by email, webhook, or Google Docs | `ask.chat.create_alert()` | [15 Create an alert](15_create_an_alert.md) |
# | Give an LLM agent or assistant (Claude, ChatGPT, Cursor, LangChain) AskNews tools | The MCP server at `https://mcp.asknews.app` | [16 Connect to the AskNews MCP server](16_connect_to_the_mcp_server.md), [17 Build an agent on the MCP server](17_build_an_agent_on_mcp.md) |
#
# Rule of thumb: use `search_news` when you want the articles, and your code
# or model does the reading. Use DeepNews when you want the answer: it runs
# the searches, follows what it finds into context you did not know to ask
# for, and returns a synthesized response with citations.
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
# ## Time: `hours_back`, timestamps, and `strategy`
#
# - `hours_back` (default `24`) is the simplest window, relative to now.
# - `start_timestamp` / `end_timestamp` (unix seconds) give an exact window
#   and take precedence over `hours_back`. One request can span at most 160
#   days.
# - **One search covers every date.** Coverage goes back to 2023 and the
#   window alone sets what is searched. The `historical` parameter is
#   deprecated and has no effect, so leave it out. A window that starts within the last 48 hours costs 1 credit.
#   One that starts further back costs 5: a `start_timestamp` more than 48
#   hours ago, `hours_back` above 48, an `end_timestamp` on its own, or
#   `strategy="news knowledge"`. See
#   [02 Search historical news](02_search_historical_news.md).
# - For a past window, pass both timestamps. An `end_timestamp` without a
#   `start_timestamp` looks 160 days back from it.
# - `strategy="latest news"` searches the last 48 hours and
#   `strategy="news knowledge"` the last 150 days; both set `method="kw"`
#   and replace the window you pass.
# - `time_filter="crawl_date"` (default) filters on when AskNews ingested
#   the article. `time_filter="pub_date"` filters on the publisher's date.
#   Use `pub_date` when "it happened in the last 24 hours" matters, e.g. for
#   monitoring and reports. `crawl_date` is best for "anything new since I
#   last polled".
#
# ## `method`: `kw` vs `nl`
#
# - `method="kw"` (the default) leans on keyword matching. Best when the query is
#   a list of names, tickers, and terms.
# - `method="nl"` leans on semantic meaning. Best when the query is a
#   sentence or a paragraph, e.g. a forecasting question.
# - `method="both"` blends the two. It cannot be paginated.
#
# ## Result order
#
# Results are ranked by relevance. `sort_by="pub_date"` sorts the page a
# search returned by date: you still get the best matches, arranged newest
# first, not the newest matches. Shorten the window when recency matters.
#
# A search with no `query` returns a page of articles from the window that
# pass your filters, sorted by date within that page. It is not necessarily
# the newest articles in the window.
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
# ## Plan limits
#
# - `n_articles`: Pay as you go, Pro and Spelunker accept up to 10 per
#   request, the default; more returns a 400 error. Analyst and Enterprise
#   return up to 30, and a larger value is reduced to 30 without an error.
# - `domain_url` needs Analyst or Enterprise.
# - `return_graphs` and `return_geo` need Spelunker, Analyst, Enterprise, or
#   wallet access.
# - DeepNews: the `"x"` source needs Spelunker or above, and `"reddit"`
#   Analyst or above.
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
    try_cache="1h",
)

print(response.as_string)
for article in response.as_dicts:
    print(article.pub_date, article.source_id, article.title, article.article_url)
print("cache hit:", response.hit_cache)
