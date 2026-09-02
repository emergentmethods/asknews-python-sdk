from typing import get_args

import pytest

from asknews_sdk.dto.alert import DeepNewsParams
from asknews_sdk.dto.deepnews import CreateDeepNewsRequest, DeepNewsSourceType


MESSAGES = [{"role": "user", "content": "query"}]


def test_podcasts_is_a_valid_deepnews_source():
    assert "podcasts" in get_args(DeepNewsSourceType)


@pytest.mark.parametrize("source", get_args(DeepNewsSourceType))
def test_create_deepnews_request_accepts_every_source(source: str):
    assert CreateDeepNewsRequest(messages=MESSAGES, sources=source).sources == source
    assert CreateDeepNewsRequest(messages=MESSAGES, sources=[source]).sources == [source]


def test_create_deepnews_request_accepts_newsplunker_alert_defaults():
    # The source list the Newsplunker alert form sends; a missing member here
    # fails the alert's fetch_sources stage and silently skips its email.
    sources = ["asknews", "google", "x", "podcasts", "wiki"]

    assert CreateDeepNewsRequest(messages=MESSAGES, sources=sources).sources == sources
    assert DeepNewsParams(sources=sources).sources == sources
