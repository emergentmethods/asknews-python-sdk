# Searching Google (live web search)

`ask.chat.live_web_search()` runs a live web search, fetches the pages,
and returns an LLM-distilled summary of each one (`key_points`), plus a
prompt-ready `as_string`.

Use it to fill gaps in the news index: company blogs, press release pages,
regulator and court sites, niche trade publications, or anything published
in the last few minutes.

Parameters that matter:

- `queries`: a list of Google-style keyword queries. Short keyword strings
  beat full sentences.
- `lookback`: hours back to accept.
- `strict=True`: only keep results with a **known** publication date
  inside `lookback`. Turn this on for monitoring, where an undated page
  is worse than no page.
- `domains`: restrict to specific sites.
- `engine="v1.5"`: the newer search engine. Prefer it.
- `start_datetime` / `end_datetime`: an explicit window instead of
  `lookback`.
- `url`: distill one specific page instead of searching.

```python
import os
from datetime import datetime, timedelta, timezone

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["chat"],
)
```

## Recent, strictly dated web results

```python
response = ask.chat.live_web_search(
    queries=["OpenAI Disney licensing deal Sora"],
    lookback=24,
    strict=True,
    engine="v1.5",
)

for r in response.as_dicts:
    print(r.published, r.source, r.title, r.url)
    for p in r.key_points:
        print("  -", p)
```

## Restrict to specific sites

```python
response = ask.chat.live_web_search(
    queries=["Delaware Court of Chancery ruling"],
    domains=["courts.delaware.gov"],
    lookback=72,
    engine="v1.5",
)
print(response.as_string)
```

## An explicit window

```python
end = datetime.now(timezone.utc)
response = ask.chat.live_web_search(
    queries=["battery robotics innovation"],
    start_datetime=end - timedelta(days=7),
    end_datetime=end,
    engine="v1.5",
)
```

## Distill a single URL

```python
response = ask.chat.live_web_search(
    queries=["key announcements"],
    url="https://www.anthropic.com/news",
)
print(response.as_string)
```
