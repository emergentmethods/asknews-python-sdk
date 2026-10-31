from __future__ import annotations

from typing import Annotated, List, Union

from pydantic import AwareDatetime, BaseModel, Field

from asknews_sdk.dto.base import BaseSchema


class FinanceResponseTimeSeriesData(BaseModel):
    datetime: Annotated[AwareDatetime, Field(title="Datetime")]
    value: Annotated[Union[int, float], Field(title="Value")]


class FinanceResponseTimeSeries(BaseModel):
    timeseries: Annotated[List[FinanceResponseTimeSeriesData], Field(title="Timeseriesdata")]


class FinanceResponse(BaseSchema):
    data: FinanceResponseTimeSeries
