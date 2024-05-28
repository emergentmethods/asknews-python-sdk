from typing import Callable, Literal, Tuple, TypeAlias, Union

from httpx import Auth, Request


RequestAuth = Union[
    Callable[[Request], Request],
    Auth,
    Tuple[Union[str, bytes], Union[str, bytes]],
]

StreamType: TypeAlias = Literal["bytes", "lines", "raw"]
