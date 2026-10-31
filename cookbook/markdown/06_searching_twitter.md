# Searching X (Twitter)

X search goes through `ask.chat.live_web_search()` with
`domains=["x.com"]`. Each entry in `queries` is an **X advanced search
expression**, so you get the full operator set:

| Operator | Meaning |
|---|---|
| `from:handle` | Posts by an account |
| `@handle` | Posts mentioning an account |
| `"exact phrase"` | Exact phrase |
| `A OR B`, `(A B)` | Boolean logic and grouping |
| `min_faves:20` | Minimum likes. **The most useful noise filter.** |
| `min_retweets:10` | Minimum reposts |
| `filter:has_engagement` | Has any engagement |
| `since:2026-02-22_12:30:30_UTC` | After a timestamp |
| `-term` | Exclude a term |

Reference: https://github.com/igorbrigadir/twitter-advanced-search

Best practices:

- Always add an engagement floor (`min_faves:20` for monitoring a company,
  `min_faves:1000` for "what is everyone talking about"). Without it you
  get spam and bots.
- For an account, use `(from:handle OR @handle)` to get both what they
  said and what others said to or about them.
- Use `lookback` (hours) to bound recency.
- Results are LLM-distilled: each result has `key_points`, plus
  `as_string` for prompt injection.

```python
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["chat"],
)
```

## What a company is saying, and what is said to it

```python
response = ask.chat.live_web_search(
    queries=["(from:OpenAI OR @OpenAI) min_faves:20"],
    domains=["x.com"],
    lookback=24,
)

for post in response.as_dicts:
    print(post.published, post.url)
    for point in post.key_points:
        print("  -", point)
```

## A topic with high engagement only

```python
response = ask.chat.live_web_search(
    queries=['("Strait of Hormuz" OR Hormuz) (tanker OR shipping OR blockade) min_faves:100'],
    domains=["x.com"],
    lookback=12,
)
print(response.as_string)
```

## Several angles in one call

`queries` is a list. Use it to cover several phrasings or accounts at
once instead of making separate calls.

```python
response = ask.chat.live_web_search(
    queries=[
        '"Jensen Huang" min_faves:50',
        "(from:nvidia OR @nvidia) min_faves:50",
        "(NVDA OR NVIDIA) (earnings OR guidance) min_faves:200",
    ],
    domains=["x.com"],
    lookback=24,
)
print(len(response.as_dicts), "posts")
```
