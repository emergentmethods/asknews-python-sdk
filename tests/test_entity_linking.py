"""Tests for `link_entity` / `link_entity_batch`: their DTOs and the requests they send."""
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
    """A minimal, valid `linked` entity link payload."""
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
    """An abstained link carries a status but no entity."""
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
    """`wikidata_metadata` allows extras so new upstream properties survive the SDK."""
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
    # A declared property parses into its typed shape...
    assert metadata.ceo[0].label == "Tim Cook"
    # ...while one this SDK does not know about still reaches the caller.
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
    assert request.include_candidates is True
    assert request.relevance_threshold is None
    assert request.ambiguity_margin is None


def test_batch_request_allows_per_element_none_types():
    """Types align positionally, and an unknown type for one entity is expressed as None."""
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
    """The request is serialized as the POST body, so it must survive a JSON round trip."""
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
    """Linking counts candidates, not documents: the API names this `n_candidates`."""
    parameters = inspect.signature(getattr(api, method)).parameters

    assert "n_candidates" in parameters
    assert "n_documents" not in parameters
    assert parameters["n_candidates"].default == 5


@pytest.mark.parametrize("api", [WikiAPI, AsyncWikiAPI])
@pytest.mark.parametrize("method", ["search_wiki", "search_wiki_batch"])
def test_search_keeps_n_documents(api, method):
    """The rename was scoped to entity linking; wiki search still counts documents."""
    parameters = inspect.signature(getattr(api, method)).parameters

    assert "n_documents" in parameters
    assert "n_candidates" not in parameters


@pytest.mark.parametrize("api", [WikiAPI, AsyncWikiAPI])
@pytest.mark.parametrize("method", ["search_wiki", "search_wiki_batch"])
def test_search_does_not_return_entity_documents(api, method):
    """Wiki search returns article chunks only; entities come from the link and
    QID methods, so there is no toggle for including them here."""
    parameters = inspect.signature(getattr(api, method)).parameters

    assert "include_entities" not in parameters
    # The surviving Wikidata-adjacent filter is unaffected by the removal.
    assert "has_wikidata" in parameters


def test_search_response_holds_only_article_documents():
    """Search can no longer return entity documents, so a QID payload must not validate."""
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
    """`build_url` drops None and stringifies, so assert on the URL the API receives."""
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
    # Unset optional filters must not be sent, or they would override server defaults.
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
    """A QID that is not in the collection is a found=False result, not an error."""
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
    """`build_url` interpolates raw and then normalizes, so a '/' in a QID would
    otherwise silently retarget the request at a different endpoint."""
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
    # Demonstrates why the escaping is required.
    assert urlparse(unsafe).path == "/v1/wiki/entity/admin"


# --- WikidataMetadata shape tolerance -----------------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        # The shapes the API sends today: lists of dicts, with the key set
        # varying by property.
        #
        # A QID-valued property lists EVERY claim, not just the current one.
        # Both entries here are rank "normal" — Wikidata does not reliably mark
        # the current one — and the second carries no end_time qualifier at all,
        # so the key is simply absent rather than null.
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
        # A "single-best-value" property: rival accounts of ONE fact, so the API
        # sends the best-ranked claim alone rather than a list.
        ("place_of_birth", {"qid": "Q60", "label": "New York City"}),
        # Times are plain ISO-ish strings.
        ("date_of_birth", "+1955-02-24T00:00:00Z"),
        # External identifiers are ALWAYS lists -- an identifier is a join key,
        # and entities legitimately carry two.
        ("gnd_id", ["118637347"]),
        ("official_name", [{"text": "Apple Inc.", "language": "en"}]),
        ("social_media_followers", [{"amount": 5000000, "platform": "x_twitter"}]),
        # Absent when the entity has no such claim.
        ("ceo", None),
    ],
)
def test_metadata_accepts_property_shapes(field, value):
    """Property-derived fields parse the shapes the API actually sends.

    These fields are typed, so the parsed value is a model (or list of models)
    rather than the raw dict — compare via model_dump(exclude_none=True), which
    also pins that absent qualifiers stay absent rather than becoming nulls.
    """
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
    """Wikidata exposes far more properties than this model declares.

    Undeclared ones must still reach the caller, otherwise a newly served
    property would be silently dropped until the SDK caught up.
    """
    metadata = WikidataMetadata(some_future_property=[{"qid": "Q1"}])

    assert metadata.model_dump(exclude_none=True) == {
        "some_future_property": [{"qid": "Q1"}]
    }


def test_metadata_uses_the_served_field_names():
    """A declared field whose name is not the served one never populates.

    It is an invisible failure: it does not raise, it just reads as None
    forever. These singular/plural pairs are the easy ones to get wrong.
    """
    declared = set(WikidataMetadata.model_fields)

    assert {"occupations", "employers", "positions_held"}.isdisjoint(declared)
    assert {"occupation", "employer", "position_held"} <= declared
    # `wikipedia_titles` carries every language, not just en.
    assert "wikipedia_url" not in declared
    assert "wikipedia_titles" in declared
