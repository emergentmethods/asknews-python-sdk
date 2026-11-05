# %% [markdown]
# # Getting real-time news
#
# The default `search_news` call covers the last 24 hours, which is what you
# want for "what's happening right now".
#
# Best practices:
#
# - Keep the window inside the last 48 hours (`hours_back=48` or less).
#   That costs 1 credit instead of 5.
# - Set `hours_back` explicitly. The default is 24.
# - Use `time_filter="pub_date"` when the *publication* time matters (e.g.
#   "only stories published in the last 6 hours"). Use the default
#   `crawl_date` when polling for "new since my last call".
# - Use `sort_by="pub_date"` to arrange the results newest first. It sorts
#   the best matches by date rather than fetching the newest articles, so
#   pair it with a short `hours_back`.

# %%
import os
import time

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
)

# %% [markdown]
# ## The latest on a topic

# %%
response = ask.news.search_news(
    query="Federal Reserve interest rate decision, FOMC statement, Powell press conference",
    hours_back=6,
    time_filter="pub_date",
    n_articles=10,
    return_type="string",
)
print(response.as_string)

# %% [markdown]
# ## Sorted by date, restricted to high-authority outlets
#
# `page_rank` is an upper bound on a domain's rank: lower is more
# prominent, and `page_rank=100000` or lower targets top sources and drops
# the long tail of low-authority sites. `diversify_sources=True` stops one outlet
# from dominating the results.

# %%
response = ask.news.search_news(
    query="earthquake tsunami warning",
    hours_back=3,
    time_filter="pub_date",
    sort_by="pub_date",
    page_rank=100000,
    diversify_sources=True,
    n_articles=10,
    return_type="dicts",
)
for a in response.as_dicts:
    print(f"{a.pub_date:%H:%M} | {a.source_id} | {a.title}")

# %% [markdown]
# ## Browsing a category, no query
#
# `query` is optional. With no query you get a page of articles from the
# window that pass your filters, sorted by date within the page. It is not
# necessarily the newest articles in the window, so keep the window short.

# %%
response = ask.news.search_news(
    categories=["Technology"],
    languages=["en"],
    hours_back=1,
    n_articles=10,
    return_type="dicts",
)
print(len(response.as_dicts), "technology articles from the last hour")

# %% [markdown]
# ## Polling for new articles
#
# For a lightweight poller, track the last time you checked and use
# `start_timestamp` with the default `time_filter="crawl_date"`, so you pick
# up anything AskNews ingested since then even if the publisher back-dated
# it. Deduplicate on `article_id`. If more articles than one page can arrive
# between polls, paginate with `offset` (see [03 Paginating](03_paginating.md)).

# %%
seen: set = set()
last_checked = int(time.time()) - 15 * 60

for _ in range(3):
    now = int(time.time())
    response = ask.news.search_news(
        query="Tesla recall, Tesla investigation, Tesla Autopilot crash",
        entity_guarantee=["Organization:Tesla"],
        start_timestamp=last_checked,
        end_timestamp=now,
        time_filter="crawl_date",
        n_articles=10,
        return_type="dicts",
    )
    for a in response.as_dicts:
        if a.article_id not in seen:
            seen.add(a.article_id)
            print("NEW:", a.title, a.article_url)
    last_checked = now
    time.sleep(60)

# %% [markdown]
# For anything more than a script, use an alert instead of a polling loop.
# See [15 Creating an alert](15_creating_an_alert.md).
