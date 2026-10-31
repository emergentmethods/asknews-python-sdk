# Searching archive news

The live index holds the last ~48 hours. To search further back, set
`historical=True` and give an explicit window.

Best practices:

- **Always pass `historical=True` for windows older than 48 hours.**
  Without it, an old `start_timestamp`/`end_timestamp` or a large
  `hours_back` quietly returns only recent articles.
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
    scopes=["news"],
)
```

## A fixed historical window

```python
start = datetime(2025, 1, 1, tzinfo=timezone.utc)
end = datetime(2025, 3, 31, 23, 59, 59, tzinfo=timezone.utc)

response = ask.news.search_news(
    query="inflation rate United States CPI report",
    historical=True,
    start_timestamp=int(start.timestamp()),
    end_timestamp=int(end.timestamp()),
    time_filter="pub_date",
    method="kw",
    n_articles=10,
    return_type="dicts",
    premium=True,
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
    historical=True,
    end_timestamp=int(as_of.timestamp()),
    start_timestamp=int(as_of.timestamp()) - 14 * 24 * 3600,
    time_filter="pub_date",
    n_articles=15,
    return_type="string",
    premium=True,
    try_cache="7d",
)
print(response.as_string)
```

## Archive + entity guarantee

Hard filters work the same way on the archive. This pulls every article
about a specific organization in a quarter. For more than one page of
results, see [03 Paginating](03_paginating.md).

```python
response = ask.news.search_news(
    entity_guarantee=["Organization:OpenAI"],
    query="OpenAI funding round valuation investors",
    historical=True,
    start_timestamp=int(datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp()),
    end_timestamp=int(datetime(2025, 4, 1, tzinfo=timezone.utc).timestamp()),
    time_filter="pub_date",
    n_articles=25,
    return_type="dicts",
    premium=True,
)
print(len(response.as_dicts), "articles")
```
