# DeepNews inline source-batch fixtures

Recorded `/v1/chat/deepnews` SSE payloads (one JSON chunk per line), copied verbatim
from `asknews/chat-service` `tests/fixtures/research_canvas/` at commit
`4fe4a794e28de715a2801c82c7394bd2d87de741` (`stream_sources_inline=true`, engine
v2.0) via `asknews/api` !450. Only each payload's top-level `id`/`created` is a
placeholder.

- `serial_v2_stream.jsonl` — two serial `search_news` calls; the second re-finds
  `news:2` (listed in `source_ids`, not re-sent in `sources`).
- `mixed_kind_wiki_v2_stream.jsonl` — a web and a news source sharing one URL get
  distinct ids (`web:1`, `news:2`); `search_wikipedia` calls stream `kind: "wiki"`
  with `web` entries.

Refresh by copying the files from chat-service and bumping the commit above.
