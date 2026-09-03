from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from asknews_sdk.dto.base import BaseSchema


class CirrusMetadata(BaseModel):
    create_timestamp: Optional[datetime] = None
    wikibase_item: Optional[str] = None
    version: Optional[int] = None
    popularity_score: Optional[float] = None
    text_bytes: Optional[int] = None
    heading: Optional[List[str]] = None
    incoming_links: Optional[int] = None
    outgoing_links: Optional[int] = None
    # other fields can be added as needed


class WikidataMetadata(BaseModel):
    """Wikidata entity metadata.
    """

    model_config = ConfigDict(extra="allow")

    # {lang: article title} for every Wikipedia the entity links to. Build a URL
    # with f"https://{lang}.wikipedia.org/wiki/{title}". Replaces the former
    # enwiki-only `wikipedia_url`, which was exactly the "en" entry.
    wikipedia_titles: Optional[Dict[str, str]] = None
    # Count of ALL sitelinks, including sister projects and languages absent
    # from wikipedia_titles.
    sitelink_count: Optional[int] = None
    # True when the entity is a class/type (it has P279 subclass_of).
    is_class: Optional[bool] = None
    # {lang: label} across the entity-resolution languages.
    alt_labels: Optional[Dict[str, str]] = None
    aliases: Optional[List[str]] = None
    # Normalized registered domain of official_website (P856).
    official_website_domain: Optional[str] = None

    # QID-valued fields list EVERY claim, not just the current one: `ceo` on a
    # company carries former officeholders alongside the incumbent. Each entry
    # is {qid, label, ...} plus whichever of start_time/end_time/point_in_time
    # and rank that claim carries — an absent qualifier is an absent key, so
    # read with .get(). Which entry is "current" is the caller's judgement from
    # those fields; Wikidata does not always mark it. Times are ISO-ish
    # strings; quantities are {amount, unit_qid, unit_label}.
    #
    # Keep as Any: a stricter annotation would fail the whole response.

    # Cross-cutting: present across most entity types.
    instance_of: Optional[Any] = None
    subclass_of: Optional[Any] = None
    part_of: Optional[Any] = None
    country: Optional[Any] = None
    official_website: Optional[Any] = None
    image: Optional[Any] = None
    inception: Optional[Any] = None
    dissolved: Optional[Any] = None
    # Entities Wikidata explicitly marks as confusable with this one (P1889).
    different_from: Optional[Any] = None

    # Person.
    date_of_birth: Optional[Any] = None
    date_of_death: Optional[Any] = None
    place_of_birth: Optional[Any] = None
    country_of_citizenship: Optional[Any] = None
    occupation: Optional[Any] = None
    employer: Optional[Any] = None
    position_held: Optional[Any] = None
    political_party: Optional[Any] = None
    educated_at: Optional[Any] = None
    notable_work: Optional[Any] = None
    awards: Optional[Any] = None
    member_of: Optional[Any] = None

    # Organization.
    headquarters: Optional[Any] = None
    ceo: Optional[Any] = None
    chairperson: Optional[Any] = None
    founded_by: Optional[Any] = None
    parent_organization: Optional[Any] = None
    owned_by: Optional[Any] = None
    subsidiary: Optional[Any] = None
    industry: Optional[Any] = None
    number_of_employees: Optional[Any] = None
    legal_form: Optional[Any] = None

    # Location.
    located_in: Optional[Any] = None
    coordinates: Optional[Any] = None
    population: Optional[Any] = None
    capital: Optional[Any] = None
    official_language: Optional[Any] = None
    head_of_government: Optional[Any] = None
    head_of_state: Optional[Any] = None
    currency: Optional[Any] = None
    basic_form_of_government: Optional[Any] = None

    # Event / conflict.
    participant: Optional[Any] = None
    winner: Optional[Any] = None
    conflict: Optional[Any] = None
    significant_event: Optional[Any] = None
    number_of_deaths: Optional[Any] = None
    victim: Optional[Any] = None
    perpetrator: Optional[Any] = None

    # Authority-control identifiers — the natural follow-on to entity linking:
    # cross-walking a resolved QID into library and archive catalogues.
    gnd_id: Optional[Any] = None
    library_of_congress_authorities_id: Optional[Any] = None
    viaf_cluster_id: Optional[Any] = None
    isni: Optional[Any] = None
    idref_id: Optional[Any] = None

    # Alternate names. Distinct from the core `aliases`/`alt_labels`: these are
    # property-table entries carrying language-tagged values.
    official_name: Optional[Any] = None
    native_label: Optional[Any] = None
    short_name: Optional[Any] = None

    # Common relations and social handles.
    has_parts: Optional[Any] = None
    named_after: Optional[Any] = None
    replaces: Optional[Any] = None
    x_twitter_username: Optional[Any] = None
    subreddit: Optional[Any] = None
    social_media_followers: Optional[Any] = None


class WikiResponseDictItem(BaseModel):
    content: str
    title: str
    url: str
    categories: List[str]
    timestamp: datetime
    cirrus_metadata: Optional[CirrusMetadata] = None
    point_id: Optional[str] = None
    has_main_section: Optional[bool] = None


class WikidataResponseDictItem(BaseModel):
    title: str
    description: Optional[str] = None
    qid: str
    relevance: Optional[float] = None
    wikidata_metadata: Optional[WikidataMetadata] = None


class WikiSearchResponse(BaseSchema):
    documents: List[WikiResponseDictItem]


class WikiBatchSearchResponse(BaseSchema):
    results: List[WikiSearchResponse]


class WikiLinkEntityResponse(BaseSchema):
    entity: str
    entity_type: Optional[str] = None
    linked_entity: Optional[WikidataResponseDictItem] = None
    candidates: Optional[List[WikidataResponseDictItem]] = None
    relevance_threshold: Optional[float] = None
    link_status: Literal["linked", "ambiguous", "no_match"]
    link_confidence: float


class WikiBatchLinkEntityRequest(BaseModel):
    entities: List[str]
    entity_types: Optional[List[Optional[str]]] = None
    entity_descriptions: Optional[List[Optional[str]]] = None
    relevance_threshold: Optional[float] = None
    ambiguity_margin: Optional[float] = None
    allow_ambiguous: bool = True
    include_candidates: bool = True

    @field_validator("entities")
    @classmethod
    def validate_entities_not_empty(cls, v):
        if any(e == "" for e in v):
            raise ValueError("entities must not contain empty strings")
        return v

    @field_validator("entity_types", "entity_descriptions")
    @classmethod
    def validate_lengths_match(cls, v, info):
        entities = info.data.get("entities")
        if v is not None and entities is not None and len(v) != len(entities):
            field = info.field_name
            raise ValueError(
                f"{field} length ({len(v)}) must match entities length ({len(entities)})"
            )
        return v


class WikiBatchLinkEntityResponse(BaseSchema):
    results: List[WikiLinkEntityResponse]


class WikiEntityResponse(BaseSchema):
    """Direct QID lookup. `entity` is None when the QID is not in the collection;
    a miss is reported as found=False rather than as an error."""

    qid: str
    entity: Optional[WikidataResponseDictItem] = None
    found: bool


class WikiBatchEntityRequest(BaseModel):
    qids: List[str]

    @field_validator("qids")
    @classmethod
    def validate_qids_not_empty(cls, v):
        if any(not q.strip() for q in v):
            raise ValueError("qids must not contain empty strings")
        return v


class WikiBatchEntityResponse(BaseSchema):
    results: List[WikiEntityResponse]
