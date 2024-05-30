import pytest
from anyio import Path as AsyncPath
from cryptography.fernet import InvalidToken
from httpx import Request, Response, HTTPStatusError

from asknews_sdk.security import (
    OAuth2ClientCredentials,
    OAuthToken,
    TokenInfo,
    SecurityWarning,
    encode_client_secret_basic,
    _derive_encryption_key,
    _encrypt_with_key,
    _decrypt_with_key,
    _load_token_disk,
    _load_token_disk_async,
    _save_token_disk,
    _save_token_disk_async,
)


@pytest.fixture
def client_credentials():
    return {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "token_url": "https://example.com/token",
        "scopes": {"scope1", "scope2"},
    }


@pytest.fixture
def oauth2_client_credentials(client_credentials):
    return OAuth2ClientCredentials(**client_credentials)


def test_oauth2_client_credentials_sync_auth_flow_happy(oauth2_client_credentials):
    request = Request("GET", "https://example.com/api")
    token_response = Response(
        request=Request("POST", "https://example.com/token"),
        status_code=200,
        headers={"content-type": "application/json"},
        content=b'{"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer", "scope": "scope1 scope2"}',
    )

    auth_flow = oauth2_client_credentials.sync_auth_flow(request)

    request = auth_flow.__next__()
    assert request.url == "https://example.com/token"

    response = auth_flow.send(token_response)
    assert response.headers["Authorization"] == "Bearer access_token"

    with pytest.raises(StopIteration):
        auth_flow.__next__()

    auth_flow.close()

    assert oauth2_client_credentials.token.access_token == "access_token"
    assert oauth2_client_credentials.token.scope == "scope1 scope2"


async def test_oauth2_client_credentials_async_auth_flow_happy(oauth2_client_credentials):
    request = Request("GET", "https://example.com/api")
    token_response = Response(
        request=Request("POST", "https://example.com/token"),
        status_code=200,
        headers={"content-type": "application/json"},
        content=b'{"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer", "scope": "scope1 scope2"}',
    )

    auth_flow = oauth2_client_credentials.async_auth_flow(request)
    request = await auth_flow.__anext__()
    assert request.url == "https://example.com/token"

    response = await auth_flow.asend(token_response)
    assert response.headers["Authorization"] == "Bearer access_token"

    with pytest.raises(StopAsyncIteration):
        await auth_flow.__anext__()

    await auth_flow.aclose()

    assert oauth2_client_credentials.token.access_token == "access_token"
    assert oauth2_client_credentials.token.scope == "scope1 scope2"


def test_oauth2_client_credentials_sync_auth_flow_error_response(oauth2_client_credentials):
    request = Request("GET", "https://example.com/api")
    token_response = Response(
        request=Request("POST", "https://example.com/token"),
        status_code=400,
        headers={"content-type": "application/json"},
        content=b'{"error": "invalid_request"}',
    )

    auth_flow = oauth2_client_credentials.sync_auth_flow(request)

    request = auth_flow.__next__()
    assert request.url == "https://example.com/token"

    with pytest.raises(HTTPStatusError) as exc_info:
        auth_flow.send(token_response)

    assert exc_info.value.response == token_response
    assert "Authorization" not in exc_info.value.response.headers

    assert oauth2_client_credentials.token.access_token == ""
    assert oauth2_client_credentials.token.scope == ""

    auth_flow.close()


async def test_oauth2_client_credentials_async_auth_flow_error_response(oauth2_client_credentials):
    request = Request("GET", "https://example.com/api")
    token_response = Response(
        request=Request("POST", "https://example.com/token"),
        status_code=400,
        headers={"content-type": "application/json"},
        content=b'{"error": "invalid_request"}',
    )

    auth_flow = oauth2_client_credentials.async_auth_flow(request)
    request = await auth_flow.__anext__()
    assert request.url == "https://example.com/token"

    with pytest.raises(HTTPStatusError) as exc_info:
        await auth_flow.asend(token_response)

    assert exc_info.value.response == token_response
    assert "Authorization" not in exc_info.value.response.headers

    assert oauth2_client_credentials.token.access_token == ""
    assert oauth2_client_credentials.token.scope == ""

    await auth_flow.aclose()


def test_oauth2_client_credentials_sync_auth_flow_token_load_hook(client_credentials):
    def token_load_hook() -> TokenInfo:
        return TokenInfo(
            access_token="access_token_loaded",
            expires_in=3600,
            token_type="Bearer",
            scope="scope1 scope2",
        )
    
    async def async_token_load_hook() -> TokenInfo:
        return TokenInfo(
            access_token="access_token_loaded",
            expires_in=3600,
            token_type="Bearer",
            scope="scope1 scope2",
        )

    oauth2_client_credentials = OAuth2ClientCredentials(
        **client_credentials, _token_load_hook=token_load_hook
    )

    request = Request("GET", "https://example.com/api")
    auth_flow = oauth2_client_credentials.sync_auth_flow(request)

    request = auth_flow.__next__()
    assert request.url == "https://example.com/api"
    assert request.headers["Authorization"] == "Bearer access_token_loaded"

    with pytest.raises(StopIteration):
        auth_flow.__next__()
    
    auth_flow.close()

    assert oauth2_client_credentials.token.access_token == "access_token_loaded"
    assert oauth2_client_credentials.token.scope == "scope1 scope2"

    oauth2_client_credentials = OAuth2ClientCredentials(
        **client_credentials, _token_load_hook=async_token_load_hook
    )

    request = Request("GET", "https://example.com/api")
    auth_flow = oauth2_client_credentials.sync_auth_flow(request)

    assert oauth2_client_credentials.token.access_token == ""
    assert oauth2_client_credentials.token.scope == ""

    auth_flow.close()


async def test_oauth2_client_credentials_async_auth_flow_token_load_hook(client_credentials):
    async def async_token_load_hook() -> TokenInfo:
        return TokenInfo(
            access_token="access_token_loaded",
            expires_in=3600,
            token_type="Bearer",
            scope="scope1 scope2",
        )

    def token_load_hook() -> TokenInfo:
        return TokenInfo(
            access_token="access_token_loaded",
            expires_in=3600,
            token_type="Bearer",
            scope="scope1 scope2",
        )

    oauth2_client_credentials = OAuth2ClientCredentials(
        **client_credentials, _token_load_hook=async_token_load_hook
    )

    request = Request("GET", "https://example.com/api")
    auth_flow = oauth2_client_credentials.async_auth_flow(request)

    request = await auth_flow.__anext__()
    assert request.url == "https://example.com/api"
    assert request.headers["Authorization"] == "Bearer access_token_loaded"

    with pytest.raises(StopAsyncIteration):
        await auth_flow.__anext__()

    await auth_flow.aclose()

    assert oauth2_client_credentials.token.access_token == "access_token_loaded"
    assert oauth2_client_credentials.token.scope == "scope1 scope2"

    oauth2_client_credentials = OAuth2ClientCredentials(
        **client_credentials, _token_load_hook=token_load_hook
    )

    request = Request("GET", "https://example.com/api")
    auth_flow = oauth2_client_credentials.async_auth_flow(request)

    assert oauth2_client_credentials.token.access_token == ""
    assert oauth2_client_credentials.token.scope == ""

    await auth_flow.aclose()


def test_oauth2_client_credentials_sync_auth_flow_token_save_hook(client_credentials):
    def token_save_hook(token_info: TokenInfo):
        assert token_info["access_token"] == "access_token"

    async def async_token_save_hook(token_info: TokenInfo):
        assert False, "This should not be called"

    oauth2_client_credentials = OAuth2ClientCredentials(
        **client_credentials, _token_save_hook=token_save_hook
    )

    request = Request("GET", "https://example.com/api")
    token_response = Response(
        request=Request("POST", "https://example.com/token"),
        status_code=200,
        headers={"content-type": "application/json"},
        content=b'{"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer", "scope": "scope1 scope2"}',
    )

    auth_flow = oauth2_client_credentials.sync_auth_flow(request)

    request = auth_flow.__next__()
    assert request.url == "https://example.com/token"

    response = auth_flow.send(token_response)
    assert response.headers["Authorization"] == "Bearer access_token"

    with pytest.raises(StopIteration):
        auth_flow.__next__()

    auth_flow.close()

    assert oauth2_client_credentials.token.access_token == "access_token"
    assert oauth2_client_credentials.token.scope == "scope1 scope2"

    oauth2_client_credentials = OAuth2ClientCredentials(
        **client_credentials, _token_save_hook=async_token_save_hook
    )

    request = Request("GET", "https://example.com/api")
    auth_flow = oauth2_client_credentials.sync_auth_flow(request)

    request = auth_flow.__next__()
    assert request.url == "https://example.com/token"

    response = auth_flow.send(token_response)
    assert response.headers["Authorization"] == "Bearer access_token"

    with pytest.raises(StopIteration):
        auth_flow.__next__()

    auth_flow.close()

    assert oauth2_client_credentials.token.access_token == "access_token"
    assert oauth2_client_credentials.token.scope == "scope1 scope2"


async def test_oauth2_client_credentials_async_auth_flow_token_save_hook(client_credentials):
    async def async_token_save_hook(token_info: TokenInfo):
        assert token_info["access_token"] == "access_token"

    def token_save_hook(token_info: TokenInfo):
        assert False, "This should not be called"

    oauth2_client_credentials = OAuth2ClientCredentials(
        **client_credentials, _token_save_hook=async_token_save_hook
    )

    request = Request("GET", "https://example.com/api")
    token_response = Response(
        request=Request("POST", "https://example.com/token"),
        status_code=200,
        headers={"content-type": "application/json"},
        content=b'{"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer", "scope": "scope1 scope2"}',
    )

    auth_flow = oauth2_client_credentials.async_auth_flow(request)

    request = await auth_flow.__anext__()
    assert request.url == "https://example.com/token"

    response = await auth_flow.asend(token_response)
    assert response.headers["Authorization"] == "Bearer access_token"

    with pytest.raises(StopAsyncIteration):
        await auth_flow.__anext__()

    await auth_flow.aclose()

    assert oauth2_client_credentials.token.access_token == "access_token"
    assert oauth2_client_credentials.token.scope == "scope1 scope2"

    oauth2_client_credentials = OAuth2ClientCredentials(
        **client_credentials, _token_save_hook=token_save_hook
    )

    request = Request("GET", "https://example.com/api")
    auth_flow = oauth2_client_credentials.async_auth_flow(request)

    request = await auth_flow.__anext__()
    assert request.url == "https://example.com/token"

    response = await auth_flow.asend(token_response)
    assert response.headers["Authorization"] == "Bearer access_token"

    with pytest.raises(StopAsyncIteration):
        await auth_flow.__anext__()

    await auth_flow.aclose()

    assert oauth2_client_credentials.token.access_token == "access_token"
    assert oauth2_client_credentials.token.scope == "scope1 scope2"


def test_encode_client_secret_basic(client_credentials):
    ground_truth_client_secret_basic = "Basic Y2xpZW50X2lkOmNsaWVudF9zZWNyZXQ="

    client_id = client_credentials["client_id"]
    client_secret = client_credentials["client_secret"]
    encoded_client_secret_basic = encode_client_secret_basic(client_id, client_secret)

    assert encoded_client_secret_basic.startswith("Basic ")
    assert encoded_client_secret_basic == ground_truth_client_secret_basic

def test_oauth_token():
    token_info = {
        "access_token": "access_token",
        "scope": "scope1 scope2",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    token = OAuthToken(token_info)

    assert token.access_token == "access_token"
    assert token.scope == "scope1 scope2"
    assert not token.is_expired
    assert not token.is_empty


    token_info = {
        "access_token": "access_token",
        "scope": "scope1 scope2",
        "token_type": "Bearer",
        "expires_in": -1,
    }
    token = OAuthToken(token_info)

    assert token.access_token == "access_token"
    assert token.scope == "scope1 scope2"
    assert token.is_expired
    assert not token.is_empty

    token_info = {
        "access_token": "access_token",
        "scope": "scope1 scope2",
        "token_type": "Bearer",
    }
    token = OAuthToken(token_info)

    assert token.access_token == "access_token"
    assert token.scope == "scope1 scope2"
    assert token.is_expired
    assert not token.is_empty

    token_info = {}
    token = OAuthToken(token_info)

    assert token.access_token == ""
    assert token.scope == ""
    assert token.is_expired
    assert token.is_empty


def test_derive_encryption_key_deterministic():
    password = "password"
    salt = b"12345678"

    key1 = _derive_encryption_key(password, salt)
    key2 = _derive_encryption_key(password, salt)

    assert key1 == key2

    password = "password"
    salt = b"12345679"

    key3 = _derive_encryption_key(password, salt)

    assert key1 != key3


def test_encrypt_decrypt():
    password = "password"
    salt = b"12345678"

    key = _derive_encryption_key(password, salt)
    plaintext = b"plaintext"

    ciphertext = _encrypt_with_key(key, plaintext)
    decrypted = _decrypt_with_key(key, ciphertext)

    assert plaintext == decrypted

    password = "password"
    salt = b"12345679"

    key = _derive_encryption_key(password, salt)

    with pytest.raises(InvalidToken):
        _decrypt_with_key(key, ciphertext)


def test_load_save_token_disk(tmp_path):
    client_id = "client_id"
    client_secret = "client_secret"
    token_info = {
        "access_token": "access_token",
        "scope": "scope1 scope2",
        "token_type": "Bearer",
        "expires_in": 3600,
    }

    file_path = tmp_path / "token"

    with pytest.warns(SecurityWarning):
        save_token = _save_token_disk(file_path, client_id, client_secret)

    save_token(token_info)

    load_token = _load_token_disk(file_path, client_id, client_secret)
    loaded_token_info = load_token()

    assert token_info == loaded_token_info


async def test_load_save_token_disk_async(tmp_path):
    client_id = "client_id"
    client_secret = "client_secret"
    token_info = {
        "access_token": "access_token",
        "scope": "scope1 scope2",
        "token_type": "Bearer",
        "expires_in": 3600,
    }

    file_path = AsyncPath(tmp_path / "token")

    with pytest.warns(SecurityWarning):
        save_token = _save_token_disk_async(file_path, client_id, client_secret)

    await save_token(token_info)

    load_token = _load_token_disk_async(file_path, client_id, client_secret)
    loaded_token_info = await load_token()

    assert token_info == loaded_token_info

