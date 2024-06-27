from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, RootModel
from typing_extensions import Annotated

from asknews_sdk.dto.base import Article, BaseSchema
from asknews_sdk.dto.stories import RedditThread


class SearchResponseDictItem(Article):
    as_string_key: Annotated[str, Field(title="As String Key")]


class SearchResponse(BaseSchema):
    as_dicts: Annotated[Optional[List[SearchResponseDictItem]], Field(None, title="As Dicts")]
    as_string: Annotated[Optional[str], Field(None, title="As String")]
    offset: Annotated[Optional[int], Field(None, title="Offset")]


class SourceReportItem(BaseModel):
    bson_date: Annotated[datetime, Field(title="Bson Date")]
    n_bucket: Annotated[int, Field(title="N Bucket")]
    n_selected: Annotated[int, Field(title="N Selected")]
    bucket_counts: Annotated[Dict[str, int], Field(title="Bucket Counts")]
    selected_counts: Annotated[Dict[str, int], Field(title="Selected Counts")]
    bucket_pct: Annotated[Dict[str, float], Field(title="Bucket Pct")]
    selected_pct: Annotated[Dict[str, float], Field(title="Selected Pct")]


class SourceReportResponse(BaseSchema, RootModel[List[SourceReportItem]]):
    root: Annotated[List[SourceReportItem], Field(title="SourceReportResponse")]


class ArticleResponse(BaseSchema, Article): ...


class RedditResponse(BaseSchema):
    as_dicts: Optional[List[RedditThread]] = None
    as_string: Optional[str] = None
