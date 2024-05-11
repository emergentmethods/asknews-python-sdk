from collections.abc import Iterable
from typing import Any, List, Optional, Tuple
from urllib.parse import urlencode, urljoin

import orjson


def serialize(data: Any) -> bytes:
    return orjson.dumps(data)


def deserialize(data: bytes) -> Any:
    return orjson.loads(data)


def build_accept_header(accepted_types: List[Tuple[str, float]]) -> str:
    accept_strings = []
    for content_type, quality in accepted_types:
        quality = f"; q={quality}" if quality < 1.0 else ""  # type: ignore
        accept_strings.append(f"{content_type}{quality}")
    return ", ".join(accept_strings)


def build_url(
    base_url: str,
    endpoint: str,
    query: Optional[dict] = None,
    params: Optional[dict] = None,
) -> str:
    params = {k: str(v) for k, v in (params or {}).items()}
    path = endpoint.format(**params)
    url = urljoin(base_url, path)

    if query:
        query_parts = []
        for k, v in query.items():
            if v is None:
                continue
            if isinstance(v, Iterable) and not isinstance(v, str):
                query_parts.extend([(k, str(item)) for item in v])
            else:
                query_parts.append((k, str(v)))
        url += "?" + urlencode(query_parts, doseq=True)

    return url


def determine_content_type(body: Any) -> str:
    if hasattr(body, "content_type"):
        return body.content_type
    elif isinstance(body, bytes):
        return "application/octet-stream"
    elif isinstance(body, (dict, list, tuple, set, frozenset, str, int, float, bool)):
        return "application/json"
    else:
        return "text/plain"
