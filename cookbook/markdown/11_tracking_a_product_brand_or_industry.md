# Tracking a product, brand, or industry

Products, brands, and industries rarely map to one clean entity, so you
combine filters. The building blocks:

| Filter | Use it for |
|---|---|
| `string_guarantee` + `string_guarantee_op="OR"` | Product names, brand spellings, industry vocabulary that **must** appear |
| `entity_guarantee` with `Product:` / `Organization:` / `Location:` / `Event:` | Extracted entities that must appear |
| `reverse_string_guarantee` / `reverse_entity_guarantee` | Removing known noise |
| `categories` | Coarse topic restriction (`Business`, `Technology`, `Finance`, ...) |
| `domain_url` / `bad_domain_url` | Trade press only, or excluding sites |
| `languages`, `countries`, `continents` | Market / geography |
| `sentiment` | Only negative (or positive) coverage |
| `page_rank` | Drop low-authority sites |
| `query` | Ranking: what matters most within the filtered set |

Best practices:

- `string_guarantee` is an exact substring match. Include plurals and
  variants yourself (`"meal kit"`, `"meal kits"`).
- Combine a **geography** entity guarantee with a **topic** string
  guarantee to scope an industry to a market.
- Keep the `query` as a comma-separated list of the vocabulary you care
  about. With `method="kw"` this ranks well.

```python
import os
from datetime import datetime, timedelta, timezone

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["news"],
)
```

## A product

```python
response = ask.news.search_news(
    string_guarantee=["Vision Pro", "visionOS"],
    string_guarantee_op="OR",
    entity_guarantee=["Organization:Apple"],
    query="Apple Vision Pro sales, reviews, price, shipments, developer adoption",
    hours_back=168,
    historical=True,
    n_articles=20,
    return_type="dicts",
    premium=True,
)
```

## A brand's negative press

`sentiment="negative"` plus `reporting_voice=["Objective", "Analytical"]`
keeps reported problems and drops `"Persuasive"` / `"Sensational"` takes.

```python
response = ask.news.search_news(
    entity_guarantee=["Organization:Boeing"],
    query="Boeing safety incident, recall, FAA investigation, lawsuit, quality control",
    sentiment="negative",
    reporting_voice=["Objective", "Analytical"],
    hours_back=72,
    historical=True,
    time_filter="pub_date",
    n_articles=20,
    return_type="dicts",
    premium=True,
)
```

## An industry, scoped to a region

Topic vocabulary as a string guarantee, region as a location entity
guarantee. Both must hold.

```python
LATAM = [
    "Location:Mexico", "Location:Brazil", "Location:Argentina", "Location:Colombia",
    "Location:Chile", "Location:Peru", "Location:Latam",
]

response = ask.news.search_news(
    string_guarantee=["meal kit", "meal kits", "recipe box", "meal subscription"],
    string_guarantee_op="OR",
    entity_guarantee=LATAM,
    entity_guarantee_op="OR",
    query="meal kit, recipe box, meal delivery kit, cook-at-home kit, food subscription",
    languages=["en", "es", "pt"],
    hours_back=720,
    historical=True,
    time_filter="pub_date",
    n_articles=50,
    return_type="dicts",
    premium=True,
)
```

## An industry event type: M&A

Event vocabulary as a string guarantee and categories to keep it on
business coverage.

```python
response = ask.news.search_news(
    query=(
        "M&A, mergers and acquisitions, acquisition, merger, SPAC, buyout, deal, "
        "transaction, definitive agreement, announced, closed, terminated, in talks, rumor"
    ),
    string_guarantee=["M&A", "merger", "acquisition"],
    string_guarantee_op="OR",
    categories=["Finance", "Business", "Technology"],
    page_rank=100000,
    languages=["en", "fr", "es", "de"],
    hours_back=24,
    time_filter="pub_date",
    n_articles=25,
    return_type="both",
    premium=True,
)
```

## Trade press only

```python
response = ask.news.search_news(
    query="semiconductor fab capacity, wafer starts, foundry pricing, advanced packaging",
    domain_url=["eetimes.com", "semiengineering.com", "digitimes.com", "anandtech.com"],
    hours_back=168,
    historical=True,
    n_articles=20,
    return_type="dicts",
)
```

## A theme with fuzzy boundaries

For a theme ("fashion trends", "celebrity outfits") there is no single
entity. Use a wide OR string guarantee for recall and let the query do
the ranking. Raise `similarity_score_threshold` to tighten.

```python
response = ask.news.search_news(
    query="fashion trends, fashion brands, runway shows, celebrity fashion, designer collections",
    string_guarantee=["fashion", "runway", "outfit", "outfits", "designer", "collection"],
    string_guarantee_op="OR",
    categories=["Entertainment", "Culture", "Business"],
    hours_back=48,
    time_filter="pub_date",
    method="kw",
    n_articles=50,
    return_type="dicts",
    premium=True,
)
```

## Share of voice across brands

`get_index_counts` with the same filters, one call per brand, gives a
comparable daily volume series.

```python
end = datetime.now(timezone.utc)
for brand in ["Nike", "Adidas", "On Running", "Hoka"]:
    counts = ask.news.get_index_counts(
        start_datetime=end - timedelta(days=14),
        end_datetime=end,
        entity_guarantee=[f"Organization:{brand}"],
        sampling="1d",
    )
    print(brand, [b.count for b in counts.root])
```
