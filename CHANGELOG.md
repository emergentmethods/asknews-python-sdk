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
