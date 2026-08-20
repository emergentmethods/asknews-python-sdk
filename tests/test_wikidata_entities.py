"""Tests for the optional `wikidata_entities` article property on structured search results."""
import copy
from uuid import uuid4

import pytest

from asknews_sdk.dto.base import WikidataEntity
from asknews_sdk.dto.news import SearchResponse, SearchResponseDictItem


def build_article_payload(**overrides):
    """A minimal, valid structured search_news article payload."""
    payload = {
        "as_string_key": "0",
        "article_url": "https://example.com/article",
        "article_id": str(uuid4()),
        "classification": ["Politics"],
        "country": "US",
        "source_id": "example",
        "page_rank": 3,
        "domain_url": "example.com",
        "eng_title": "Example title",
        "entities": {"Person": ["Ada Lovelace"], "Organization": []},
        "keywords": ["example"],
        "language": "en",
        "pub_date": "2026-08-04T12:00:00+00:00",
        "summary": "Example summary.",
        "title": "Example title",
        "sentiment": 0,
    }
    payload.update(overrides)
    return payload


def build_search_payload(**overrides):
    return {"as_dicts": [build_article_payload(**overrides)], "as_string": None}


POPULATED_WIKIDATA_ENTITIES = {
    "Person": [
        {
            "title": "Ada Lovelace",
            "qid": "Q7259",
            "relevance": 0.97,
            "description": "English mathematician and writer",
            "source_mention": "Lovelace",
        },
        {
            "title": "Charles Babbage",
            "qid": "Q46633",
            "relevance": 0.81,
            "description": "English mathematician and inventor",
            "source_mention": "Babbage",
        },
    ],
    "Organization": [
        {
            "title": "Analytical Engine",
            "qid": "Q332676",
            "relevance": 0.65,
            "description": "mechanical general-purpose computer",
            "source_mention": "the Engine",
        }
    ],
}


def test_missing_wikidata_entities_parses_to_none():
    response = SearchResponse.model_validate(build_search_payload())

    article = response.as_dicts[0]
    assert isinstance(article, SearchResponseDictItem)
    assert article.wikidata_entities is None


def test_explicit_null_wikidata_entities_parses_to_none():
    response = SearchResponse.model_validate(build_search_payload(wikidata_entities=None))

    assert response.as_dicts[0].wikidata_entities is None


def test_empty_mapping_is_preserved_and_not_coerced_to_none():
    response = SearchResponse.model_validate(build_search_payload(wikidata_entities={}))

    article = response.as_dicts[0]
    assert article.wikidata_entities == {}
    assert article.wikidata_entities is not None


def test_populated_mapping_with_multiple_groups_and_entities():
    response = SearchResponse.model_validate(
        build_search_payload(wikidata_entities=copy.deepcopy(POPULATED_WIKIDATA_ENTITIES))
    )

    wikidata_entities = response.as_dicts[0].wikidata_entities
    assert set(wikidata_entities) == {"Person", "Organization"}
    assert len(wikidata_entities["Person"]) == 2
    assert len(wikidata_entities["Organization"]) == 1

    ada = wikidata_entities["Person"][0]
    assert isinstance(ada, WikidataEntity)
    assert ada.title == "Ada Lovelace"
    assert ada.qid == "Q7259"
    assert ada.relevance == pytest.approx(0.97)
    assert ada.description == "English mathematician and writer"
    assert ada.source_mention == "Lovelace"


def test_optional_description_and_source_mention_may_be_omitted():
    response = SearchResponse.model_validate(
        build_search_payload(
            wikidata_entities={"Person": [{"title": "Ada Lovelace", "qid": "Q7259", "relevance": 1.0}]}
        )
    )

    entity = response.as_dicts[0].wikidata_entities["Person"][0]
    assert entity.description is None
    assert entity.source_mention is None


def test_empty_entity_group_list_is_preserved():
    response = SearchResponse.model_validate(build_search_payload(wikidata_entities={"Person": []}))

    assert response.as_dicts[0].wikidata_entities == {"Person": []}


def test_round_trip_serialization_preserves_populated_mapping():
    payload = build_search_payload(wikidata_entities=copy.deepcopy(POPULATED_WIKIDATA_ENTITIES))

    response = SearchResponse.model_validate(payload)
    dumped = response.model_dump(mode="json")
    reparsed = SearchResponse.model_validate_json(response.model_dump_json())

    assert dumped["as_dicts"][0]["wikidata_entities"] == POPULATED_WIKIDATA_ENTITIES
    assert reparsed.as_dicts[0].wikidata_entities == response.as_dicts[0].wikidata_entities


@pytest.mark.parametrize("value", [None, {}, POPULATED_WIKIDATA_ENTITIES])
def test_round_trip_serialization_is_lossless(value):
    payload = build_search_payload(wikidata_entities=copy.deepcopy(value))

    response = SearchResponse.model_validate(payload)
    reparsed = SearchResponse.model_validate(response.model_dump(mode="json"))

    assert reparsed.as_dicts[0].wikidata_entities == response.as_dicts[0].wikidata_entities
    assert reparsed.model_dump(mode="json")["as_dicts"][0]["wikidata_entities"] == value


def test_absent_field_is_not_synthesized_on_dump():
    """A response without the property must not gain fabricated entity groups."""
    response = SearchResponse.model_validate(build_search_payload())

    dumped = response.model_dump(mode="json")
    assert dumped["as_dicts"][0]["wikidata_entities"] is None
    assert (
        "wikidata_entities" not in response.model_dump(mode="json", exclude_none=True)["as_dicts"][0]
    )


def test_other_article_fields_are_unaffected():
    response = SearchResponse.model_validate(
        build_search_payload(wikidata_entities=copy.deepcopy(POPULATED_WIKIDATA_ENTITIES))
    )

    article = response.as_dicts[0]
    assert article.entities.Person == ["Ada Lovelace"]
    assert article.title == "Example title"
    assert article.as_string_key == "0"
