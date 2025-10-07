from __future__ import annotations

import asyncio
import base64
import inspect
import json
import os
import threading
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import AsyncGenerator, Awaitable, Callable, Generator, Optional, Set, Union
from urllib.parse import quote, urlencode

from anyio import Path as AsyncPath
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from httpx import Auth, Request, Response
from typing_extensions import TypedDict


class SecurityWarning(Warning): ...


def encode_client_secret_basic(client_id: str, client_secret: str) -> str:
    text = f"{quote(client_id)}:{quote(client_secret)}"
    auth = base64.b64encode(text.encode()).decode()
    return f"Basic {auth}"


class TokenInfo(TypedDict):
    access_token: str
    scope: str
    token_type: str
    expires_in: int


TokenLoadHook = Callable[..., Optional[TokenInfo]]
TokenSaveHook = Callable[[TokenInfo], None]
AsyncTokenLoadHook = Callable[..., Awaitable[Optional[TokenInfo]]]
AsyncTokenSaveHook = Callable[[TokenInfo], Awaitable[None]]


class OAuthToken:
    def __init__(self, token_info: Optional[TokenInfo] = None) -> None:  # type: ignore
        self.set_token(token_info)

    def set_token(self, token_info: Optional[TokenInfo]) -> None:
        self.token_info = token_info
        self._expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=(
                self.token_info.get("expires_in", 0)
                if self.token_info
                else 0
            )
        )

    def reset_token(self):
        self.token_info = None

    @property
    def is_expired(self) -> bool:
        if not self.token_info:
            return True
        return datetime.now(timezone.utc) > self._expires_at

    @property
    def is_empty(self) -> bool:
        return not self.token_info

    @property
    def access_token(self) -> str:
        if not self.token_info:
            return ""
        return self.token_info["access_token"]

    @property
    def scope(self) -> str:
        if not self.token_info:
            return ""
        return self.token_info["scope"]

    @property
    def expires(self) -> datetime:
        return self._expires_at


class APIKey(Auth):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def inject_headers(self, request: Request) -> Request:
        request.headers["Authorization"] = f"Bearer {self.api_key}"
        return request

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        yield self.inject_headers(request)

    async def async_auth_flow(self, request: Request) -> AsyncGenerator[Request, Response]:
        yield self.inject_headers(request)


class OAuth2ClientCredentials(Auth):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        scopes: Optional[Set[str]] = None,
        token: Optional[OAuthToken] = None,
        *,
        _token_load_hook: Optional[Union[TokenLoadHook, AsyncTokenLoadHook]] = None,
        _token_save_hook: Optional[Union[TokenSaveHook, AsyncTokenSaveHook]] = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.scope = " ".join({"offline", "openid", *(scopes or set())})
        self.token = token or OAuthToken()

        if _token_load_hook or _token_save_hook:
            warnings.warn(
                "Using _token_load_hook and _token_save_hook is deprecated and will be "
                "removed in a future version.",
                DeprecationWarning,
                stacklevel=2,
            )

        self._token_load_hook = _token_load_hook
        self._token_save_hook = _token_save_hook

        self._token_lock = threading.RLock()
        self._atoken_lock = asyncio.Lock()

    def _build_fetch_token_request(self) -> Request:
        return Request(
            method="POST",
            url=self.token_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": encode_client_secret_basic(self.client_id, self.client_secret),
            },
            content=urlencode(
                {
                    "grant_type": "client_credentials",
                    "scope": self.scope,
                }
            ),
        )

    def inject_headers(self, request: Request) -> Request:
        request.headers["Authorization"] = f"Bearer {self.token.access_token}"
        return request

    def sync_auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        retried = False

        if (
            not self.token.access_token
            and self._token_load_hook
            and inspect.isfunction(self._token_load_hook)
        ):
            with self._token_lock:
                self.token.set_token(self._token_load_hook())

        while True:
            if self.token.is_expired:
                fetch_response = yield self._build_fetch_token_request()
                fetch_response.read()
                fetch_response.raise_for_status()

                with self._token_lock:
                    self.token.set_token(fetch_response.json())

            response = yield self.inject_headers(request)
            if (
                response
                and response.status_code == 401
                and not retried
            ):
                retried = True
                self.token.reset_token()
                continue
            else:
                break

        if (
            self._token_save_hook
            and inspect.isfunction(self._token_save_hook)
            and not inspect.iscoroutinefunction(self._token_save_hook)
        ):
            with self._token_lock:
                self._token_save_hook(self.token.token_info)

    async def async_auth_flow(self, request: Request) -> AsyncGenerator[Request, Response]:
        retried = False

        if (
            not self.token.access_token
            and self._token_load_hook
            and inspect.iscoroutinefunction(self._token_load_hook)
        ):
            async with self._atoken_lock:
                self.token.set_token(await self._token_load_hook())

        while True:
            if self.token.is_expired:
                fetch_response = yield self._build_fetch_token_request()
                await fetch_response.aread()
                fetch_response.raise_for_status()

                async with self._atoken_lock:
                    self.token.set_token(fetch_response.json())

            response = yield self.inject_headers(request)

            if (
                response
                and response.status_code == 401
                and not retried
            ):
                retried = True
                self.token.reset_token()
                continue
            else:
                break

        if (
            self._token_save_hook
            and self.token.token_info
            and inspect.iscoroutinefunction(self._token_save_hook)
        ):
            async with self._atoken_lock:
                await self._token_save_hook(self.token.token_info)


def _derive_encryption_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _encrypt_with_key(key: bytes, data: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data)


def _decrypt_with_key(key: bytes, data: bytes) -> bytes:
    f = Fernet(key)
    return f.decrypt(data)


def _save_token_disk(
    file_path: Union[Path, str], client_id: str, client_secret: str
) -> TokenSaveHook:
    warnings.warn(
        "Saving access tokens to disk is dangerous and should be avoided. "
        "Use at your own risk.",
        SecurityWarning,
        stacklevel=2,
    )

    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    def _save_token(token: TokenInfo) -> None:
        salt = os.urandom(16)
        key = _derive_encryption_key((client_id + client_secret), salt)

        serialized_token = json.dumps(token).encode()
        token_info = _encrypt_with_key(key, serialized_token)
        file_path.write_bytes(salt + b"::" + token_info)

    return _save_token


def _load_token_disk(file_path: Path, client_id: str, client_secret: str) -> TokenLoadHook:
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    def _load_token() -> Optional[TokenInfo]:
        if not file_path.exists():
            return None

        data = file_path.read_bytes()
        salt, token_info = data.split(b"::", 1)

        key = _derive_encryption_key((client_id + client_secret), salt)
        serialized_token = _decrypt_with_key(key, token_info)

        return json.loads(serialized_token)

    return _load_token


def _save_token_disk_async(
    file_path: Union[Path, AsyncPath, str], client_id: str, client_secret: str
) -> AsyncTokenSaveHook:
    warnings.warn(
        "Saving access tokens to disk is dangerous and should be avoided. "
        "Use at your own risk.",
        SecurityWarning,
        stacklevel=2,
    )

    if not isinstance(file_path, AsyncPath):
        file_path = AsyncPath(file_path)

    async def _save_token(token: TokenInfo) -> None:
        salt = os.urandom(16)
        key = _derive_encryption_key((client_id + client_secret), salt)

        serialized_token = json.dumps(token).encode()
        token_info = _encrypt_with_key(key, serialized_token)
        await file_path.write_bytes(salt + b"::" + token_info)

    return _save_token


def _load_token_disk_async(
    file_path: Union[Path, AsyncPath, str], client_id: str, client_secret: str
) -> AsyncTokenLoadHook:
    if not isinstance(file_path, AsyncPath):
        file_path = AsyncPath(file_path)

    async def _load_token() -> Optional[TokenInfo]:
        if not await file_path.exists():
            return None

        data = await file_path.read_bytes()
        salt, token_info = data.split(b"::", 1)

        key = _derive_encryption_key((client_id + client_secret), salt)
        serialized_token = _decrypt_with_key(key, token_info)
        return json.loads(serialized_token)

    return _load_token
