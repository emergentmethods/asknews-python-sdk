# AskNews SDK Cookbook

Runnable, best-practice examples for the AskNews Python SDK.

## Layout

```
cookbook/
├── recipes/    # source of truth: runnable .py files in "percent" cell format
├── markdown/   # generated from recipes/ by build.py, do not edit by hand
└── build.py    # recipes/*.py -> markdown/*.md + markdown/index.md
```

Each recipe mixes prose (`# %% [markdown]` cells) and code (`# %%` cells).
You can run a recipe as a script, step through it cell by cell in VS Code or
PyCharm, or convert it to a notebook with `jupytext --to ipynb`.

## Recipes

| # | Recipe | Use this when | Calls | Covers |
|---|---|---|---|---|
| 00 | [Get started: setup and core concepts](markdown/00_get_started.md) | You are starting with the SDK, or choosing which AskNews endpoint fits your task. Every other recipe builds on the concepts here. | `AskNewsSDK`, `AsyncAskNewsSDK` | Client, which endpoint to use, filter-then-rank model, time windows, `kw` vs `nl`, result order, return types, caching, plan limits |
| 01 | [Search live news](markdown/01_search_live_news.md) | Your application or agent needs what is being reported now: current context for an LLM, the latest on a topic, or new coverage as it arrives. | `news.search_news` | The last 48 hours, `pub_date` vs `crawl_date`, sorting by date, polling |
| 02 | [Search historical news](markdown/02_search_historical_news.md) | The question is about a defined period in the past: how an event developed, what was reported at a given moment, or dated context for forecasting research and backtests. Coverage goes back to 2023. | `news.search_news` | Searching back to 2023 by window, exact windows, point-in-time context for backtests |
| 03 | [Paginate news search results](markdown/03_paginate_news_search.md) | One page of results is not enough: you need every match for a query, or a bulk pull over a long period. | `news.search_news` with `offset` | `offset` loops, caps, dedupe, windowed bulk pulls |
| 04 | [Build LLM context from news](markdown/04_build_llm_context.md) | You retrieve news for your own LLM and want context it can reason over and cite. | `news.search_news` | `as_string` vs custom context from `as_dicts`, citations, graphs, geo |
| 05 | [Search Wikipedia for background](markdown/05_search_wikipedia.md) | Your model needs the background behind the news: who a person is, what a company or institution does, or the history behind an event. | `wiki.search_wiki` | `search_wiki` parameters, background + news in one prompt |
| 06 | [Search X (Twitter)](markdown/06_search_x_twitter.md) | You need what was said on X: an account's own statements, or how people are reacting to an event. | `chat.live_web_search` with `domains=["x.com"]` | Advanced search syntax, engagement floors, accounts |
| 07 | [Search the live web (Google)](markdown/07_search_the_live_web.md) | The answer lives on the wider web rather than in news coverage: company blogs, press releases, regulator and court sites, documentation, or pages published minutes ago. | `chat.live_web_search` | Live web search, `strict`, `lookback`, domains, single URL |
| 08 | [Search podcasts](markdown/08_search_podcasts.md) | You want what people said rather than what was reported: interviews, opinion, and long-form commentary from podcast episodes. | `news.search_news` with `podcasts` | `podcasts="only" / "include" / "none"`, podcasts in DeepNews |
| 09 | [Monitor a company](markdown/09_monitor_a_company.md) | You follow one organization's coverage over time: launches, deals, earnings, leadership changes, and legal issues. | `news.search_news`, `news.get_index_counts` | Entity guarantee + descriptive query, variants, exclusions, volume |
| 10 | [Monitor a person](markdown/10_monitor_a_person.md) | You follow coverage of one person, such as an executive or a politician: what they said, and what was reported about them. | `news.search_news` | Person guarantee, role in query, AND with a company, watchlists |
| 11 | [Monitor a product, brand, or industry](markdown/11_monitor_a_product_brand_or_industry.md) | What you follow is a product, a brand, or an industry or market rather than one company, so no single entity filter covers it. | `news.search_news`, `news.get_index_counts` | Combining string/entity guarantees, region scoping, sentiment, trade press, share of voice |
| 12 | [Run deep research (DeepNews)](markdown/12_run_deep_research.md) | You want a researched, cited answer rather than a list of articles: a question that takes more than one search, such as an investigation, a fact-check, a forecast, or a report across many companies. DeepNews plans the searches, follows what it finds across your chosen sources, and writes the answer. | `chat.get_deep_news` | `get_deep_news`, sources, streaming v2.0 events, `stream_sources_inline` per-call source batches, `filter_params`, async |
| 13 | [Set deep research depth](markdown/13_set_deep_research_depth.md) | A DeepNews answer or report misses things, or does more research than the question needs. Depth sets how much the agent searches before it answers. | `chat.get_deep_news` | `search_depth` / `max_depth`: how and why, sizing guide, cutoff backtests |
| 14 | [Prompt deep research](markdown/14_prompt_deep_research.md) | You want to guide how DeepNews does its research: which tools it uses and how, what it focuses on, and how it formats the output. | `chat.get_deep_news` | Role and tools, exact tool parameters, per-item procedures, fixed vs flexible params, fallbacks, defining what matters, dates and citations, output format |
| 15 | [Create an alert](markdown/15_create_an_alert.md) | A question needs revisiting on a schedule: a recurring research report, or a notification when a described event happens. | `chat.create_alert`, `run_alert`, `update_alert`, `delete_alert` | `ReportAbout` / `AlwaysAlertWhen` / `AlertOnceIf`, DeepNews reports, triggers, testing and managing |
| 16 | [Connect to the AskNews MCP server](markdown/16_connect_to_the_mcp_server.md) | An LLM should decide which AskNews searches to run: inside an assistant such as Claude, ChatGPT, or Cursor, or in an agent you build. | MCP tools at `https://mcp.asknews.app` | MCP vs SDK, auth and transport, tool catalog, MCP-vs-SDK parameter differences, connecting assistants, calling tools directly, `do_news_research` |
| 17 | [Build an agent on the MCP server](markdown/17_build_an_agent_on_mcp.md) | You want your own model, loop, and prompt to do the research on AskNews tools, instead of calling DeepNews. | MCP tools with LangChain | Tool selection, enforcing constraints with interceptors, rate-limit retries, date grounding, research system prompt, search budget, fail-fast, local tools |

## Running

```bash
pip install asknews
export ASKNEWS_API_KEY="..."
python cookbook/recipes/01_search_live_news.py
```

Recipe 15 creates, runs, and deletes a real alert. Change the trigger email
before running it.

Recipes 16 and 17 need extra packages: `pip install "fastmcp>=4"` for 16, and
`pip install langchain langchain-anthropic langchain-mcp-adapters` (plus
`ANTHROPIC_API_KEY`) for 17.

## Building the markdown

```bash
python cookbook/build.py
```

## Adding a recipe

1. Copy an existing recipe to `recipes/NN_short_name.py`. Name it after the
   task, in the imperative and with the terms the API docs use
   (`08_search_podcasts.py`), so readers and agents can match it to what
   they want to do.
2. Start with a `# %% [markdown]` cell whose first line is `# # Title`, the
   file name in words (`# # Search podcasts`), followed by a
   `**Use this when** ...` line.
3. Open with the "best practices" for the topic, then alternate short prose
   cells with code cells that each show one idea.
4. Keep every recipe standalone: its own imports and client setup.
5. Run `python cookbook/build.py` and add the recipe to the table above,
   with the same "Use this when" text and the SDK methods it calls.
