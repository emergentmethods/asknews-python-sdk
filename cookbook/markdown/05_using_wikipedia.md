# Using Wikipedia

`ask.wiki.search_wiki()` searches a chunked Wikipedia index. Pair it with
news: Wikipedia gives the stable background (who someone is, what a
company does, the history of a conflict), news gives what changed.

Parameters that matter:

- `n_documents`: how many chunks to return.
- `neighbor_chunks`: how many surrounding chunks to attach to each hit, so
  a match comes with its context. `1` is a good default.
- `include_main_section=True`: always include the article's lead section,
  the densest summary of the subject.
- `full_articles=True`: return whole articles. Large; only use when you
  really need everything.
- `diversify`: `0.0` to `1.0`. Higher spreads results across more distinct
  articles instead of many chunks from one.
- `string_guarantee`: chunks must contain these strings.
- `hybrid_search=True`: blend keyword and semantic matching. Helps with
  exact names and rare terms.

```python
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["news"],
)
```

## Background on an entity

```python
response = ask.wiki.search_wiki(
    query="Anduril Industries defense technology company founders products",
    n_documents=5,
    neighbor_chunks=1,
    include_main_section=True,
    hybrid_search=True,
)

for doc in response.documents:
    print(doc.title, doc.url)
    print(doc.content[:500])
    print("---")
```

## A broad topic, spread across articles

```python
response = ask.wiki.search_wiki(
    query="history of the Strait of Hormuz as a shipping chokepoint",
    n_documents=10,
    diversify=0.5,
)
print({doc.title for doc in response.documents})
```

## Background + news in one prompt

A common pattern: Wikipedia for "who/what", news for "what's new".

```python
subject = "Helsing"

background = ask.wiki.search_wiki(
    query=f"{subject} European defense AI company",
    n_documents=3,
    include_main_section=True,
    string_guarantee=[subject],
)
news = ask.news.search_news(
    query=f"{subject} contract funding drones defense AI",
    entity_guarantee=[f"Organization:{subject}"],
    hours_back=168,
    historical=True,
    n_articles=10,
    return_type="string",
    premium=True,
)

background_text = "\n\n".join(
    f"<wiki title={d.title!r} url={d.url!r}>\n{d.content}\n</wiki>" for d in background.documents
)
prompt = f"""Background (Wikipedia):
{background_text}

Recent news:
{news.as_string}

Summarize what {subject} does and what has changed for it in the last week."""
```
