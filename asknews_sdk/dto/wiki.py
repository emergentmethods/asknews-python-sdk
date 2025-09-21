from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from asknews_sdk.dto.base import BaseSchema


class CirrusMetadata(BaseModel):
    create_timestamp: datetime
    wikibase_item: str
    version: int
    popularity_score: float
    text_bytes: int
    # other fields can be added as needed


class WikiResponseDictItem(BaseModel):
    content: str
    title: str
    url: str
    categories: List[str]
    timestamp: datetime
    cirrus_metadata: Optional[CirrusMetadata] = None
    point_id: Optional[str] = None


class WikiSearchResponse(BaseSchema):
    documents: List[WikiResponseDictItem]

    # @classmethod
    # def from_qdrant_records(
    #     cls,
    #     data: dict,
    # ) -> "WikiSearchResponse":

    #     return cls(

    #     )
