from __future__ import annotations

from typing import List

from pydantic import AwareDatetime, BaseModel, Field
from typing_extensions import Annotated

from asknews_sdk.dto.base import BaseSchema


class FinanceResponseTimeSeriesData(BaseModel):
    datetime: Annotated[AwareDatetime, Field(title="Datetime")]
    value: Annotated[int, Field(title="Value")]


class FinanceResponseTimeSeries(BaseModel):
    timeseries: Annotated[
        List[FinanceResponseTimeSeriesData], Field(title="Timeseriesdata")
    ]


class FinanceResponse(BaseSchema):
    data: FinanceResponseTimeSeries
