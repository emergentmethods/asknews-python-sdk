# %% [markdown]
# # Tracking a company
#
# The reliable pattern is **entity guarantee + descriptive query**:
#
# - `entity_guarantee=["Organization:<Name>"]` makes it a hard requirement
#   that the article is actually about (mentions, as an extracted entity)
#   the company. This removes false matches on common words ("Apple",
#   "Block", "Ramp", "Notion").
# - `query` then ranks those articles by **what you care about**: the
#   company's description, its handle and website, and the kinds of events
#   that matter to you.
#
# Entity guarantee format is `"<Type>:<Name>"` with no space after the
# colon. Common types: `Organization`, `Person`, `Location`, `Event`,
# `Product`, `Money`, `Law`, `Technology`.
#
# Best practices:
#
# - Put the company description in the query. "Ramp, corporate spend
#   management, cards, bill pay" ranks very differently from just "Ramp".
# - Add name variants with OR: legal name, short name, ticker
#   (`"Organization:Meta"`, `"Organization:Meta Platforms"`).
#   `entity_guarantee_op` defaults to `"OR"`.
# - Use `time_filter="pub_date"` and an explicit `hours_back` for daily
#   monitoring, so "last 24 hours" means published in the last 24 hours.
# - Use `page_rank` and `languages` to keep the signal-to-noise ratio high.
# - If a company has a lot of news, do a second, narrower search on the
#   topic that surfaced, rather than one huge `n_articles`.

# %%
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["news", "chat"],
)

# %% [markdown]
# ## Daily company monitor

# %%
MATERIAL_EVENTS = (
    "Financial & Capital Events, Revenue, Earnings, Funding, Valuation, IPO, Debt, "
    "Partnerships, M&A, Leadership Changes, Product Launches, Regulatory Actions, "
    "Lawsuits, Competitive Threats, Executive Statements, SEC filings, "
    "stock price movements, analyst ratings"
)

response = ask.news.search_news(
    entity_guarantee=["Organization:Ramp"],
    query=f"Ramp, corporate spend management platform, cards, bill pay, expense tracking, "
    f"@tryramp, ramp.com, {MATERIAL_EVENTS}",
    hours_back=24,
    time_filter="pub_date",
    n_articles=10,
    page_rank=100000,
    languages=["en"],
    return_type="both",
    premium=True,
)
print(response.as_string)

# %% [markdown]
# ## Public company: name variants and ticker

# %%
response = ask.news.search_news(
    entity_guarantee=["Organization:Tesla", "Organization:TSLA", "Organization:Tesla Inc."],
    entity_guarantee_op="OR",
    query="Tesla stock price, deliveries, earnings, analyst ratings, electric vehicles",
    categories=["Finance", "Business"],
    hours_back=48,
    time_filter="pub_date",
    n_articles=10,
    return_type="dicts",
    premium=True,
)

# %% [markdown]
# ## Narrowing to one kind of event
#
# Add a `string_guarantee` on top of the entity guarantee to require event
# vocabulary. Here: only articles about the company that use M&A language.

# %%
response = ask.news.search_news(
    entity_guarantee=["Organization:Databricks"],
    string_guarantee=["acquire", "acquisition", "acquires", "merger", "deal"],
    string_guarantee_op="OR",
    query="Databricks acquisition, acquires startup, deal terms, purchase price",
    hours_back=720,
    historical=True,
    time_filter="pub_date",
    n_articles=20,
    return_type="dicts",
    premium=True,
)

# %% [markdown]
# ## Excluding noise
#
# `reverse_entity_guarantee` and `reverse_string_guarantee` drop articles
# that contain those entities/strings. Useful for a company that shares a
# name with something else, or for removing recurring irrelevant coverage.

# %%
response = ask.news.search_news(
    entity_guarantee=["Organization:Apple"],
    reverse_string_guarantee=["recipe", "orchard", "apple cider"],
    query="Apple Inc. iPhone, App Store, antitrust, Tim Cook, earnings",
    hours_back=24,
    n_articles=10,
    premium=True,
)

# %% [markdown]
# ## Company news + the company's own posts
#
# News misses what a company announces on social media. Pair the search
# with an X search. See [06 Searching X](06_searching_twitter.md).

# %%
posts = ask.chat.live_web_search(
    queries=["(from:tryramp OR @tryramp) min_faves:20"],
    domains=["x.com"],
    lookback=24,
)

# %% [markdown]
# ## Coverage volume over time
#
# `get_index_counts` returns article counts per time bucket for the same
# filters, which is a quick way to spot spikes in attention.

# %%
from datetime import datetime, timedelta, timezone


end = datetime.now(timezone.utc)
counts = ask.news.get_index_counts(
    start_datetime=end - timedelta(days=30),
    end_datetime=end,
    entity_guarantee=["Organization:Ramp"],
    sampling="1d",
)
for bucket in counts.root:
    print(f"{bucket.start:%Y-%m-%d}: {bucket.count}")
