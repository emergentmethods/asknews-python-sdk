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
