# %% [markdown]
# # Deep research depth: how and why
#
# Depth is the most important DeepNews setting. It decides how much
# research the agent does before writing, which decides coverage, cost,
# and latency.
#
# - **`search_depth`**: the **minimum** number of searches the agent must
#   run before it is allowed to answer. A search is one tool call: deciding
#   on a query, running it, and reading the results. This is your main dial
#   for thoroughness.
# - **`max_depth`**: the **maximum** total number of searches. It is
#   headroom for following leads that turn up along the way, and a guard
#   against runaway cost.
#
# `search_depth` must be less than or equal to `max_depth`.
#
# ## Why depth matters
#
# **Too little depth** is the most common failure. The agent stops before
# it has covered the task: a portfolio report silently skips half the
# companies, a "who is involved" question finds the first two parties and
# not the third, a contested claim gets one side.
#
# **Too much depth** on a narrow question wastes tokens and time, and the
# agent may wander into loosely related material to use the budget.
#
# So size depth to the **shape of the task**, not to how important it is.
#
# ## Sizing guide
#
# Count how many distinct searches a careful human researcher would run.
# That is roughly your `search_depth`. Set `max_depth` to ~1.5-2x that to
# leave room for follow-ups.
#
# | Task shape | `search_depth` | `max_depth` |
# |---|---|---|
# | One factual question ("What has X said about Y?") | 1-2 | 3-5 |
# | One topic, a few angles (news + social + web) | 3-5 | 8-10 |
# | One theme, a daily report (e.g. sports-team ownership changes) | 5 | 10 |
# | Top-N headlines across a sector | 15 | 20 |
# | Broad sweep with rumors + confirmed events (e.g. all tech M&A today) | 20 | 50 |
# | A list of N entities, ~2 searches each (news, then X) | ~N to 2N | ~1.5-2x |
#
# Real examples from production monitoring reports:
#
# - ~55 companies and people, news + X for each: `search_depth=40`,
#   `max_depth=80`.
# - ~100 people for an event briefing, news + X for each:
#   `search_depth=190`, `max_depth=200`.
#
# Limits: `search_depth` can be at most 190 and `max_depth` at most 200,
# both for direct `get_deep_news` calls and for alert reports.
#
# ## Depth works with the prompt, not instead of it
#
# Depth gives the agent budget. The prompt tells it how to spend that
# budget. For list-shaped tasks, spell out the per-item procedure ("for
# each company do Step 1 then Step 2, then move on") so the agent spends
# its rounds evenly instead of going deep on the first few items. See
# [14 Prompting deep research](14_prompting_deep_research.md).
#
# ## Other knobs for deep runs
#
# - `max_parallel_tool_calls` (1-4): run several tool calls per round.
#   Faster wall-clock on wide tasks. Keep it at 1 when the order of
#   searches matters (e.g. strictly per-entity procedures).
# - `enable_source_pruning=True`: drop irrelevant sources during research
#   to keep the context small. Recommended for large `search_depth`; the
#   trade-off is that a pruned source can't be cited later.
# - `only_cited_sources`: return only the sources cited in the answer
#   (default) or everything retrieved (`False`, useful for auditing what
#   the agent saw).

# %%
import os
from datetime import datetime, timezone

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["chat", "news"],
)

# %% [markdown]
# ## Shallow: one question

# %%
response = ask.chat.get_deep_news(
    messages=[{"role": "user", "content": "What has Emirates said about fuel costs this quarter?"}],
    sources=["asknews"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=1,
    max_depth=3,
)

# %% [markdown]
# ## Medium: an investigation with several angles

# %%
response = ask.chat.get_deep_news(
    messages=[
        {
            "role": "user",
            "content": (
                "Who are the parties involved in the reported acquisition talks for "
                "Wiz, what are the reported terms, and what do regulators and "
                "analysts say about the deal's chances?"
            ),
        }
    ],
    sources=["asknews", "google", "x"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=5,
    max_depth=10,
)

# %% [markdown]
# ## Deep: a list of entities, depth sized to the list

# %%
companies = ["Revolut", "Monzo", "Ramp", "Databricks", "Anduril Industries", "Figma"]
SEARCHES_PER_COMPANY = 2  # news, then X

response = ask.chat.get_deep_news(
    messages=[
        {
            "role": "user",
            "content": (
                "For EACH company below, first search news for the last 24 hours, then "
                "search X for the last 24 hours, then move to the next company. Report "
                "only companies with material developments.\n\n" + "\n".join(companies)
            ),
        }
    ],
    sources=["asknews", "x", "google"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=len(companies) * SEARCHES_PER_COMPANY,
    max_depth=len(companies) * SEARCHES_PER_COMPANY * 2,
    enable_source_pruning=True,
    filter_params={"hours_back": 24, "time_filter": "pub_date", "n_articles": 5},
)

# %% [markdown]
# ## Backtesting with a knowledge cutoff
#
# `cutoff_datetime` tells every tool to ignore information after a point in
# time. Also cap the news searches with `filter_params["end_timestamp"]`
# so the two agree. This lets you evaluate research or forecasts as of a
# past date without leakage.

# %%
cutoff = datetime(2026, 4, 15, 14, 0, tzinfo=timezone.utc)

response = ask.chat.get_deep_news(
    messages=[{"role": "user", "content": "Will the ECB cut rates at its next meeting? Give a probability."}],
    sources=["asknews", "google"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=3,
    max_depth=6,
    cutoff_datetime=cutoff,
    filter_params={"end_timestamp": int(cutoff.timestamp()), "historical": True},
)
