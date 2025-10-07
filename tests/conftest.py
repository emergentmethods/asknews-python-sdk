import asyncio

import pytest
import respx

from asknews_sdk.client import APIClient, AsyncAPIClient


CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
SCOPES = {"chat", "news", "stories", "analytics"}
BASE_URL = "https://api.asknews.app"
TOKEN_URL = "https://auth.asknews.app/oauth2/token"


# Redefine `pytest-asyncio` event loop fixture for session scope
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sync_api_client():
    with APIClient(
        client_id=None,
        client_secret=None,
        scopes=None,
        api_key=None,
        base_url=BASE_URL,
        token_url=TOKEN_URL,
        auth=None,
    ) as client:
        yield client


@pytest.fixture
def sync_api_client_with_auth():
    with APIClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
        api_key=None,
        base_url=BASE_URL,
        token_url=TOKEN_URL,
    ) as client:
        yield client


@pytest.fixture
async def async_api_client():
    async with AsyncAPIClient(
        client_id=None,
        client_secret=None,
        scopes=None,
        api_key=None,
        base_url=BASE_URL,
        token_url=TOKEN_URL,
        auth=None,
    ) as client:
        yield client


@pytest.fixture
async def async_api_client_with_auth():
    async with AsyncAPIClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
        api_key=None,
        base_url=BASE_URL,
        token_url=TOKEN_URL,
    ) as client:
        yield client


@pytest.fixture
def response_mock():
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as respx_mock:
        respx_mock.post(TOKEN_URL).respond(
            json={
                "access_token": "access_token",
                "token_type": "bearer",
                "expires_in": 3600,
                "scope": " ".join(SCOPES),
            }
        )

        yield respx_mock
