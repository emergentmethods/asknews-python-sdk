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

| # | Recipe | Covers |
|---|---|---|
| 00 | Setup and core concepts | Client, which endpoint to use, filter-then-rank model, time windows, `kw` vs `nl`, return types, caching |
| 01 | Getting real-time news | Live index, `pub_date` vs `crawl_date`, newest-first, polling |
| 02 | Searching archive news | `historical=True`, exact windows, point-in-time context for backtests |
| 03 | Paginating | `offset` loops, caps, dedupe, windowed bulk pulls |
| 04 | Building LLM context | `as_string` vs custom context from `as_dicts`, citations, graphs, geo |
| 05 | Using Wikipedia | `search_wiki` parameters, background + news in one prompt |
| 06 | Searching X (Twitter) | Advanced search syntax, engagement floors, accounts |
| 07 | Searching Google | Live web search, `strict`, `lookback`, domains, single URL |
| 08 | Searching podcasts | `podcasts="only" / "include" / "none"`, podcasts in DeepNews |
| 09 | Tracking a company | Entity guarantee + descriptive query, variants, exclusions, volume |
| 10 | Tracking a person | Person guarantee, role in query, AND with a company, watchlists |
| 11 | Tracking a product, brand, or industry | Combining string/entity guarantees, region scoping, sentiment, trade press, share of voice |
| 12 | Deep research basics | `get_deep_news`, sources, streaming v2.0 events, `stream_sources_inline` per-call source batches, `filter_params`, async |
| 13 | Deep research depth | `search_depth` / `max_depth`: how and why, sizing guide, cutoff backtests |
| 14 | Prompting deep research | Surgical tool instructions, per-item procedures, fixed vs flexible params, report rules |
| 15 | Creating an alert | `ReportAbout` / `AlwaysAlertWhen` / `AlertOnceIf`, DeepNews reports, triggers, testing and managing |
| 16 | Using the MCP server | MCP vs SDK, auth and transport, tool catalog, MCP-vs-SDK parameter differences, connecting assistants, calling tools directly, `do_news_research` |
| 17 | Building agents on the MCP server | Tool selection, enforcing constraints with interceptors, rate-limit retries, date grounding, research system prompt, search budget, fail-fast, local tools |

## Running

```bash
pip install asknews
export ASKNEWS_API_KEY="..."
python cookbook/recipes/01_getting_real_time_news.py
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

1. Copy an existing recipe to `recipes/NN_short_name.py`.
2. Start with a `# %% [markdown]` cell whose first line is `# # Title`.
3. Open with the "best practices" for the topic, then alternate short prose
   cells with code cells that each show one idea.
4. Keep every recipe standalone: its own imports and client setup.
5. Run `python cookbook/build.py` and add the recipe to the table above.
