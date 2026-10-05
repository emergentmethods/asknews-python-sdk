from typing import List, Optional

from pydantic import BaseModel

from asknews_sdk.dto.base import BaseSchema


class DomainMetricsDayItem(BaseModel):
    day: str
    surfaces: int
    citations: int
    full_text: int


class DomainMetricsResponse(BaseSchema):
    surfaces: int
    citations: int
    full_text: int


class DomainMetricsTimeWindowResponse(BaseSchema):
    data: List[DomainMetricsDayItem]
    total_surfaces: int
    total_citations: int
    total_full_text: int


class TopNArticlesForDomainItem(BaseModel):
    article_url: str
    article_id: Optional[str] = None
    hit_count: int


class TopNArticlesForDomainResponse(BaseSchema):
    data: List[TopNArticlesForDomainItem]
    total_count: int
    page: int = 1
    next_page: Optional[int] = None
