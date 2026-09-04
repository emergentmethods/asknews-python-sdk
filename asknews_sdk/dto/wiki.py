from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_serializer

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


class _WikidataValue(BaseModel):
    """Base for the nested property-value shapes.

    Two settings, both load-bearing:

    * ``extra="allow"`` -- the API attaches per-property context keys to these
      entries (``for_work`` on awards, ``kinship`` on relatives,
      ``character_role``/``character_name`` on cast members), and new ones can
      appear without warning. Keeping extras means a newly served qualifier
      reaches you as an attribute on ``model_extra`` instead of raising.
    * ``_drop_none`` -- the API omits absent qualifiers rather than sending
      nulls, and re-serializing one of these models keeps that shape, so a
      round trip does not invent keys the API never sent.
    """

    model_config = ConfigDict(extra="allow")

    @model_serializer(mode="wrap")
    def _drop_none(self, handler):
        return {k: v for k, v in handler(self).items() if v is not None}


class WikidataQidRef(_WikidataValue):
    """A QID-valued claim -- the element type of most metadata fields.

    Most QID fields list EVERY claim, not just the current one: ``ceo`` carries
    former officeholders alongside the incumbent. Which entry is current is
    yours to decide -- ``rank`` marks it when an editor has set one, but is
    often left "normal" throughout, and a missing ``end_time`` does not imply
    currency (an announced successor has none either).

    A few fields are list-shaped but store only ONE entry; they are marked
    ``[one entry]`` on the field below. Do not read a list's length as a count
    without checking.
    """

    qid: str
    label: str
    # Temporal qualifiers, present on time-bounded roles such as ceo,
    # position_held or member_of. Dating rates vary enormously by property, so
    # `end_time is None` means "current OR undated".
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    # The point-in-time counterpart to the start/end interval -- the only date
    # a point event carries (an award has a year, not a range).
    point_in_time: Optional[str] = None
    # Wikidata claim rank: "preferred" | "normal".
    rank: Optional[str] = None


class WikidataQuantity(_WikidataValue):
    """A quantity claim, with its unit and attribution qualifiers.

    The unit is not decoration -- revenue in EUR and USD are otherwise silently
    mixed in one field. ``platform``/``account_id``/``point_in_time`` attribute
    the value: ``social_media_followers`` carries one claim per account per
    snapshot, so a bare number cannot be attributed, ordered or summed without
    double-counting the same account at two dates.
    """

    amount: float
    unit_qid: Optional[str] = None
    unit_label: Optional[str] = None
    # A plain platform name ("X (Twitter)", "YouTube"), not a QID.
    platform: Optional[str] = None
    account_id: Optional[str] = None
    point_in_time: Optional[str] = None


class WikidataMonolingualText(_WikidataValue):
    """A language-tagged text value (e.g. official_name)."""

    text: str
    language: Optional[str] = None


class WikidataCoordinate(_WikidataValue):
    """A globe-coordinate value."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None


class WikidataMetadata(BaseModel):
    """Wikidata entity metadata.

    A typed core plus every Wikidata property the API returns. ``extra="allow"``
    is kept so a newly added property still reaches you (via ``model_extra``)
    before this SDK is updated to name it.

    Almost every field is absent on any given entity -- a person has no
    ``capital``, a city no ``date_of_birth`` -- so read defensively and expect
    ``None``. The trailing comment on each line is the Wikidata property id,
    for lookup at wikidata.org/wiki/Property:<id>.
    """

    model_config = ConfigDict(extra="allow")

    # ---- Core: not property-table entries ----------------------------------
    # {lang: article title} for every Wikipedia the entity links to. Build a URL
    # with f"https://{lang}.wikipedia.org/wiki/{title}".
    wikipedia_titles: Optional[Dict[str, str]] = None
    # Count of ALL sitelinks, including sister projects and languages absent
    # from wikipedia_titles.
    sitelink_count: Optional[int] = None
    # True when the entity is a class/type (it has subclass_of).
    is_class: Optional[bool] = None
    alt_labels: Optional[Dict[str, str]] = None
    aliases: Optional[List[str]] = None
    # Normalized registered domain of official_website, for exact-match lookup
    # -- scheme/www/trailing-slash variants make the raw URL an unreliable key.
    official_website_domain: Optional[str] = None
    # Revision metadata for the source Wikidata item.
    lastrevid: Optional[int] = None
    last_modified: Optional[str] = None

    # ---- Every extracted Wikidata property ---------------------------------

    # List[WikidataQidRef] -- normally EVERY claim, best-ranked first
    # (`ceo` carries former officeholders alongside the incumbent).
    # NOTE: the fields marked [one entry] below are list-shaped but
    # currently store a SINGLE entry -- the shape is held open so
    # restoring the full history stays non-breaking. Do not read
    # their length as a count.
    instance_of: Optional[List[WikidataQidRef]] = None  # P31
    subclass_of: Optional[List[WikidataQidRef]] = None  # P279
    spouse: Optional[List[WikidataQidRef]] = None  # P26
    child: Optional[List[WikidataQidRef]] = None  # P40
    sibling: Optional[List[WikidataQidRef]] = None  # P3373
    relative: Optional[List[WikidataQidRef]] = None  # P1038
    student_of: Optional[List[WikidataQidRef]] = None  # P1066
    doctoral_advisor: Optional[List[WikidataQidRef]] = None  # P184
    country_of_citizenship: Optional[List[WikidataQidRef]] = None  # P27
    gender: Optional[List[WikidataQidRef]] = None  # P21
    occupation: Optional[List[WikidataQidRef]] = None  # P106
    academic_degree: Optional[List[WikidataQidRef]] = None  # P512
    noble_title: Optional[List[WikidataQidRef]] = None  # P97
    medical_condition: Optional[List[WikidataQidRef]] = None  # P1050
    employer: Optional[List[WikidataQidRef]] = None  # P108
    educated_at: Optional[List[WikidataQidRef]] = None  # P69
    position_held: Optional[List[WikidataQidRef]] = None  # P39
    member_of: Optional[List[WikidataQidRef]] = None  # P463
    awards: Optional[List[WikidataQidRef]] = None  # P166
    notable_work: Optional[List[WikidataQidRef]] = None  # P800
    field_of_work: Optional[List[WikidataQidRef]] = None  # P101
    political_party: Optional[List[WikidataQidRef]] = None  # P102
    religion: Optional[List[WikidataQidRef]] = None  # P140
    native_language: Optional[List[WikidataQidRef]] = None  # P103
    cause_of_death: Optional[List[WikidataQidRef]] = None  # P509
    legislative_body: Optional[List[WikidataQidRef]] = None  # P194
    electoral_district: Optional[List[WikidataQidRef]] = None  # P768
    candidacy_in_election: Optional[List[WikidataQidRef]] = None  # P3602
    appointed_by: Optional[List[WikidataQidRef]] = None  # P748
    replaced_by: Optional[List[WikidataQidRef]] = None  # P1366
    replaces: Optional[List[WikidataQidRef]] = None  # P1365
    diplomatic_relation: Optional[List[WikidataQidRef]] = None  # P530
    executive_body: Optional[List[WikidataQidRef]] = None  # P208
    judicial_branch: Optional[List[WikidataQidRef]] = None  # P209
    flag: Optional[List[WikidataQidRef]] = None  # P163
    territory_claimed_by: Optional[List[WikidataQidRef]] = None  # P1336
    political_alignment: Optional[List[WikidataQidRef]] = None  # P1387
    political_ideology: Optional[List[WikidataQidRef]] = None  # P1142
    headquarters: Optional[List[WikidataQidRef]] = None  # P159
    ceo: Optional[List[WikidataQidRef]] = None  # P169
    chief_operating_officer: Optional[List[WikidataQidRef]] = None  # P1789
    founded_by: Optional[List[WikidataQidRef]] = None  # P112
    parent_organization: Optional[List[WikidataQidRef]] = None  # P749
    industry: Optional[List[WikidataQidRef]] = None  # P452
    stock_exchange: Optional[List[WikidataQidRef]] = None  # P414
    legal_form: Optional[List[WikidataQidRef]] = None  # P1454
    owned_by: Optional[List[WikidataQidRef]] = None  # P127
    subsidiary: Optional[List[WikidataQidRef]] = None  # P355
    chairperson: Optional[List[WikidataQidRef]] = None  # P488
    board_member: Optional[List[WikidataQidRef]] = None  # P3320
    merged_into: Optional[List[WikidataQidRef]] = None  # P7888
    partnership_with: Optional[List[WikidataQidRef]] = None  # P1327
    beneficial_owner: Optional[List[WikidataQidRef]] = None  # P12621
    significant_person: Optional[List[WikidataQidRef]] = None  # P3342
    country: Optional[List[WikidataQidRef]] = None  # P17
    located_in: Optional[List[WikidataQidRef]] = None  # P131
    capital: Optional[List[WikidataQidRef]] = None  # P36
    official_language: Optional[List[WikidataQidRef]] = None  # P37
    basic_form_of_government: Optional[List[WikidataQidRef]] = None  # P122
    language_used: Optional[List[WikidataQidRef]] = None  # P2936
    head_of_government: Optional[List[WikidataQidRef]] = None  # P6
    head_of_state: Optional[List[WikidataQidRef]] = None  # P35
    part_of: Optional[List[WikidataQidRef]] = None  # P361
    author: Optional[List[WikidataQidRef]] = None  # P50
    director: Optional[List[WikidataQidRef]] = None  # P57
    genre: Optional[List[WikidataQidRef]] = None  # P136
    cast_member: Optional[List[WikidataQidRef]] = None  # P161
    original_language: Optional[List[WikidataQidRef]] = None  # P364
    crew: Optional[List[WikidataQidRef]] = None  # P1029
    operator: Optional[List[WikidataQidRef]] = None  # P137
    launch_vehicle: Optional[List[WikidataQidRef]] = None  # P375  [one entry]
    manufacturer: Optional[List[WikidataQidRef]] = None  # P176
    brand: Optional[List[WikidataQidRef]] = None  # P1716
    product_or_material_produced: Optional[List[WikidataQidRef]] = None  # P1056
    part_of_series: Optional[List[WikidataQidRef]] = None  # P179
    developer: Optional[List[WikidataQidRef]] = None  # P178
    platform: Optional[List[WikidataQidRef]] = None  # P400
    material_used: Optional[List[WikidataQidRef]] = None  # P186
    operating_system: Optional[List[WikidataQidRef]] = None  # P306
    license: Optional[List[WikidataQidRef]] = None  # P275
    cpu: Optional[List[WikidataQidRef]] = None  # P880
    gpu: Optional[List[WikidataQidRef]] = None  # P2560
    director_manager: Optional[List[WikidataQidRef]] = None  # P1037
    sponsor: Optional[List[WikidataQidRef]] = None  # P859
    participant_in: Optional[List[WikidataQidRef]] = None  # P1344
    significant_event: Optional[List[WikidataQidRef]] = None  # P793
    sport: Optional[List[WikidataQidRef]] = None  # P641
    league: Optional[List[WikidataQidRef]] = None  # P118
    member_of_sports_team: Optional[List[WikidataQidRef]] = None  # P54
    coach: Optional[List[WikidataQidRef]] = None  # P286
    sports_season: Optional[List[WikidataQidRef]] = None  # P3450
    winner: Optional[List[WikidataQidRef]] = None  # P1346
    participant: Optional[List[WikidataQidRef]] = None  # P710
    country_of_origin: Optional[List[WikidataQidRef]] = None  # P495
    conflict: Optional[List[WikidataQidRef]] = None  # P607
    ethnic_group: Optional[List[WikidataQidRef]] = None  # P172
    currency: Optional[List[WikidataQidRef]] = None  # P38
    convicted_of: Optional[List[WikidataQidRef]] = None  # P1399
    penalty: Optional[List[WikidataQidRef]] = None  # P1596
    charge: Optional[List[WikidataQidRef]] = None  # P1595
    victim: Optional[List[WikidataQidRef]] = None  # P8032
    perpetrator: Optional[List[WikidataQidRef]] = None  # P8031
    jurisdiction: Optional[List[WikidataQidRef]] = None  # P1001
    investigated_by: Optional[List[WikidataQidRef]] = None  # P1840
    discoverer_or_inventor: Optional[List[WikidataQidRef]] = None  # P61
    location_of_discovery: Optional[List[WikidataQidRef]] = None  # P189
    approved_by: Optional[List[WikidataQidRef]] = None  # P790
    military_branch: Optional[List[WikidataQidRef]] = None  # P241
    military_rank: Optional[List[WikidataQidRef]] = None  # P410
    armament: Optional[List[WikidataQidRef]] = None  # P520
    commanded_by: Optional[List[WikidataQidRef]] = None  # P4791
    military_unit: Optional[List[WikidataQidRef]] = None  # P7779
    producer: Optional[List[WikidataQidRef]] = None  # P162
    screenwriter: Optional[List[WikidataQidRef]] = None  # P58
    composer: Optional[List[WikidataQidRef]] = None  # P86
    performer: Optional[List[WikidataQidRef]] = None  # P175
    record_label: Optional[List[WikidataQidRef]] = None  # P264
    distributor: Optional[List[WikidataQidRef]] = None  # P750
    production_company: Optional[List[WikidataQidRef]] = None  # P272
    collection: Optional[List[WikidataQidRef]] = None  # P195
    creator: Optional[List[WikidataQidRef]] = None  # P170
    iucn_conservation_status: Optional[List[WikidataQidRef]] = None  # P141  [one entry]
    climate_classification: Optional[List[WikidataQidRef]] = None  # P2564
    source_of_energy: Optional[List[WikidataQidRef]] = None  # P618
    seismic_classification: Optional[List[WikidataQidRef]] = None  # P9235
    named_after: Optional[List[WikidataQidRef]] = None  # P138
    different_from: Optional[List[WikidataQidRef]] = None  # P1889
    has_parts: Optional[List[WikidataQidRef]] = None  # P527
    follows: Optional[List[WikidataQidRef]] = None  # P155
    followed_by: Optional[List[WikidataQidRef]] = None  # P156

    # WikidataQidRef -- rival accounts of ONE fact, so only the
    # best-ranked claim is stored.
    place_of_birth: Optional[WikidataQidRef] = None  # P19
    place_of_death: Optional[WikidataQidRef] = None  # P20

    # List[WikidataQuantity] -- read unit_qid/unit_label before
    # comparing, and platform/account_id/point_in_time before summing.
    # NOTE: the fields marked [one entry] below are list-shaped but
    # currently store a SINGLE entry -- the shape is held open so
    # restoring the full history stays non-breaking. Do not read
    # their length as a count.
    social_media_followers: Optional[List[WikidataQuantity]] = None  # P8687
    number_of_subscribers: Optional[List[WikidataQuantity]] = None  # P3744  [one entry]
    number_of_employees: Optional[List[WikidataQuantity]] = None  # P1128  [one entry]
    total_revenue: Optional[List[WikidataQuantity]] = None  # P2139  [one entry]
    total_assets: Optional[List[WikidataQuantity]] = None  # P2403
    population: Optional[List[WikidataQuantity]] = None  # P1082  [one entry]
    payload_mass: Optional[List[WikidataQuantity]] = None  # P4519
    mass: Optional[List[WikidataQuantity]] = None  # P2067
    battery_capacity: Optional[List[WikidataQuantity]] = None  # P4140
    data_transfer_speed: Optional[List[WikidataQuantity]] = None  # P6711
    frequency: Optional[List[WikidataQuantity]] = None  # P2144
    number_of_processor_cores: Optional[List[WikidataQuantity]] = None  # P1141
    storage_capacity: Optional[List[WikidataQuantity]] = None  # P2928
    engine_displacement: Optional[List[WikidataQuantity]] = None  # P8628  [one entry]
    wheelbase: Optional[List[WikidataQuantity]] = None  # P3039
    width: Optional[List[WikidataQuantity]] = None  # P2049
    height: Optional[List[WikidataQuantity]] = None  # P2048
    length: Optional[List[WikidataQuantity]] = None  # P2043
    speed: Optional[List[WikidataQuantity]] = None  # P2052
    torque: Optional[List[WikidataQuantity]] = None  # P2230
    power: Optional[List[WikidataQuantity]] = None  # P2109
    duration: Optional[List[WikidataQuantity]] = None  # P2047
    richter_magnitude: Optional[List[WikidataQuantity]] = None  # P2528
    number_of_deaths: Optional[List[WikidataQuantity]] = None  # P1120
    number_of_casualties: Optional[List[WikidataQuantity]] = None  # P1590
    number_of_injured: Optional[List[WikidataQuantity]] = None  # P1339
    range: Optional[List[WikidataQuantity]] = None  # P2073
    number_produced: Optional[List[WikidataQuantity]] = None  # P1092  [one entry]
    box_office: Optional[List[WikidataQuantity]] = None  # P2142
    budget: Optional[List[WikidataQuantity]] = None  # P2130
    carbon_footprint: Optional[List[WikidataQuantity]] = None  # P5991

    # str -- an ISO-ish time string; rival precisions of ONE date
    # collapse to the best-ranked claim.
    date_of_birth: Optional[str] = None  # P569
    date_of_death: Optional[str] = None  # P570
    dissolved: Optional[str] = None  # P576
    inception: Optional[str] = None  # P571
    date_of_official_opening: Optional[str] = None  # P1619

    # List[str] -- ISO-ish time strings.
    # NOTE: the fields marked [one entry] below are list-shaped but
    # currently store a SINGLE entry -- the shape is held open so
    # restoring the full history stays non-breaking. Do not read
    # their length as a count.
    publication_date: Optional[List[str]] = None  # P577
    launch_date: Optional[List[str]] = None  # P619  [one entry]
    time_of_discovery: Optional[List[str]] = None  # P575
    service_entry: Optional[List[str]] = None  # P729  [one entry]
    service_retirement: Optional[List[str]] = None  # P730  [one entry]

    # List[WikidataMonolingualText] -- language-tagged values.
    short_name: Optional[List[WikidataMonolingualText]] = None  # P1813
    nickname: Optional[List[WikidataMonolingualText]] = None  # P1449
    native_label: Optional[List[WikidataMonolingualText]] = None  # P1705
    name_in_native_language: Optional[List[WikidataMonolingualText]] = None  # P1559
    official_name: Optional[List[WikidataMonolingualText]] = None  # P1448

    # List[str] -- ALWAYS a list: an identifier is a join key and
    # entities legitimately carry two (Alphabet has two SEC CIKs).
    x_twitter_username: Optional[List[str]] = None  # P2002
    facebook_id: Optional[List[str]] = None  # P2013
    instagram_username: Optional[List[str]] = None  # P2003
    youtube_channel_id: Optional[List[str]] = None  # P2397
    linkedin_company_or_organization_id: Optional[List[str]] = None  # P4264
    linkedin_personal_profile_id: Optional[List[str]] = None  # P6634
    telegram_username: Optional[List[str]] = None  # P3789
    tiktok_username: Optional[List[str]] = None  # P7085
    youtube_handle: Optional[List[str]] = None  # P11245
    mastodon_address: Optional[List[str]] = None  # P4033
    threads_username: Optional[List[str]] = None  # P11892
    vk_username: Optional[List[str]] = None  # P3185
    weibo_user_id: Optional[List[str]] = None  # P3579
    bluesky_handle: Optional[List[str]] = None  # P12361
    pinterest_username: Optional[List[str]] = None  # P3836
    twitch_username: Optional[List[str]] = None  # P5797
    tumblr_username: Optional[List[str]] = None  # P3943
    snapchat_username: Optional[List[str]] = None  # P2984
    reddit_username: Optional[List[str]] = None  # P4265
    bilibili_uid: Optional[List[str]] = None  # P6455
    discord_server_numeric_id: Optional[List[str]] = None  # P9345
    whatsapp_channel_id: Optional[List[str]] = None  # P12542
    wechat_id: Optional[List[str]] = None  # P7650
    truth_social_username: Optional[List[str]] = None  # P10858
    quora_username: Optional[List[str]] = None  # P4411
    douyin_username: Optional[List[str]] = None  # P7120
    gab_username: Optional[List[str]] = None  # P8919
    rednote_profile_id: Optional[List[str]] = None  # P12038
    rumble_channel: Optional[List[str]] = None  # P11962
    discord_username: Optional[List[str]] = None  # P9101
    subreddit: Optional[List[str]] = None  # P3984
    viaf_cluster_id: Optional[List[str]] = None  # P214
    isni: Optional[List[str]] = None  # P213
    gnd_id: Optional[List[str]] = None  # P227
    library_of_congress_authorities_id: Optional[List[str]] = None  # P244
    idref_id: Optional[List[str]] = None  # P269
    grid_id: Optional[List[str]] = None  # P2427
    sec_cik: Optional[List[str]] = None  # P5531
    duns_number: Optional[List[str]] = None  # P2771
    opensanctions_id: Optional[List[str]] = None  # P10632
    isin: Optional[List[str]] = None  # P946
    lei_code: Optional[List[str]] = None  # P1278
    swift_bic_code: Optional[List[str]] = None  # P2627
    imdb_id: Optional[List[str]] = None  # P345

    # str -- locale variants collapse to ONE site; the normalized
    # `official_website_domain` sibling in the core above is the match key.
    official_website: Optional[str] = None  # P856

    # List[str] -- Wikimedia Commons file URLs.
    image: Optional[List[str]] = None  # P18

    # WikidataCoordinate -- rival measurements of ONE point.
    coordinates: Optional[WikidataCoordinate] = None  # P625

    # List[str].
    ticker_symbol: Optional[List[str]] = None  # P249
    version: Optional[List[str]] = None  # P348


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
