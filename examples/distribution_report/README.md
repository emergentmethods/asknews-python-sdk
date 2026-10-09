# Exact-domain distribution Excel report

Standalone, read-only Python **3.10+** example. Defaults: `apnews.com`, `2026-09`.
Run locally with **your existing authorized credentials**. No credential or
permission changes, customer extraction, or live authorization tests were made
to develop this example. Tests use synthetic responses only.

Primary reference: the official [Publisher Analytics guide](https://docs.asknews.app/en/publisher)
and its [linked API reference](https://docs.asknews.app/en/reference#tag--distribution),
read with the live Python recipes on 2026-10-09. See the guide/source comparison below.

## Install and run

Keep `distribution_report.py` and `requirements.txt` together (or enter this
example directory in a checkout):

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python distribution_report.py --domain apnews.com --month 2026-09 --output apnews-2026-09.xlsx --include-internal --allow-partial
```

On Windows use `.venv\Scripts\activate` instead. Output must be a new `.xlsx`
path; existing files are never overwritten. Save in a private local directory.
The temporary/output workbook uses restrictive permissions where the OS supports
POSIX modes. Filesystems must support hard links for atomic no-overwrite output.

**Credentials:** provision the environment privately using your existing local
secret manager/session; do not put secrets in command arguments, source files,
chat, or shell history. This script reads one of:

- `ASKNEWS_API_KEY`, passed to the SDK's `api_key` parameter. The publisher guide
  uses an **existing publisher organization key** (`ank_org_...`) with
  `distribution` + `news` scopes. **Personal API keys cannot access distribution**;
  ownership/admin privileges do not turn a personal key into a publisher key; **or**
- `ASKNEWS_CLIENT_ID` + `ASKNEWS_CLIENT_SECRET`, passed to the SDK's OAuth client
  credentials parameters. Optional `ASKNEWS_SCOPES` is a space-separated subset
  of `distribution news internal`; default `distribution news`. Request only
  scopes the existing client already has. The script does not grant scopes.
  OAuth is an additional source-verified SDK/admin authentication option, not
  the publisher guide's organization-key recipe; it still needs endpoint and
  exact-domain authorization. Do not create or change credentials to run this example.

These environment names are this example's adapter, not automatic SDK environment
loading. Do not set both authentication methods. No custom host, token URL,
organization impersonation headers, or credentials-on-CLI options are provided.
TLS verification stays enabled, redirects are disabled, and the SDK uses its
normal production API/auth hosts. All analytics requests are GET; SDK OAuth may
POST to its token endpoint. Request/response bodies, identities and credentials
are never logged. Do not enable HTTP debugging.

`--include-internal` tries dashboard metrics with the same existing credentials.
**Admin status does not imply `internal` scope.** Omit the flag for the public
ranking/share plus news index report. A 403 stops the internal group immediately;
there is no loop probing its remaining endpoints. Public ranking 401/403 stops
the entire run without a workbook. Any 401 (including OAuth) is fatal without a
retry or credential-refresh loop. Optional-section 403s mark that section
unavailable; they are never retried or represented as zero. Use an already
suitably authorized credential or accept the documented gap—not an access change.

### Exit codes and bounded requests

- **0**: selected sections collected, **with calendar/snapshot coverage caveats**.
  Does not mean an exact complete month or that internal sections were requested.
- **2**: a flagged partial workbook was saved with `--allow-partial`.
- **1**: fatal error or incomplete sections without `--allow-partial`; no new
  workbook. Errors are deliberately sanitized. Inspect a flagged workbook's
  Coverage sheet for section-specific failures, then address the identified
  cause before rerunning.

Defaults: page size **100**, at most **100 pages per metric**, **400 HTTP sends**
(including OAuth/retries), **2400 seconds** of request-start/retry budget,
30-second HTTP operation timeout, serial requests with **6 seconds before every
distribution send** (including retries and admin/internal requests) and 1 second
before other/news/auth sends. This follows guide Recipe 3 and stays below the
published **0.2 distribution requests/second** limit (burst 5, concurrency 2).
The longer bounded default budget accommodates the slower polite pagination.
A request already in flight may finish after the overall deadline;
httpx timeouts bound individual network operations, not a strict wall-clock
process deadline. Set an external process timeout if required.

Optional bounded flags: `--page-size 1..100`, `--max-pages 1..1000`,
`--max-requests 1..4000`, `--max-seconds 1..3600`. API/transport transient failures
retry at most twice (three attempts total); retryable statuses are
408/429/500/502/503/504. `Retry-After` seconds and HTTP dates set a **reader-wide
not-before deadline**, including on the final failed attempt of a section.
Every later send (other metrics, share, internal, index or OAuth) must honor that
deadline as well as its normal pacing; a section boundary never resets it.
A wait over 60 seconds, unusable/negative Retry-After, or exhausted request/time
budget **permanently stops all further sends for the run**, not just the current
section. Remaining sections are recorded unavailable/partial without network
requests. Previously collected data can only be saved via `--allow-partial`
(exit 2); otherwise no workbook is written. No concurrency or article-by-article fanout. Index
counts cost one additional bounded request per day (28–31). Request limits
include unsuccessful sends; no unrestricted all-history queries.

## Workbook and interpretation

| Sheet | Contents |
| --- | --- |
| Summary | Raw event aggregates when authorized, exported article sums, distinct retrieval articles when authorized, exported indexed-day count sum, explicit coverage status |
| Daily metrics | Server-grouped retrieval/citation/grounding/full-text events when authorized; daily unique retrieval articles; separate crawl-date index counts |
| Articles | Stable article UUID, literal URL, joined retrieval/citation/grounding counts |
| Weighted share | Exact-domain server weighted fraction formatted as percent; **not payout** |
| Coverage | Availability, pagination completion/caps, failure and reconciliation notes |
| Methodology | Requested and actual bounds, UTC acquisition timestamps, SDK/API behavior and limitations |

Text cells are explicitly literal, including strings beginning with `=`, `+`,
`-`, `@`, and URLs; no formulas, hyperlinks or external workbook links are
created. Sheets have frozen headers, filters, widths and readable count/percent
formats. Missing fields/days are **blank/unavailable**, not zero. Zero is retained
when the server returns it; an absent article metric is zero only when that
positive-event ranking has exhausted pagination. A page's `total_count` is its
**event sum**, not a domain total or article count. Rankings are independently
paginated and joined by UUID, never by title or URL; conflicting UUID URLs fail
the export. Duplicate IDs/repeated pages are not summed. An exact page boundary
may require a final empty page. Old servers without explicit `page`/`next_page`
metadata are marked partial/unavailable rather than falsely reporting their
potentially top-N-capped cohort as complete.

The daily distinct response requires `hits` and `surfaced` on every returned
row plus both `total_hits` and `total_surfaced`. Missing fields remain blank;
missing/invalid fields or totals mark the internal group partial/unavailable and
require `--allow-partial` (exit 2), never an unflagged successful export.
`total_surfaced` reconciles the **sum of daily distinct counts only**.
Monthly distinct article counts must **not** be computed by summing daily
uniques; the independent monthly `surfaced` value is preserved. Index counts
describe current retained indexed articles filtered by
**crawl date**; they are not distribution events, publication-date activity,
or a historical inventory snapshot. Ranking endpoints do not supply titles,
publication dates, bias/sentiment or other enrichments: those are not collected
by this event-count example. The guide's Recipe 4 supports these via a separate
batched article lookup (see below); they are not unsupported API features.
This example performs no additional article enrichment fanout. Consumer identities, prompts,
queries, raw hits and billing/PII endpoints are never requested or exported.

Only the requested exact domain is sent in filters. URLs with a different host
(including `www.` or other subdomains), embedded credentials, or nonstandard
ports cause the page to be discarded and flagged; returned share rows must match
exactly. Aggregate endpoints have no domain label in their response: isolation
there relies on their verified exact-domain filter contract. No parent-domain,
fuzzy or wildcard matching and no other publisher rows are exported.

### Dates: important September limitation

September 2026 is requested as `[2026-09-01T00:00:00Z, 2026-10-01T00:00:00Z)`.
Distribution queries accept integer seconds and compare both endpoints
inclusively. The script sends **1788220800 through 1790812799**, i.e.
`2026-09-30T23:59:59Z` inclusive. It **cannot include fractional-second events
after that instant**. Sending next-month midnight would both include an unwanted
instant and conflict with the public same-month restriction. Admin exemptions
are not used to pretend this is an exact half-open month. The warning is present
in every workbook and successful console output.

Distribution dates are **event timestamps**, not article publication dates.
Daily distribution metrics use one monthly request grouped on the server, not
adjacent inclusive daily queries. Server bucket labels are treated as UTC; the
deployed database's timezone cannot be verified by this client.

The index service's daily split can use adjacent inclusive endpoints. To avoid
double counting boundaries, this example requests each day separately from UTC
00:00:00 to 23:59:59 and validates the returned aware timestamps. Consequently
**index counts exclude the fractional remainder of EVERY day's final second**.
The retained-index backend can also combine recent hot/archive data or conceal
partial backend failures; client-side exact completeness is not established.
Missing/shifted/naive buckets are unavailable, never guessed or silently shifted.

Requests have no shared database snapshot. Late events, cache TTLs, corrections
or backfills can move ranking offsets and change totals during acquisition.
Duplicate/page guards and ranking-vs-aggregate/daily reconciliation catch some,
not all, drift. Pagination exhaustion does not prove immutable completeness.
Weighted share reflects the server's current metric weights and publisher
multipliers for the selected period; weights/pool values are not exposed by this
response. **No revenue, payout, currency or dollar amount is inferred.**

## Publisher guide / source cross-check

- **Recipes 1–3 match:** `AskNewsSDK(api_key=...)`, authenticated
  `sdk.client.request(...)`, `response.content`, exact domain names, same-UTC-month
  integer dates, page size <=100, 1-based page/next_page, page-only event sums and
  an optional empty final page. The script also guards caps/duplicates/drift.
- **Rate correction:** the guide and API configuration say **0.2 req/s**, not
  1 req/s. This example now follows the guide's six-second distribution delay.
  The guide's deterministic tie ordering does not create a transactional snapshot.
- **Share wording:** the guide calls `hit_share` a share of publisher traffic.
  Inspected service code applies metric weights and publisher multipliers. The
  workbook therefore says **weighted share**, never unweighted event percentage
  or dollars; it cannot reconstruct weights from this response.
- **Metrics not listed in the guide's parameter table:** the linked public
  API reference (version **0.32.4** when checked) includes
  `metric=surface|citation|grounded` on article rankings. Retrievals are `surface`
  events, citations and groundings are independent event counts, not publication
  counts. Internal raw models also have `full_text`, which is a separate metric.
- **Public versus internal:** the guide FAQ explicitly excludes dashboard-only
  daily/query/domain lookup endpoints from the public API. The linked schema
  confirms `distribution` + `internal` on the optional metric/unique routes;
  neither the guide's organization-key recipe nor admin status promises access.
- **Index counts:** not one of the guide's three recipes. The linked reference
  exposes `/v1/index_counts` with `news` scope, and inspected publisher-key
  allowlist explicitly includes it. This source-verified extra is still
  deployment/authorization-dependent; denial is recorded, not bypassed.
- **Recipe 4 is supported, but deliberately not requested:** verified SDK method
  `sdk.news.get_articles(article_ids: List[str] | List[UUID], full_text=False)`
  returns `List[ArticleResponse]` and GETs `/v1/news`. The guide batches at 100 IDs
  for title, publication metadata, classification, sentiment and reporting voice.
  This scoped event-count report does not fetch that additional metadata, entities,
  summaries or article bodies, even in batches. Its article sheet is IDs/URLs/counts;
  do not interpret absent metadata as an API/SDK limitation. No high-cost per-article fanout.
- **Date completeness:** the guide's examples use integer timestamps and do not
  establish fractional-second month-end coverage; the source's inclusive bounds
  and this report's explicit coverage warnings remain necessary.

The guide links are also recorded as **literal text** in each workbook's
Methodology sheet. No guidance here changes existing permissions, SDK/API
functionality or production settings.

## Verified SDK/API compatibility

Verified SDK source: `asknews==0.14.6`, commit
`77e434f3e08aa9372aed8fb4b72c3044a677b6a6`.

- `AskNewsSDK(api_key=...)` or `(client_id=..., client_secret=..., scopes=...)`
  and its supported httpx `event_hooks` constructor kwargs provide auth,
  safe errors, throttling and request budgets.
- `sdk.distribution.get_domain_metrics(domain_names, start_date, end_date)` and
  `get_domain_metrics_timeseries(...)` exist. Their current Pydantic models
  omit `grounded`/`total_grounded` and would silently discard these fields.
- Ranking/share/unique aggregates have no named distribution wrappers.
- `sdk.news.get_index_counts(start_datetime, end_datetime, ..., domains=...)`
  exists, returning `IndexCountsResponse.root` with `start/end/count` rows,
  but its formatter drops the datetime timezone offset.

For those reasons the example consistently uses the SDK's supported
**`sdk.client.request(method="GET", endpoint=..., query=...).content`** transport
with a fixed endpoint allowlist. It retains SDK authentication and serialization;
there is no direct `requests`, `httpx` client, curl fallback, SDK/API extension,
or private client member access. `httpx` types are used only for the SDK's
supported hooks and exceptions. The example never requests an alternate server.

| SDK transport endpoint | Scope / contract |
| --- | --- |
| `/v1/distribution/articles/top_n_for_domains` | `distribution`; exact `domain_names`, integer dates, `metric=surface/citation/grounded`, `limit<=100`, 1-based `page`; `data` article IDs/URLs/raw counts, page sum, next page |
| `/v1/distribution/stats/hit_share` | `distribution`; exact domain, same dates, `is_publisher=true`; domain weighted fractions |
| `/v1/distribution/stats/metrics` | `distribution` + `internal`; raw surfaces/citations/grounded/full_text |
| `/v1/distribution/stats/metrics_timeseries` | same internal scope; day rows and metric totals |
| `/v1/distribution/articles/domain_hits_surface` | same internal scope; year/month; raw hits and monthly distinct surfaced articles |
| `/v1/distribution/articles/domain_hits_surface_timewindow` | same internal scope; daily hits/distinct; daily distinct sum is not monthly distinct |
| `/v1/index_counts` | `news`; exact domains, aware ISO start/end, `sampling=1d`, `time_filter=crawl_date`; index bucket counts |

These are source-verified contracts, not evidence that any particular credential
or deployed version can use them. Endpoint/schema mismatch, missing additive
fields, pagination guards and API caps are explicit partial/unavailable outcomes.

## Offline tests

From this directory, after installing requirements:

```bash
python -m pip install 'pytest>=8,<10'
python -m pytest test_distribution_report.py -q
```

Fixtures and httpx MockTransport exercise the **real SDK** without network or
real credentials. Tests cover pagination, repeated/capped pages, metric joining,
leap/year/UTC boundaries, exact-domain rejection, 401/403, retries/budgets,
missing fields, daily reconciliation, formula injection, workbook reopening,
totals, output collision and partial exit behavior. Reviewer regressions cover
cross-section/final-attempt Retry-After, unusable headers, exhausted wait/request
time budgets, missing daily distinct fields/totals, explicit partial CLI behavior,
and preserving monthly distinct counts when daily distinct counts overlap.
No real AP workbook or data
is included. Tests live with this optional example to avoid adding Excel
runtime/dev dependencies to the SDK package or changing its release workflows.
