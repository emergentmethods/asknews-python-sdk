import pytest
from pydantic import ValidationError

from asknews_sdk.dto.distribution import (
    HitShareItem,
    HitShareResponse,
    TopNArticlesForDomainItem,
    TopNArticlesForDomainResponse,
)


def test_top_articles_optional_fields_and_defaults():
    response = TopNArticlesForDomainResponse.model_validate(
        {
            "data": [{"article_url": "https://example.com/story", "hit_count": 1}],
            "total_count": 1,
        }
    )
    assert response.page == 1
    assert response.next_page is None
    assert response.data[0].article_id is None
    assert (
        TopNArticlesForDomainItem(article_url="url", hit_count=0, article_id=None).article_id
        is None
    )
    assert TopNArticlesForDomainResponse(data=[], total_count=0, next_page=None).next_page is None


@pytest.mark.parametrize(
    "model,payload",
    [
        (HitShareResponse, {"data": [], "total_share": 0.0}),
        (TopNArticlesForDomainResponse, {"data": [], "total_count": 0}),
    ],
)
def test_empty_responses(model, payload):
    assert model.model_validate(payload).data == []


@pytest.mark.parametrize(
    "model,payload",
    [
        (HitShareItem, {"domain": "example.com"}),
        (HitShareResponse, {"data": []}),
        (TopNArticlesForDomainItem, {"article_url": "https://example.com/story"}),
        (TopNArticlesForDomainResponse, {"data": []}),
    ],
)
def test_required_counts_and_shares(model, payload):
    with pytest.raises(ValidationError):
        model.model_validate(payload)
