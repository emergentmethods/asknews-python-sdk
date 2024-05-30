from typing import Callable, Literal, Tuple, Union

from httpx import Auth, Request
from pydantic import BaseModel


class Sentinel:
    def __repr__(self):
        return self.__class__.__name__

CLIENT_DEFAULT = Sentinel()


RequestAuth = Union[
    Callable[[Request], Request],
    Auth,
    Tuple[Union[str, bytes], Union[str, bytes]],
]

StreamType = Literal["bytes", "lines", "raw"]

class ServerSentEvent(BaseModel):
    event: str = "message"
    data: list = []
    id: str = ""
    retry: int = 0

    @property
    def content(self) -> str:
        return "\n".join(self.data)
