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
# - Use `n_articles=100` per page for bulk pulls (fewer round trips).
# - Always set a cap (articles or pages) so a broad query cannot run away.
# - Deduplicate on `article_id` when merging pages.
# - For very large pulls across long time ranges, split the range into
#   windows and paginate each window. Smaller windows are more reliable
#   and easy to resume.

# %%
import os
from datetime import datetime, timedelta, timezone

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["news"],
)

# %% [markdown]
# ## Basic offset loop

# %%
params = dict(
    query="Thailand Cambodia border conflict ceasefire peace talks",
    entity_guarantee=["Location:Thailand", "Location:Cambodia"],
    entity_guarantee_op="AND",
    hours_back=168,
    historical=True,
    time_filter="pub_date",
    n_articles=100,
    return_type="dicts",
    premium=True,
)

articles = {}
offset = None
max_articles = 500

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
            historical=True,
            start_timestamp=int(start.timestamp()),
            end_timestamp=int(end.timestamp()),
            time_filter="pub_date",
            n_articles=100,
            return_type="dicts",
            premium=True,
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
