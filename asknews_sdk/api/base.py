from typing import Generic, TypeVar

from asknews_sdk.client import APIClient, AsyncAPIClient


TAPIClient = TypeVar("TAPIClient", APIClient, AsyncAPIClient)

class BaseAPI(Generic[TAPIClient]):
    def __init__(self, client: TAPIClient) -> None:
        self.client: TAPIClient = client
