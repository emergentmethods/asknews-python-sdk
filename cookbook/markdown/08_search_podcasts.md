# Search podcasts

**Use this when** you want what people said rather than what was reported:
interviews, opinion, and long-form commentary from podcast episodes.

Podcast episodes are indexed alongside news and are searchable with
`search_news`. The `podcasts` parameter controls them:

- `"include"` (default): news and podcasts together.
- `"only"`: podcasts only.
- `"none"`: exclude podcasts (articles only).

All the usual filters (`entity_guarantee`, `string_guarantee`,
and time windows) apply to podcasts too.

Podcasts are where opinions, interviews, and long-form commentary live.

```python
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
)
```

## Podcasts only

```python
response = ask.news.search_news(
    query="opinions on the war with Iran, commentary, debate",
    podcasts="only",
    hours_back=168,
    n_articles=10,
    return_type="dicts",
)
for ep in response.as_dicts:
    print(f"{ep.pub_date:%Y-%m-%d} | {ep.source_id} | {ep.title}")
```

## What a person said on podcasts

Combine `podcasts="only"` with an entity guarantee to find appearances
and mentions.

```python
response = ask.news.search_news(
    query="interview, podcast appearance, comments on AI regulation",
    entity_guarantee=["Person:Dario Amodei"],
    podcasts="only",
    hours_back=720,
    n_articles=10,
    return_type="string",
)
print(response.as_string)
```

## Keeping podcasts out

If you need only written reporting, e.g. for a news-only digest, exclude
them explicitly.

```python
response = ask.news.search_news(
    query="central bank rate decision",
    podcasts="none",
    hours_back=24,
    n_articles=10,
)
```

## Podcasts as a DeepNews source

DeepNews can research podcasts as their own source. See
[12 Run deep research (DeepNews)](12_run_deep_research.md) for streaming
details.

```python
research = ask.chat.get_deep_news(
    messages=[{"role": "user", "content": "What are the current opinions on the war with Iran?"}],
    sources=["podcasts"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=1,
    max_depth=3,
    stream=False,
)
print(research.choices[0].message.content)
```
