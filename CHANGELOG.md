## 0.13.9 (2026-01-16)

### Fix

- Add index_urls endpoint

## 0.13.8 (2026-01-08)

### Fix

- Update Article object

## 0.13.7 (2025-12-03)

### Fix

- Route on DeepNews sync

## 0.13.6 (2025-12-02)

### Fix

- Add reverse_entity_guarantee

## 0.13.5 (2025-11-27)

### Fix

- Add claude 4.5 opus and gemini-2.5-flash

## 0.13.4 (2025-11-18)

### Fix

- Add ability to filter on author name

## 0.13.3 (2025-11-10)

### Fix

- Add png_url to chart response

## 0.13.2 (2025-11-09)

### Fix

- Charts and Reddit tools :tada: [+bug fix]

## 0.13.1 (2025-11-08)

### Fix

- Add claude 4.5 to forecast

## 0.13.0 (2025-11-07)

### Feat

- Add charts :tada:

## 0.12.5 (2025-10-22)

### Fix

- Remove unnecessary params

## 0.12.4 (2025-10-22)

### Fix

- Fix return type on index counts method
- Use correct path, handle datetimes correctly

## 0.12.3 (2025-10-18)

### Fix

- Add get_index_counts

## 0.12.2 (2025-10-09)

### Fix

- Diversify should be a float, not a bool

## 0.12.1 (2025-10-08)

### Fix

- Add claude 4.5 to deepnews :tada:

## 0.12.0 (2025-10-07)

### Feat

- Add API key support as alternative authentication method

### Fix

- Fix unit tests
- Fix typing throughout clients for better async, sync, and stream handling

## 0.11.32 (2025-09-21)

### Fix

- Pander to ancient python versions

## 0.11.31 (2025-09-21)

### Fix

- Pander to ancient python versions

## 0.11.30 (2025-09-21)

### Fix

- Add wikipedia :tada:

## 0.11.29 (2025-08-28)

### Fix

- Add bias to Article model

## 0.11.28 (2025-08-21)

### Fix

- Ensure o3-mini is available to forecast

## 0.11.27 (2025-08-20)

### Fix

- Ensure py3.9 typing

## 0.11.26 (2025-08-20)

### Fix

- Add gpt4.1, o3 to get_forecast

## 0.11.25 (2025-08-10)

### Fix

- Add websource option for alert tracking

## 0.11.24 (2025-08-08)

### Fix

- Update package classifiers and requires python

## 0.11.23 (2025-08-06)

### Fix

- Add pagination to live web search

## 0.11.22 (2025-08-04)

### Fix

- Use query for article_ids and add async

## 0.11.21 (2025-08-03)

### Fix

- Get multiple articles by their uuid

## 0.11.20 (2025-07-30)

### Fix

- Add X (twitter) tool to DeepNews

## 0.11.19 (2025-07-29)

### Fix

- Add wiki tool to deep_research

## 0.11.18 (2025-07-29)

### Fix

- Add domain controls to live_web_search

## 0.11.17 (2025-07-01)

### Fix

- Correctly handle error tokens in chat and deepnews streams

## 0.11.16 (2025-06-24)

### Fix

- Add support for claude 4 opus and o3

## 0.11.15 (2025-06-11)

### Fix

- Add countries_blacklist as an option

## 0.11.14 (2025-06-05)

### Fix

- Use python3.8 typing

## 0.11.13 (2025-06-05)

### Fix

- Add deepseek-r1-0528 and social_embeds

## 0.11.12 (2025-06-03)

### Fix

- add bad_domain_url

## 0.11.11 (2025-06-02)

### Fix

- Start returning asset lists with docs

## 0.11.10 (2025-05-12)

### Fix

- Replace poetry with uv
- pin poetry to 1.8.3 for python3.8 only
- pin poetry
- add keypoints to the Article object

## 0.11.9 (2025-05-02)

### Fix

- Add start_timestamp and stop_timestamp to autofilter response

## 0.11.8 (2025-04-28)

### Fix

- Allow more control over the internal context size

## 0.11.7 (2025-04-24)

### Fix

- Add support for gpt4.1 in alerts

## 0.11.6 (2025-04-20)

### Fix

- Allow graph source in deepnews

## 0.11.5 (2025-03-27)

### Fix

- add return_sources to async client

## 0.11.4 (2025-03-27)

### Fix

- Bump respx

## 0.11.3 (2025-03-21)

### Fix

- Allow users to blacklist domains

## 0.11.2 (2025-03-18)

### Fix

- allow llama3.3 70b as an alert model

## 0.11.1 (2025-03-09)

### Fix

- Fix lint
- Fix models and deep news methods
- avoid mutable defaults
- use an adapter for the final deepnews token
- Add discriminated union for deep news stream token and sources
- Add DeepNews endpoint

## 0.11.0 (2025-03-05)

### Feat

- Change default value for string_guarantee_op to 'OR' instead of 'AND' to match API

## 0.10.4 (2025-03-01)

### Fix

- allow gpt-4o as an alert model

## 0.10.3 (2025-02-17)

### Fix

- Add bluesky source

## 0.10.2 (2025-02-12)

### Fix

- Change language code for korean

## 0.10.1 (2025-02-09)

### Fix

- Remove exclude defaults that is preventing alert updates

## 0.10.0 (2025-02-06)

### Feat

- Add sources and move news into

## 0.9.2 (2025-02-06)

### Fix

- add o3-mini as forecast option

## 0.9.1 (2025-01-24)

### Fix

- Add logo_url to report

## 0.9.0 (2025-01-22)

### Fix

- Add expires_at to alerts
- Update alert log model
- Add more alert report models

## 0.8.0 (2025-01-22)

### Feat

- Add alerts endpoints

### Fix

- Add sync alert logs
- Update report request model
- Update report request model
- Update request params for alerts
- Add alert logs
- Move report to outer object
- Update description for cron
- Update request body for alerts and add dtos
- Add support for empty body (204 no content)
- Update request method of update alerts
- Typing fixes
- Typing fixes
- Use typing extension for annotated
- Add pydantic email validator
- Typing fixes
- Typing fixes
- Update payload dump method

## 0.7.58 (2025-01-03)

### Fix

- add continent to return value for article

## 0.7.57 (2025-01-03)

### Fix

- autofilter response type
- Make autofilter function async

## 0.7.56 (2025-01-03)

### Fix

- Update typing of list

## 0.7.55 (2024-12-20)

### Fix

- add autofilter feature

## 0.7.54 (2024-12-09)

### Fix

- add -latest tag to claude 3.5, add llama 3.3 70b

## 0.7.53 (2024-12-01)

### Fix

- allow search on premium sources

## 0.7.52 (2024-11-17)

### Fix

- allow users to filter on pub_date or crawl_date

## 0.7.51 (2024-11-01)

### Fix

- add geocoordinates :tada:

## 0.7.50 (2024-10-20)

### Fix

- Add rate and concurrency limit errors

## 0.7.49 (2024-10-20)

### Fix

- Add py.typed file to package

## 0.7.48 (2024-10-16)

### Fix

- no longer require query for graph build

## 0.7.47 (2024-10-07)

### Fix

- add ability to control string/entity operators

## 0.7.46 (2024-10-07)

### Fix

- allow query-less filtering + streaming

## 0.7.45 (2024-10-02)

### Fix

- ensure reporting_voice can be a list or string

## 0.7.44 (2024-09-22)

### Fix

- allow users to pass filter_param to get_chat_completion

## 0.7.43 (2024-09-17)

### Fix

- add o1 models

## 0.7.42 (2024-09-16)

### Fix

- add gpt-4o-mini

## 0.7.41 (2024-09-16)

### Fix

- use supported typing

## 0.7.40 (2024-09-16)

### Fix

- add live_web_search endpoint

## 0.7.39 (2024-09-04)

### Fix

- bump httpx

## 0.7.38 (2024-09-04)

### Fix

- allow expert definition on get_forecast
- allow expert definition on get_forecast

## 0.7.37 (2024-09-03)

### Fix

- allow docs_upload, change name for constrained_disamb, add visualize_with option, improve GraphResponse

## 0.7.36 (2024-08-30)

### Fix

- allow domain_url to be a list, allow filtering on sentiment

## 0.7.35 (2024-08-28)

### Fix

- linting and README
- linting and README

## 0.7.34 (2024-08-28)

### Fix

- add mega-news-knowledge-graph endpoint :tada:

## 0.7.33 (2024-08-08)

### Fix

- add knowledge graphs, allow filtering on countries, languages, continents

## 0.7.32 (2024-08-06)

### Fix

- typing

## 0.7.31 (2024-08-06)

### Fix

- improve the typing on forecast return

## 0.7.30 (2024-07-08)

### Fix

- use old types for old python versions

## 0.7.29 (2024-07-08)

### Fix

- add more return values to ForecastResponse

## 0.7.28 (2024-07-06)

### Fix

- add web_search functionality

## 0.7.27 (2024-07-05)

### Fix

- add probability to return object for forecast

## 0.7.26 (2024-07-04)

### Fix

- add string_guarantee/reverse_string_guarantee/entity_guarantee

## 0.7.25 (2024-06-29)

### Fix

- make sure the reddit param is correcT

## 0.7.24 (2024-06-29)

### Fix

- add reddit option to get_forecast

## 0.7.23 (2024-06-29)

### Fix

- add params to search_reddit

## 0.7.22 (2024-06-27)

### Fix

- use old python types

## 0.7.21 (2024-06-27)

### Fix

- use old python types

## 0.7.20 (2024-06-27)

### Fix

- use old python types

## 0.7.19 (2024-06-27)

### Fix

- add search_reddit, add command-nightly to forecast

## 0.7.18 (2024-06-26)

### Fix

- ensure scopes are set by default

## 0.7.17 (2024-06-25)

### Fix

- make sure reddit threads can be lists or strings

## 0.7.16 (2024-06-25)

### Fix

- add conversational awareness to chat completions

## 0.7.15 (2024-06-23)

### Fix

- add cutoff_date to get_forecast

## 0.7.14 (2024-06-23)

### Fix

- allow gpt4o and claude-35 to sync and async chat

## 0.7.13 (2024-06-22)

### Fix

- make cryptography more flexible

## 0.7.12 (2024-06-21)

### Fix

- typing

## 0.7.11 (2024-06-21)

### Fix

- update forecast parameters

## 0.7.10 (2024-06-20)

### Fix

- update forecast response to include choice

## 0.7.9 (2024-06-19)

### Fix

- add confidence to forecast return object

## 0.7.8 (2024-06-18)

### Fix

- tests

## 0.7.7 (2024-06-18)

### Fix

- support python 3.9 types

## 0.7.6 (2024-06-18)

### Fix

- add forecast endpoint, bump httpx

## 0.7.5 (2024-06-08)

### Fix

- add strategy and hours_back params

## 0.7.4 (2024-06-06)

### Fix

- add 'diversity_sources' option to SDK

## 0.7.3 (2024-06-06)

### Fix

- Fix typing in graph relationships dto
- Fix typing in story response dto
- Fix typing in sentiment response dto
- Change match statements to if to support 3.8
- Handle 401 code in OAuth2ClientCredentials to retry getting new token
- Remove user param from chat api

## 0.7.2 (2024-06-05)

### Fix

- ensure user is passed for async too

## 0.7.1 (2024-06-05)

### Fix

- add user to sdk chat args

## 0.7.0 (2024-06-05)

### Feat

- Allow passing additional http headers in API methods, fix many docstrings, and update unit tests
- Add unit tests and small fixes to security
- Refactor auth handling to be more streamlined and reduce dependencies

### Fix

- Add concrete return type for chat headline questions method
- Fix response streaming in client
- Fix content type handling in APIResponse
- Improve get_chat_completions stream handling and fix parameters
- Improve error handling with attached response and fix some typing issues
- Refactor base client and remove API request object to simplify
- Fix get article method in NewsAPI and switch to ArticleResponse object

## 0.6.11 (2024-06-05)

### Fix

- allow floats for sentiment

## 0.6.10 (2024-06-02)

### Fix

- default to fastest return_type 'string'

## 0.6.9 (2024-05-31)

### Fix

- update the graph relationships

## 0.6.8 (2024-05-23)

### Fix

- README
- ruff
- ruff
- add relationships to the StoryResponse model
- use gpt4-1106 preview for now
- improve filtering

## 0.6.7 (2024-05-21)

### Fix

- ruff

## 0.6.6 (2024-05-21)

### Fix

- ruff

## 0.6.5 (2024-05-21)

### Fix

- ruff
- sources endpoint

## 0.6.4 (2024-05-21)

### Fix

- allow filtering on reporting voice and domain_url

## 0.6.3 (2024-05-18)

### Fix

- allow hybrid search, add provocative param

## 0.6.2 (2024-05-14)

### Fix

- **deps**: downgrade httpx

## 0.6.1 (2024-05-11)

### Fix

- add union typing for article_id

## 0.6.0 (2024-05-11)
