# %% [markdown]
# # Paginating
#
# `search_news` returns at most `n_articles` per call. To go deeper, pass
# `response.offset` back into the **same** query. When `response.offset`
# is `None` (or the page comes back empty), you have reached the end.
#
# Best practices:
#
# - Keep every parameter identical between pages. Only `offset` changes.
# - Use the largest page your plan allows: 10 on Pay as you go, Pro and
#   Spelunker (more returns a 400 error), and 30 on Analyst and Enterprise
#   (a larger value is reduced to 30). The examples use 10.
# - Always set a cap (articles or pages) so a broad query cannot run away.
# - Deduplicate on `article_id` when merging pages.
# - For very large pulls across long time ranges, split the range into
#   windows and paginate each window. Smaller windows are more reliable
#   and easy to resume. A window can span at most 160 days, and numeric
#   offsets stop at 3000.
# - Paginate with `method="kw"` or `"nl"`; `"both"` cannot be paginated.
#   Pagination also needs at least one of `query`, `domain_url`,
#   `entity_guarantee`, `authors`, or a geographic filter.

# %%
import os
from datetime import datetime, timedelta, timezone

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
)

# %% [markdown]
# ## Basic offset loop

# %%
window_end = datetime.now(timezone.utc)

params = dict(
    query="Thailand Cambodia border conflict ceasefire peace talks",
    entity_guarantee=["Location:Thailand", "Location:Cambodia"],
    entity_guarantee_op="AND",
    start_timestamp=int((window_end - timedelta(days=7)).timestamp()),
    end_timestamp=int(window_end.timestamp()),
    time_filter="pub_date",
    n_articles=10,
    return_type="dicts",
)

articles = {}
offset = None
max_articles = 100

while True:
    response = ask.news.search_news(**params, offset=offset or 0)
    for a in response.as_dicts or []:
        articles[a.article_id] = a
    print(f"page: {len(response.as_dicts or [])} articles, next offset: {response.offset}")

    offset = response.offset
    if not offset or not response.as_dicts or len(articles) >= max_articles:
        break

print(len(articles), "unique articles")

# %% [markdown]
# ## Windowed pagination for large historical pulls
#
# Walk backwards through time in fixed windows and paginate within each.
# This keeps every request bounded and lets you checkpoint after each
# window.

# %%
def pull_window(start: datetime, end: datetime, **filters) -> list:
    out = []
    offset = None
    while True:
        response = ask.news.search_news(
            **filters,
            start_timestamp=int(start.timestamp()),
            end_timestamp=int(end.timestamp()),
            time_filter="pub_date",
            n_articles=10,
            return_type="dicts",
            offset=offset or 0,
        )
        out.extend(response.as_dicts or [])
        offset = response.offset
        if not offset or not response.as_dicts:
            return out


now = datetime.now(timezone.utc)
window = timedelta(days=30)
all_articles = {}

for i in range(6):  # last ~6 months, one month at a time
    end = now - i * window
    start = end - window
    batch = pull_window(
        start,
        end,
        query="meal kit, recipe box, meal delivery kit, meal subscription",
        string_guarantee=["meal kit", "meal kits", "recipe box", "meal subscription"],
        string_guarantee_op="OR",
    )
    for a in batch:
        all_articles[a.article_id] = a
    print(f"{start:%Y-%m-%d} -> {end:%Y-%m-%d}: {len(batch)} articles")

print(len(all_articles), "unique articles total")
