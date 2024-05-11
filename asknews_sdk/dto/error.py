from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class APIErrorModel(BaseModel):
    code: Annotated[Optional[int], Field(title="Error Code")] = 500000
    detail: Annotated[Optional[str], Field(title="Detail")] = "Internal Server Error"


class ValidationError(BaseModel):
    loc: Annotated[List[Union[str, int]], Field(title="Location")]
    msg: Annotated[str, Field(title="Message")]
    type: Annotated[str, Field(title="Error Type")]


class HTTPValidationError(BaseModel):
    detail: Annotated[Optional[List[ValidationError]], Field(None, title="Detail")]
