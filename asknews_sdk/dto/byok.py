from typing import Literal

from pydantic import Field
from typing_extensions import Annotated

from asknews_sdk.dto.base import BaseSchema


Provider = Literal["anthropic", "google"]


class UpsertApiKeyRequest(BaseSchema):
    api_key: Annotated[str, Field(min_length=10, title="Api Key")]


class ApiKeyResponse(BaseSchema):
    provider: Annotated[Provider, Field(title="Provider")]
    key_hint: Annotated[str, Field(title="Key Hint")]
