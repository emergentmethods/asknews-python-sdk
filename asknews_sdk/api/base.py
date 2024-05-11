from typing import Union

from asknews_sdk.client import APIClient, AsyncAPIClient


class BaseAPI:
    def __init__(self, client: Union[APIClient, AsyncAPIClient]) -> None:
        self.client = client
