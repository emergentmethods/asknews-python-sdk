# Exact-domain distribution Excel report

Standalone read-only Python **3.10+** utility, default domain `apnews.com`.
Select an explicit **inclusive `--start` / exclusive `--stop`** range, or use
`--month YYYY-MM` as an optional, mutually exclusive shorthand. There is no
implicit date range. No SDK runtime, release, permission or production changes
are needed to run the utility. Development and tests use synthetic data only.

Reference: [Publisher Analytics](https://docs.asknews.app/en/publisher), including
its rendered Python Recipes 1–4, re-read **2026-10-10**, and the
[API reference](https://docs.asknews.app/en/reference#tag--distribution).

## Install and safe commands

Keep the script and requirements together; use your existing authorized local
credentials. Never put credentials in CLI arguments, source, chat or shell history.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt

# Test one week first: Sep 1 inclusive through Sep 8 exclusive, UTC.
python distribution_report.py --domain apnews.com --start 2026-09-01T00:00:00Z --stop 2026-09-08T00:00:00Z --output apnews-sep01-07.xlsx

# All September (same precision caveats below).
python distribution_report.py --domain apnews.com --start 2026-09-01T00:00:00Z --stop 2026-10-01T00:00:00Z --output apnews-september.xlsx

# Equivalent month shorthand; do not combine with --start or --stop.
python distribution_report.py --domain apnews.com --month 2026-09 --output apnews-month.xlsx
```

Windows activation: `.venv\Scripts\activate`. Files must be new `.xlsx` paths
in a private directory. Atomic no-overwrite publication requires hard-link
support; the temporary/output file has restrictive POSIX permissions where
supported. Existing files are never overwritten, including a concurrent creator.

Add `--include-internal` **only with already-authorized internal scope** to request
the existing optional dashboard sections. Add `--allow-partial` only if you want
a flagged workbook despite failed/missing sections (exit 2). Neither flag grants
access. The week command does not request any unrelated whole-month analytics.

### Authentication

Set privately via your existing local secret manager/session, choosing one:

- `ASKNEWS_API_KEY`: the guide uses an existing **publisher organization key**
  (`ank_org_...`) with `distribution` and `news` scopes. Personal keys cannot
  access distribution; ownership/admin status does not change that.
- `ASKNEWS_CLIENT_ID` + `ASKNEWS_CLIENT_SECRET`: SDK OAuth alternative for an
  already-authorized client. `ASKNEWS_SCOPES` is an optional space-separated
  subset of `distribution news internal`, default `distribution news`.
  Admin status does **not** imply internal scope.

These environment names are utility adapters, not automatic SDK environment
loading. No credentials are created, read from other sessions, or modified.
No custom host, token URL, impersonation header or credential CLI is offered.
SDK default production hosts, TLS verification and disabled redirects apply.
Data calls are GETs; OAuth may POST to the SDK token endpoint. Errors are sanitized;
no raw bodies, credentials or HTTP debugging are emitted.

Public ranking 401/403 aborts with no workbook. Any 401, including token exchange
or article enrichment, is fatal: no retry or SDK OAuth-refresh loop. A 403 is
never retried; a denied internal request stops that group without probing the
remaining endpoints. Optional-section denials are unavailable, never zero.

## Range semantics and limitations

- Require both ISO8601 calendar datetimes with seconds and explicit `Z` or
  `±HH:MM` offset; normalize to **UTC before validation or any requests**.
  Reject naive/date-only/invalid input, nonzero fractional seconds, stop <= start,
  mixed month/range options and missing bounds. Whole-second precision is the
  supported input contract; no silent rounding or expansion to a month.
- Only one UTC calendar month is supported. The inclusive integer end is
  **exclusive stop minus one second** and must be in the start's UTC month.
  Thus Sep 1–Oct 1 midnight works, but Sep 1–Oct 1 00:00:01 does not.
  Cross-month weighted-share aggregation is deliberately not invented.
- Inclusive integer-second server filters cannot represent a truly half-open
  continuous-time range: events **after stop - 1s and before stop are omitted**.
  For September the API bounds are `1788220800..1790812799`; the final fractional
  second is not covered. The workbook and console never claim exact completeness.
- Rankings, weighted share, internal aggregates and their daily series all use
  these same selected bounds. Distribution dates are **event times**, not article
  publication dates. Server daily buckets are accepted for intersecting UTC dates,
  including clipped first/last days. Database bucket timezone is assumed UTC,
  not live-verified. No daily query overlap or daily-share averaging is used.
- The two internal distinct routes accept **year/month only**. For partial months,
  neither route is called: monthly and daily distinct cells stay blank, and
  Coverage explicitly says unsupported. This expected limitation alone does not
  force exit 2. No whole-month values are labelled weekly, no sum of daily uniques
  is presented as range unique. Full-month requests retain both original routes
  and reconcile their response fields/totals; monthly distinct remains independent.
- Index requests use **crawl_date**, not event/publication date, clipped to each
  intersecting UTC day: `[clipped start, clipped stop - 1s]` inclusive. This repeats
  the fractional gap at **every daily stop**, avoiding adjacent inclusive overlap.
  A one-second clipped segment has equal server endpoints and cannot produce an
  index bucket; no request is sent, its cell stays blank and the run is partial.
  Missing/naive/shifted buckets are unavailable. Counts describe the **current
  retained index**, not an immutable historical inventory. Backend hot/archive
  combination or masked partial failures prevent proof of completeness.
- Enrichment looks up only the UUID union of valid rows from the selected event
  rankings. `/v1/news` has no date filter: an older article used during the range
  correctly retains its older publication date. Do not filter away those events.
  Missing retained-index articles/metadata stay blank and never erase event counts.

No shared snapshot exists across sections/pages. Cache TTLs, late events,
backfills and offset changes can cause drift; checks catch some, not all of it.
Pagination exhaustion does not prove immutable completeness.

## SDK methods and honest transport fallbacks

Pinned **asknews 0.14.6**; no SDK upgrade/release is needed for this correction.

| Operation | Implementation and rationale |
| --- | --- |
| Article enrichment (Recipe 4) | **`sdk.news.get_articles(article_ids=batch, full_text=False)`**, one batch per <=100 unique IDs; actual named SDK method, not a locally invented SDK wrapper |
| Rankings/share (Recipes 1–3) | `sdk.client.request(...).content`, exactly the guide's authenticated transport; no named helpers in 0.14.6 |
| Internal aggregate/daily metrics | Narrow transport fallback: existing `sdk.distribution.get_domain_metrics` and `get_domain_metrics_timeseries` DTOs silently drop `grounded`/`total_grounded` |
| Internal monthly/daily distinct | Transport: no named helpers; year/month-only contract, full-month requests only |
| Index counts | Transport preserves explicit UTC offsets; named `sdk.news.get_index_counts` serializes datetimes without offsets |

There are no duplicate named-plus-transport calls just to demonstrate methods.
Transport is fixed-allowlist SDK transport, not an independent HTTP client or
private SDK access. Named enrichment shares the same hooks, retries and budgets.
The guide's broad “traffic share” language does not expose service weighting:
this workbook calls it **weighted share**, never raw-event percentage or payout.
Rank metric selector `surface|citation|grounded` and index counts are reference/
source-verified extras; internal dashboard routes require existing internal scope.
No assertion is made that every deployed credential has access to these routes.

## Workbook

| Sheet | Contents |
| --- | --- |
| Summary | Selected UTC bounds, raw aggregates if authorized, exported event sums, monthly distinct only where supported, sum of available clipped index windows |
| Daily metrics | Range-filtered daily events if authorized, optional full-month daily distinct, separate clipped crawl-date index counts; missing cells blank |
| Articles | UUID and literal ranking URL; joined retrieval/citation/grounding counts; **title, eng_title, pub_date, language, country, classification, sentiment, entities, keywords, reporting_voice, provocative, page_rank, key_points, bias, content_type**, enrichment status |
| Weighted share | Selected range's exact-domain server weighted fraction, not money |
| Coverage | Exhaustion/caps/errors, unsupported sections, send counts and limits |
| Methodology | Source links, precise bounds, UTC acquisition timestamps and caveats |

Enrichment is joined by **UUID**, not return order/title/URL, and validates both
article URL host and metadata `domain_url` against the exact requested domain.
Unknown/duplicate IDs or foreign/subdomain URLs discard the entire batch; prior
valid batches survive as flagged partial data. No foreign metadata is exported.
Missing IDs mark partial; absent optional fields stay blank. List/object values
are literal JSON. No full-text bodies are fetched or exported.

All text cells are literal—even `=`, `+`, `-`, `@` and URLs—with no formulas,
hyperlinks or external workbook links. Control characters are removed and Excel
cell limits applied. No consumer identities, prompts, raw hits, billing data or
raw response dumps are fetched/exported. One bare exact domain is sent; no fuzzy,
wildcard or parent-domain matching. Aggregate isolation relies on the verified
server domain filter because responses have no domain labels.

Missing article metrics are zero **only after that positive-event ranking
exhausts**; otherwise blank. Duplicate ranking IDs/pages are not summed and
conflicting UUID URLs fail export. `total_count` is the **page event sum**, not a
domain total. Both daily distinct row fields and response totals are validated;
`total_surfaced` reconciles daily uniques only, never replaces monthly distinct.

## Bounded requests and precise counts

For a successful collection without retries:

**Data sends = P_surface + P_citation + P_grounded + 1 + I × (2 + 2F)
+ ceil(U / 100) + D**

- `P_metric`: pages actually needed for that ranking (including a terminal empty
  page when supplied; empty rankings still cost one request).
- `1`: weighted-share call.
- `I`: 1 with `--include-internal`, else 0; `F`: 1 for a full UTC month, else 0.
  Two date-range aggregates remain available for partial-month requests; the
  two monthly-only distinct calls are added only for a full month.
- `U`: number of **unique validated UUIDs across all three rankings**. Zero IDs
  means zero enrichment calls; batches are not repeated per metric.
- `D`: number of clipped UTC-day index windows of **at least two seconds**.
  Usually 7 for the week or 30 for September; partial days count as windows.
  One-second clips are skipped/flagged as described above.

Actual HTTP sends additionally include **OAuth token sends + extra retry sends**.
Failures/denials/caps can stop sections early; this is not a promise all planned
calls will happen. With one page per metric and 1–100 unique IDs: week **12**
public / **14** internal data sends; September **35** public / **39** internal.

Defaults: page size 100, max 100 pages **per metric**, **400 total HTTP sends**,
**2400 seconds request-start budget**, 30-second individual HTTP operation timeout.
Explicit bounded flags: `--page-size 1..100`, `--max-pages 1..1000`,
`--max-requests 1..4000`, `--max-seconds 1..3600`.
Enrichment now consumes budget too; high-UUID walks may need explicitly larger
limits even when rankings fit. No unrestricted all-history or per-article fanout.

All calls are serial. Every distribution send waits **6 seconds** (guide limit
0.2 req/s, burst 5, concurrency 2); other/news/auth sends wait 1 second. Transient
408/429/500/502/503/504 or transport failures get at most three attempts total.
Retry-After seconds/HTTP dates establish **reader-wide not-before state**, including
on the last retry, across enrichment, index, distribution and OAuth sends.
Invalid/negative/unusable headers, waits >60 seconds or exhausted request/time
budgets permanently stop all further sends. No section can reset that state.
In-flight operations can finish after the request-start deadline; use an external
process timeout if a hard wall-clock limit is required.

Exit **0** means collected with documented precision/snapshot/unsupported-section
caveats, not exact completeness. **2** means flagged partial output explicitly
allowed by `--allow-partial`. **1** means failure/no new workbook. Inspect Coverage
before interpreting any sums as totals; partial sums describe exported data only.

## Offline tests

```bash
python -m pip install 'pytest>=8,<10'
python -m pytest test_distribution_report.py -q
```

Tests forbid sockets and exercise real SDK methods with MockTransport: named
helper invocation/batches, UUID/domain validation and partial enrichment,
week/month/offset/partial-day ranges, invalid inputs before credentials/network,
monthly-only omissions, pacing/backpressure and caps including OAuth/news,
prior pagination/distinct regressions, workbook reopening, injection/no links,
missing versus zero, no false totals and atomic no-overwrite.
No live extraction or real AP workbook is included. Optional example dependencies
and tests are not added to the SDK package or its CI workflows.
