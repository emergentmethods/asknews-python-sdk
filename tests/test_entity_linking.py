"""Entity-linking and QID-lookup DTOs and request shapes."""
import inspect
from urllib.parse import parse_qs, quote, urlparse

import pytest
from pydantic import BaseModel, ValidationError

from asknews_sdk.api.wiki import AsyncWikiAPI, WikiAPI
from asknews_sdk.dto.wiki import (
    WikiBatchEntityRequest,
    WikiBatchEntityResponse,
    WikiBatchLinkEntityRequest,
    WikiBatchLinkEntityResponse,
    WikidataMetadata,
    WikiEntityResponse,
    WikiLinkEntityResponse,
    WikiSearchResponse,
)
from asknews_sdk.utils import build_url


def build_linked_payload(**overrides):
    payload = {
        "entity": "Apple",
        "entity_type": "organization",
        "linked_entity": {
            "title": "Apple Inc.",
            "description": "American technology company",
            "qid": "Q312",
            "relevance": 0.91,
        },
        "candidates": [
            {"title": "Apple Inc.", "qid": "Q312", "relevance": 0.91},
            {"title": "Apple", "qid": "Q89", "relevance": 0.42},
        ],
        "relevance_threshold": 0.40,
        "link_status": "linked",
        "link_confidence": 0.91,
    }
    payload.update(overrides)
    return payload


def test_linked_payload_parses():
    response = WikiLinkEntityResponse.model_validate(build_linked_payload())

    assert response.link_status == "linked"
    assert response.linked_entity.qid == "Q312"
    assert response.linked_entity.relevance == 0.91
    assert [c.qid for c in response.candidates] == ["Q312", "Q89"]


def test_no_match_has_null_entity():
    response = WikiLinkEntityResponse.model_validate(
        {
            "entity": "Zzzz Not A Real Entity",
            "entity_type": None,
            "link_status": "no_match",
            "link_confidence": 0.0,
        }
    )

    assert response.link_status == "no_match"
    assert response.linked_entity is None
    assert response.candidates is None


def test_ambiguous_status_is_accepted():
    response = WikiLinkEntityResponse.model_validate(
        build_linked_payload(link_status="ambiguous", link_confidence=0.51)
    )

    assert response.link_status == "ambiguous"
    assert response.linked_entity.qid == "Q312"


def test_unknown_link_status_is_rejected():
    with pytest.raises(ValidationError):
        WikiLinkEntityResponse.model_validate(
            build_linked_payload(link_status="maybe")
        )


def test_candidates_omitted_when_not_requested():
    payload = build_linked_payload()
    payload.pop("candidates")

    response = WikiLinkEntityResponse.model_validate(payload)

    assert response.candidates is None
    assert response.linked_entity.qid == "Q312"


def test_unknown_wikidata_metadata_fields_are_preserved():
    response = WikiLinkEntityResponse.model_validate(
        build_linked_payload(
            linked_entity={
                "title": "Apple Inc.",
                "qid": "Q312",
                "relevance": 0.91,
                "wikidata_metadata": {
                    "ceo": [{"qid": "Q312556", "label": "Tim Cook"}],
                    "some_future_property": 42,
                },
            }
        )
    )

    metadata = response.linked_entity.wikidata_metadata
    assert metadata.ceo[0].label == "Tim Cook"
    assert metadata.model_extra == {"some_future_property": 42}


def test_batch_response_preserves_order_and_per_entity_status():
    response = WikiBatchLinkEntityResponse.model_validate(
        {
            "results": [
                build_linked_payload(),
                {
                    "entity": "Nowhere",
                    "entity_type": None,
                    "link_status": "no_match",
                    "link_confidence": 0.0,
                },
            ]
        }
    )

    assert [r.entity for r in response.results] == ["Apple", "Nowhere"]
    assert [r.link_status for r in response.results] == ["linked", "no_match"]
    assert response.results[1].linked_entity is None


def test_batch_request_defaults_match_the_api():
    request = WikiBatchLinkEntityRequest(entities=["Apple", "Paris"])

    assert request.allow_ambiguous is True
    assert request.include_candidates is False
    assert request.n_candidates == 5
    assert request.relevance_threshold == 0.40
    assert request.ambiguity_margin == 0.05


def test_batch_request_allows_per_element_none_types():
    request = WikiBatchLinkEntityRequest(
        entities=["Apple", "Paris"],
        entity_types=["organization", None],
        entity_descriptions=[None, "the French capital"],
    )

    assert request.entity_types == ["organization", None]
    assert request.entity_descriptions == [None, "the French capital"]


@pytest.mark.parametrize("field", ["entity_types", "entity_descriptions"])
def test_batch_request_rejects_length_mismatch(field):
    with pytest.raises(ValidationError, match="must match entities length"):
        WikiBatchLinkEntityRequest(entities=["Apple", "Paris"], **{field: ["organization"]})


def test_batch_request_rejects_empty_entity_names():
    with pytest.raises(ValidationError, match="must not contain empty strings"):
        WikiBatchLinkEntityRequest(entities=["Apple", ""])


def test_batch_request_round_trips_to_json_body():
    request = WikiBatchLinkEntityRequest(
        entities=["Apple", "Paris"],
        entity_types=["organization", None],
        relevance_threshold=0.5,
        allow_ambiguous=False,
    )

    dumped = request.model_dump(mode="json")

    assert dumped["entities"] == ["Apple", "Paris"]
    assert dumped["entity_types"] == ["organization", None]
    assert dumped["relevance_threshold"] == 0.5
    assert dumped["allow_ambiguous"] is False
    assert WikiBatchLinkEntityRequest.model_validate(dumped) == request


# --- request shape sent to the API --------------------------------------------


@pytest.mark.parametrize("api", [WikiAPI, AsyncWikiAPI])
@pytest.mark.parametrize("method", ["link_entity", "link_entity_batch"])
def test_candidate_count_is_named_n_candidates(api, method):
    parameters = inspect.signature(getattr(api, method)).parameters

    assert "n_candidates" in parameters
    assert "n_documents" not in parameters
    assert parameters["n_candidates"].default == 5


@pytest.mark.parametrize("api", [WikiAPI, AsyncWikiAPI])
@pytest.mark.parametrize("method", ["search_wiki", "search_wiki_batch"])
def test_search_keeps_n_documents(api, method):
    parameters = inspect.signature(getattr(api, method)).parameters

    assert "n_documents" in parameters
    assert "n_candidates" not in parameters


@pytest.mark.parametrize("api", [WikiAPI, AsyncWikiAPI])
@pytest.mark.parametrize("method", ["search_wiki", "search_wiki_batch"])
def test_search_does_not_return_entity_documents(api, method):
    parameters = inspect.signature(getattr(api, method)).parameters

    assert "include_entities" not in parameters
    assert "has_wikidata" in parameters


def test_search_response_holds_only_article_documents():
    response = WikiSearchResponse.model_validate(
        {
            "documents": [
                {
                    "content": "Apple Inc. is an American technology company.",
                    "title": "Apple Inc.",
                    "url": "https://en.wikipedia.org/wiki/Apple_Inc.",
                    "categories": ["Technology companies"],
                    "timestamp": "2026-08-10T12:00:00+00:00",
                }
            ]
        }
    )

    assert response.documents[0].title == "Apple Inc."
    assert not hasattr(response.documents[0], "qid")

    with pytest.raises(ValidationError):
        WikiSearchResponse.model_validate(
            {"documents": [{"title": "Apple Inc.", "qid": "Q312", "relevance": 0.91}]}
        )


def test_link_entity_sends_n_candidates_on_the_query_string():
    url = build_url(
        base_url="https://api.asknews.dev",
        endpoint="/v1/wiki/link-entity",
        query={
            "entity": "Apple",
            "entity_type": None,
            "n_candidates": 3,
            "relevance_threshold": 0.40,
        },
    )

    parsed = parse_qs(urlparse(url).query)
    assert parsed["n_candidates"] == ["3"]
    assert "n_documents" not in parsed
    # Unset filters must not be sent, or they would override server defaults.
    assert "entity_type" not in parsed


# --- QID lookup ---------------------------------------------------------------


def test_entity_response_parses_a_hit():
    response = WikiEntityResponse.model_validate(
        {
            "qid": "Q312",
            "entity": {"title": "Apple Inc.", "qid": "Q312", "description": "tech company"},
            "found": True,
        }
    )

    assert response.found is True
    assert response.entity.qid == "Q312"


def test_entity_response_reports_a_miss_without_erroring():
    response = WikiEntityResponse.model_validate({"qid": "Q_missing", "found": False})

    assert response.found is False
    assert response.entity is None


def test_batch_entity_response_preserves_order_and_misses():
    response = WikiBatchEntityResponse.model_validate(
        {
            "results": [
                {"qid": "Q312", "entity": {"title": "Apple Inc.", "qid": "Q312"}, "found": True},
                {"qid": "Q_missing", "found": False},
            ]
        }
    )

    assert [r.qid for r in response.results] == ["Q312", "Q_missing"]
    assert [r.found for r in response.results] == [True, False]
    assert response.results[1].entity is None


def test_batch_entity_request_rejects_blank_qids():
    with pytest.raises(ValidationError, match="must not contain empty strings"):
        WikiBatchEntityRequest(qids=["Q312", "   "])


@pytest.mark.parametrize("api", [WikiAPI, AsyncWikiAPI])
@pytest.mark.parametrize("method", ["get_entity", "get_entity_batch"])
def test_qid_lookup_methods_exist(api, method):
    assert callable(getattr(api, method))


def test_qid_is_escaped_into_the_path():
    safe = build_url(
        base_url="https://api.asknews.dev",
        endpoint="/v1/wiki/entity/{qid}",
        params={"qid": quote("Q1/../admin", safe="")},
    )
    unsafe = build_url(
        base_url="https://api.asknews.dev",
        endpoint="/v1/wiki/entity/{qid}",
        params={"qid": "Q1/../admin"},
    )

    assert urlparse(safe).path == "/v1/wiki/entity/Q1%2F..%2Fadmin"
    assert urlparse(unsafe).path == "/v1/wiki/entity/admin"


# --- WikidataMetadata shape tolerance -----------------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        (
            "ceo",
            [
                {
                    "qid": "Q5820",
                    "label": "Steve Jobs",
                    "start_time": "+1997-09-16T00:00:00Z",
                    "end_time": "+2011-08-24T00:00:00Z",
                    "rank": "normal",
                },
                {
                    "qid": "Q312556",
                    "label": "Tim Cook",
                    "start_time": "+2011-08-24T00:00:00Z",
                    "rank": "normal",
                },
            ],
        ),
        ("place_of_birth", {"qid": "Q60", "label": "New York City"}),
        ("date_of_birth", "+1955-02-24T00:00:00Z"),
        ("gnd_id", ["118637347"]),
        ("official_name", [{"text": "Apple Inc.", "language": "en"}]),
        ("social_media_followers", [{"amount": 5000000, "platform": "x_twitter"}]),
        ("ceo", None),
    ],
)
def test_metadata_accepts_property_shapes(field, value):
    metadata = WikidataMetadata(**{field: value})
    parsed = getattr(metadata, field)

    def _plain(v):
        if isinstance(v, list):
            return [_plain(x) for x in v]
        if isinstance(v, BaseModel):
            return v.model_dump(exclude_none=True)
        return v

    assert _plain(parsed) == value


def test_metadata_passes_through_undeclared_fields():
    metadata = WikidataMetadata(some_future_property=[{"qid": "Q1"}])

    assert metadata.model_dump(exclude_none=True) == {
        "some_future_property": [{"qid": "Q1"}]
    }


def test_metadata_uses_the_served_field_names():
    declared = set(WikidataMetadata.model_fields)

    assert {"occupations", "employers", "positions_held"}.isdisjoint(declared)
    assert {"occupation", "employer", "position_held"} <= declared
    assert "wikipedia_url" not in declared
    assert "wikipedia_titles" in declared
