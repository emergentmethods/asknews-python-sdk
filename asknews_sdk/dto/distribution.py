from typing import List

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
