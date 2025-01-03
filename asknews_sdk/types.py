from typing import Annotated, Callable, Literal, Tuple, Union

from crontab import CronTab
from httpx import Auth, Request
from pydantic import AfterValidator, BaseModel, BeforeValidator, HttpUrl


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


HttpUrlString = Annotated[HttpUrl, AfterValidator(lambda v: str(v))]
CronStr = Annotated[str, BeforeValidator(lambda v: validate_crontab(v))]


def validate_crontab(v: str):
    try:
        CronTab(crontab=v)
    except ValueError:
        raise
    except BaseException:
        pass
    return v
