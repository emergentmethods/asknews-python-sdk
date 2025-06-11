from typing import Generic, List, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    count: int
    next_page: Optional[int]
    previous_page: Optional[int]


class FilterParams(BaseModel):
    query: str = Field(
        "",
        description=(
            "Query string that can be any phrase, "
            "keyword, question, or paragraph. "
            "If method='nl', then this will be used "
            "as a natural language query. If method='kw', "
            "then this will be used as a direct keyword query."
            " This is not required, if it is not passed, then "
            "the search is based on the remaining filters only."
        ),
    )
    n_articles: int = Field(10, description="Number of articles to return")
    start_timestamp: Optional[int] = Field(None, description="Timestamp to start search from")
    end_timestamp: Optional[int] = Field(None, description="Timestamp to end search at")
    time_filter: Literal["crawl_date", "pub_date"] = Field(
        "crawl_date",
        description="Control which date type to filter on. 'crawl_date' is the date "
        "the article was crawled, 'pub_date' is the date the article was published.",
    )
    return_type: Literal["string", "dicts", "both"] = Field(
        "dicts",
        description=(
            "Type of return value. 'string' means "
            "that the return is prompt-optimized "
            "and ready to be immediately injected "
            "into any prompt. 'dicts' means that the "
            "return is a structured dictionary, containing "
            "additional metadata (like a classic news api). "
            "Can be 'string' or 'dicts', or 'both'. "
            "'string' guarantees the lowest-latency response "
            "'dicts' requires more I/O, therefore increases "
            "latency (very slightly, depending on your "
            "network connection)."
        ),
    )
    historical: bool = Field(
        False,
        description=(
            "Search on archive of historical news. "
            "Defaults to False, meaning that the search "
            "will only look through the most recent "
            "news (48 hours)"
        ),
    )
    method: Literal["nl", "kw", "both"] = Field(
        "kw",
        description=(
            "Method to use for searching. 'nl' means Natural "
            "Language, which is a string that can be any "
            "phrase, keyword, question, or paragraph that will "
            "be used for semantic search on the news. "
            "'kw' means Keyword, which can also be any keyword(s),"
            " phrase, or paragraph, however the search is a "
            "direct keyword search on the database. 'both' means both methods "
            "will be used and results will be ranked according to IRR. "
            "'both' may reduce latency by 10 pct in exchange "
            " for improved accuracy."
        ),
    )
    similarity_score_threshold: float = Field(
        0.5,
        description="Similarity score threshold to determine which"
        " articles to return. Lower means less similar results "
        " are allowed.",
    )
    offset: Union[int, str] = Field(
        0,
        description=(
            "Offset for pagination. The n_articles is your page size, "
            "while your offset is the number of articles to skip to get"
            " to your page of interest. For example, if you want to get page 3 "
            "for n_article page size of 10, you would set offset to 20."
        ),
    )
    categories: List[
        Literal[
            "All",
            "Business",
            "Crime",
            "Politics",
            "Science",
            "Sports",
            "Technology",
            "Military",
            "Health",
            "Entertainment",
            "Finance",
            "Culture",
            "Climate",
            "Environment",
            "World",
        ]
    ] = Field(["All"], description="Categories of news to filter on")
    doc_start_delimiter: str = Field(
        "<doc>", description="Document start delimiter for string return."
    )
    doc_end_delimiter: str = Field(
        "</doc>", description="Document end delimiter for string return."
    )
    provocative: Literal["unknown", "low", "medium", "high", "all"] = Field(
        "all",
        description="Filter articles based on how provocative they are deemed"
        " based on the use of provocative language and emotional vocabulary.",
    )
    reporting_voice: Union[
        List[
            Literal[
                "Objective",
                "Subjective",
                "Investigative",
                "Narrative",
                "Analytical",
                "Advocacy",
                "Conversational",
                "Satirical",
                "Emotive",
                "Explanatory",
                "Persuasive",
                "Sensational",
                "Unknown",
                "all",
            ]
        ],
        Literal[
            "Objective",
            "Subjective",
            "Investigative",
            "Narrative",
            "Analytical",
            "Advocacy",
            "Conversational",
            "Satirical",
            "Emotive",
            "Explanatory",
            "Persuasive",
            "Sensational",
            "Unknown",
            "all",
        ],
    ] = Field(["all"], description="Type of reporting voice to filer by.")
    domain_url: Optional[Union[List[str], str]] = Field(
        None,
        description="filter by domain(s) url of interest. "
        "This can be a single domain or a list of domains. "
        "For example, 'npr.org' or ['nature.com', 'npr.org']",
    )
    bad_domain_url: Optional[Union[List[str], str]] = Field(
        None,
        description="Domain blacklist. "
        "This can be a single domain or a list of domains. "
        "For example, 'npr.org' or ['nature.com', 'npr.org']",
    )
    page_rank: Optional[int] = Field(
        None, description="Maximum allowed page rank for returned articles."
    )
    diversify_sources: bool = Field(
        False,
        description="Ensure that the return set of articles are selected from diverse "
        "sources. This adds latency to the search, but attempts to balance the "
        "representation of sources by country and source origins. In summary, a net "
        "is cast around your search, then the diversity of sources is analyzed, "
        "and your final result matches the large net diversity distribution. "
        "This means that your search accuracy is reduced, but you gain more diverse "
        "perspectives.",
    )
    strategy: Literal["latest news", "news knowledge", "default"] = Field(
        "default",
        description="Strategy to use for searching. 'latest news' automatically sets"
        "method='nl', historical=False, and looks within the past 24 hours. "
        "'news knowledge' automatically sets method='kw', historical=True, and looks"
        " within the past 60 days. 'news knowledge' will increase latency due to the "
        " larger search space in the archive. Use 'default' if you want to control "
        " start_timestamp, end_timestamp, historical, and method.",
    )
    hours_back: int = Field(
        24,
        description="Can be set to easily control the look back on the search. "
        "This is the same as controlling the 'start_timestamp' parameter. "
        "The difference is that this is not a timestamp, it is the number of hours "
        "back to look from the current time. Defaults to 24 hours.",
    )
    string_guarantee: Optional[List[str]] = Field(
        None,
        description="If defined, the search will only occur on articles "
        "that contain strings in this list.",
    )
    string_guarantee_op: Literal["AND", "OR"] = Field(
        "AND", description="Operator to use for string guarantee list."
    )
    reverse_string_guarantee: Optional[List[str]] = Field(
        None,
        description="If defined, the search will only occur on articles "
        "that do not contain strings in this list.",
    )
    entity_guarantee: Optional[List[str]] = Field(
        None,
        description="Entity guarantee to filter by. This is a list of strings, "
        "where each string includes entity type and entity value separated by a "
        "colon. The first element is the entity type and the second element is "
        "the entity value. For example ['Location:Paris', 'Person:John']",
    )
    entity_guarantee_op: Literal["AND", "OR"] = Field(
        "OR", description="Operator to use for entity guarantee list."
    )
    return_graphs: bool = Field(
        False,
        description="Return graphs for the articles. Only available to " "Analyst tier and above.",
    )
    return_geo: bool = Field(
        False,
        description="Return GeoCoordinates associated with locations discussed"
        "  inside the articles. Only available to Analyst tier and above.",
    )
    languages: Optional[
        List[
            Literal[
                "en",
                "de",
                "es",
                "fr",
                "de",
                "it",
                "pt",
                "ru",
                "ar",
                "tr",
                "zh",
                "jp",
                "ko",
                "sv",
                "nl",
                "no",
                "da",
                "uk",
                "pl",
                "hi",
            ]
        ]
    ] = Field(
        None,
        description="Languages to filter by. This is the two-letter "
        "'set 1' of the ISO 639-1 standard. For example: English is 'en'.",
    )
    countries: Optional[List[str]] = Field(
        None,
        description="Source countries to filter by (this is only for the publisher location, "
        "not the locations mentioned in articles. For "
        "Locations mentioned in articles, refer to entity_guarantee)"
        ", countries must be the two-letter ISO country code"
        "For example: United States is 'US', France is 'FR', Sweden is 'SE'.",
    )
    countries_blacklist: Optional[List[str]] = Field(
        None,
        description="Source countries to blacklist from search "
        "(this is only for the publisher location, "
        "not the locations mentioned in articles. For Locations mentioned in articles, "
        "refer to reverse_entity_guarantee)"
        ", countries must be the two-letter ISO country code"
        "For example: United States is 'US', France is 'FR', Sweden is 'SE'.",
    )
    continents: Optional[
        List[
            Literal[
                "Africa",
                "Asia",
                "Oceania",
                "Europe",
                "Middle East",
                "North America",
                "South America",
            ]
        ]
    ] = Field(None, description="Continents to filter by.")
    sentiment: Optional[Literal["negative", "neutral", "positive"]] = Field(
        None, description="Sentiment to filter articles by."
    )
    premium: bool = Field(False, description="Include premium sources.")

    class Config:
        extra = "forbid"
