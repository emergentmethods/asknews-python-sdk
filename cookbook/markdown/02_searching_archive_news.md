# Searching archive news

Coverage goes back to 2023, and the same `search_news` call reaches it:
give a window that starts in the past. There is no separate mode or flag.

Best practices:

- **Pass both `start_timestamp` and `end_timestamp`.** A start more than
  48 hours ago reaches back. An `end_timestamp` on its own looks 160
  days back from it, which is rarely the window you meant. The
  `historical` parameter is deprecated and has no effect, so leave it
  out.
- One request can span at most 160 days. Split longer periods into
  windows, see [03 Paginating](03_paginating.md).
- A request whose window starts more than 48 hours ago costs 5 credits,
  and so does every page of it.
- Prefer `start_timestamp` / `end_timestamp` over a huge `hours_back` for
  anything you want to reproduce later.
- Use `time_filter="pub_date"` for historical research: you almost always
  mean "published in this window", not "crawled in this window".
- Build timestamps from timezone-aware datetimes so the window is the one
  you meant.

```python
import os
from datetime import datetime, timezone

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
)
```

## A fixed historical window

```python
start = datetime(2025, 1, 1, tzinfo=timezone.utc)
end = datetime(2025, 3, 31, 23, 59, 59, tzinfo=timezone.utc)

response = ask.news.search_news(
    query="inflation rate United States CPI report",
    start_timestamp=int(start.timestamp()),
    end_timestamp=int(end.timestamp()),
    time_filter="pub_date",
    method="kw",
    n_articles=10,
    return_type="dicts",
)
for a in response.as_dicts:
    print(f"{a.pub_date:%Y-%m-%d} | {a.source_id} | {a.title}")
```

## "What did the news say at the time?" (point-in-time context)

For forecasting backtests and evaluations, cap `end_timestamp` at the
moment you are simulating so nothing published afterwards can leak into
the context. `method="nl"` works well when the query is a full question.

```python
as_of = datetime(2024, 10, 1, tzinfo=timezone.utc)

response = ask.news.search_news(
    query="Will the Federal Reserve cut interest rates at the November 2024 FOMC meeting?",
    method="nl",
    end_timestamp=int(as_of.timestamp()),
    start_timestamp=int(as_of.timestamp()) - 14 * 24 * 3600,
    time_filter="pub_date",
    n_articles=10,
    return_type="string",
    try_cache="7d",
)
print(response.as_string)
```

## Archive + entity guarantee

Hard filters work the same way on the archive. This pulls articles about
a specific organization in a quarter. For more than one page of results,
see [03 Paginating](03_paginating.md).

```python
response = ask.news.search_news(
    entity_guarantee=["Organization:OpenAI"],
    query="OpenAI funding round valuation investors",
    start_timestamp=int(datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp()),
    end_timestamp=int(datetime(2025, 4, 1, tzinfo=timezone.utc).timestamp()),
    time_filter="pub_date",
    n_articles=10,
    return_type="dicts",
)
print(len(response.as_dicts), "articles")
```
