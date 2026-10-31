# Building LLM context from news

The most common use of `search_news` is retrieval for your own LLM. There
are two good ways to do it.

Best practices:

- Start with `return_type="string"`. It is already prompt-optimized,
  includes citation keys, and is the least work.
- Switch to `return_type="dicts"` when you need control: your own
  formatting, extra metadata (entities, bias, reporting voice, geo),
  reranking, or filtering after retrieval.
- Keep the citation key (`as_string_key`) in each document so the model
  can cite, and you can map citations back to URLs.
- Include the publication date in each document. LLMs reason much better
  about "latest" and "before/after" when the date sits next to the text.

```python
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["news"],
)
```

## Option 1: the prompt-optimized string

`doc_start_delimiter` / `doc_end_delimiter` let you match the tags your
prompt already uses.

```python
response = ask.news.search_news(
    query="EU US trade negotiations tariffs",
    hours_back=48,
    n_articles=10,
    return_type="string",
    doc_start_delimiter="<article>",
    doc_end_delimiter="</article>",
    premium=True,
)

prompt = f"""Answer using only the articles below. Cite articles by their citation key.

{response.as_string}

Question: Where do EU-US trade negotiations stand right now?"""
```

## Option 2: build your own context from dicts

`return_graphs=True` adds an entity relationship graph per article and
`return_geo=True` adds coordinates for extracted locations. Only request
them when your prompt uses them; they add tokens.

```python
response = ask.news.search_news(
    query="Iran Strait of Hormuz shipping tanker",
    hours_back=48,
    n_articles=10,
    return_type="dicts",
    return_graphs=True,
    return_geo=True,
    premium=True,
)


def render_entities(entities) -> str:
    lines = []
    for entity_type, values in entities:
        if values and entity_type != "Date":
            lines.append(f"{entity_type}: {' | '.join(values)}")
    return "\n".join(lines)


def render_graph(graph) -> str:
    if not graph:
        return ""
    edges = {f"[{e['from']}] <{e['label']}> [{e['to']}]" for e in graph.edges}
    return "\n".join(sorted(edges))


def render_geo(geo) -> str:
    if not geo:
        return ""
    return "\n".join(f"{k} @ {v.latitude}, {v.longitude}" for k, v in geo.items())


def build_context(articles) -> str:
    docs = []
    for a in articles:
        sentiment = {1: "positive", -1: "negative"}.get(a.sentiment, "neutral")
        key_points = "\n".join(f"- {p}" for p in (a.key_points or [])) or a.summary
        docs.append(
            f"""<doc>
Citation Key: {a.as_string_key}
Title: {a.title}
URL: {a.article_url}
Published: {a.pub_date:%B %d %Y, %H:%M} UTC
Source: {a.source_id}
Reporting voice: {a.reporting_voice}
Sentiment: {sentiment}

Key points:
{key_points}

Entities:
{render_entities(a.entities)}

Relationships:
{render_graph(a.entity_relation_graph)}

Locations:
{render_geo(a.geo_coordinates)}
</doc>"""
        )
    return "\n\n".join(docs)


print(build_context(response.as_dicts))
```

## Post-retrieval filtering

With dicts you can apply logic the API does not have, e.g. keeping only
reported news (no opinion pieces) and sorting by recency.

```python
reported = [a for a in response.as_dicts if a.content_type not in ("opinion", "review")]
reported.sort(key=lambda a: a.pub_date, reverse=True)
```
