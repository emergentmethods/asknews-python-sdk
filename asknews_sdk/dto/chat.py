from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, HttpUrl, RootModel
from typing_extensions import Annotated

from asknews_sdk.dto.base import BaseSchema
from asknews_sdk.dto.news import SearchResponseDictItem


class CreateChatCompletionRequestMessage(BaseModel):
    role: Annotated[str, Field(title="Role")]
    content: Annotated[str, Field(title="Content")]
    name: Annotated[Optional[str], Field(None, title="Name")]
    function_call: Annotated[Optional[Dict[str, Any]], Field(None, title="Function Call")]


class CreateChatCompletionResponseChoice(BaseModel):
    index: Annotated[int, Field(title="Index")]
    message: CreateChatCompletionRequestMessage
    finish_reason: Annotated[Optional[str], Field(None, title="Finish Reason")]


class CreateChatCompletionResponseStreamChoice(BaseModel):
    index: Annotated[int, Field(title="Index")]
    delta: CreateChatCompletionRequestMessage
    finish_reason: Annotated[Optional[str], Field(None, title="Finish Reason")]


class CreateChatCompletionResponseUsage(BaseModel):
    prompt_tokens: Annotated[int, Field(title="Prompt Tokens")]
    completion_tokens: Annotated[int, Field(title="Completion Tokens")]
    total_tokens: Annotated[int, Field(title="Total Tokens")]


class CreateChatCompletionRequest(BaseSchema):
    model_config = ConfigDict(
        extra="allow",
    )
    model: Annotated[Optional[str], Field("gpt-3.5-turbo-16k", title="Model")]
    messages: Annotated[List[CreateChatCompletionRequestMessage], Field(title="Messages")]
    temperature: Annotated[Optional[float], Field(0.9, title="Temperature")]
    top_p: Annotated[Optional[float], Field(1.0, title="Top P")]
    n: Annotated[Optional[int], Field(1, title="N")]
    stream: Annotated[Optional[bool], Field(False, title="Stream")]
    stop: Annotated[Optional[Union[str, List[str]]], Field(None, title="Stop")]
    max_tokens: Annotated[Optional[int], Field(9999, title="Max Tokens")]
    presence_penalty: Annotated[Optional[int], Field(0, title="Presence Penalty")]
    frequency_penalty: Annotated[Optional[int], Field(0, title="Frequency Penalty")]
    user: Annotated[Optional[str], Field(None, title="User")]
    inline_citations: Annotated[
        Optional[Literal["markdown_link", "numbered", "none"]],
        Field("markdown_link", title="Type of inline citation formatting."),
    ]
    journalist_mode: Annotated[
        Optional[bool],
        Field(
            True,
            title=(
                "Activate journalist mode, with improved alignment for making claims"
                "with supporting evidence. Improved journalistic style."
            ),
        ),
    ]
    asknews_watermark: Annotated[
        Optional[bool], Field(True, title='Append "Generated by AskNews AI" watermark')
    ]
    append_references: Annotated[Optional[bool], Field(True, title="Append References or not")]
    conversational_awareness: Annotated[
        Optional[bool], Field(False, title="Conversational Awareness")
    ]
    filter_params: Annotated[
        Optional[Dict[str, Any]],
        Field(None, title="Any filter param available on the /news endpoint."),
    ]


class CreateChatCompletionResponse(BaseSchema):
    id: Annotated[str, Field(title="Id")]
    created: Annotated[int, Field(title="Created")]
    object: Annotated[Optional[str], Field("chat.completion", title="Object")]
    model: Annotated[Optional[str], Field("gpt-3.5-turbo-16k", title="Model")]
    usage: CreateChatCompletionResponseUsage
    choices: Annotated[List[CreateChatCompletionResponseChoice], Field(title="Choices")]


class CreateChatCompletionResponseStream(BaseSchema):
    __content_type__ = "text/event-stream"

    id: Annotated[str, Field(title="Id")]
    created: Annotated[int, Field(title="Created")]
    object: Annotated[Optional[str], Field("chat.completion.chunk", title="Object")]
    model: Annotated[Optional[str], Field("gpt-3.5-turbo-16k", title="Model")]
    usage: CreateChatCompletionResponseUsage
    choices: Annotated[List[CreateChatCompletionResponseStreamChoice], Field(title="Choices")]


class ModelItem(BaseModel):
    id: Annotated[str, Field(title="Id")]
    object: Annotated[Optional[str], Field("model", title="Object")]
    created: Annotated[
        Optional[int],
        Field(
            default_factory=lambda: int(datetime.now(timezone.utc).timestamp()),
            title="Created",
        ),
    ]
    owned_by: Annotated[Optional[str], Field("asknews", title="Owned By")]


class ListModelResponse(BaseSchema):
    __content_type__ = "application/json"

    object: Annotated[Optional[str], Field("list", title="Object")]
    data: Annotated[List[ModelItem], Field(title="Data")]


class HeadlineQuestionsResponse(BaseSchema, RootModel[Dict[str, List[str]]]): ...


HttpUrlString = Annotated[HttpUrl, AfterValidator(lambda v: str(v))]


class KeyPerson(BaseModel):
    name: str
    role: str


class WebSearchResult(BaseModel):
    title: str
    url: HttpUrlString
    source: str
    published: str
    key_points: List[str]
    raw_text: str = ""
    as_string_key: Optional[str] = None


class WebSearchResponse(BaseModel):
    as_string: str
    as_dicts: List[WebSearchResult]


class ForecastResponse(BaseModel):
    forecast: str
    resolution_criteria: str
    date: datetime
    reasoning: str
    sources: List[SearchResponseDictItem]
    timeline: List[str]
    opposite_request: str
    confidence: float
    choice: Union[bool, str]
    llm_confidence: int
    model_used: str
    likelihood: str
    probability: int
    web_search_results: List[WebSearchResult]
    summary: str
    key_people: List[KeyPerson]
    key_facets: List[str]
    reconciled_information: str
    candidate_models: List[str]
    unique_information: str
    expert_information: Dict


class FilterParams(BaseModel):
    query: Annotated[
        str,
        "Query string that can be any phrase, "
        "keyword, question, or paragraph. The more descriptive the better. "
        "Treat this like a powerful google query. This is optional.",
    ] = ("",)
    categories: Annotated[
        List[
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
        ],
        "Categories of news to filter on",
    ] = (["All"],)
    reporting_voice: Annotated[
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
        "Type of reporting voice to filer by.",
    ] = (["all"],)
    strategy: Annotated[
        Literal["latest news", "news knowledge", "default"],
        "Strategy to use for searching. 'latest news' automatically sets"
        "method='nl', historical=False, and looks within the past 24 hours. "
        "'news knowledge' automatically sets method='kw', historical=True, and looks"
        " within the past 60 days. 'news knowledge' will increase latency due to the "
        " larger search space in the archive. Use 'default' if you want to control "
        " start_timestamp, end_timestamp, historical, and method.",
    ] = ("default",)
    hours_back: Annotated[
        int,
        "Can be set to easily control the look back on the search. "
        "This is the same as controlling the 'start_timestamp' parameter. "
        "The difference is that this is not a timestamp, it is the number of hours "
        "back to look from the current time. Defaults to 24 hours.",
    ] = (24,)
    string_guarantee: Annotated[
        Optional[List[str]],
        "If defined, the search will only occur on articles "
        "that contain strings in this list. This is powerful for "
        "constraining important names or concepts. It is optional.",
    ] = (None,)
    string_guarantee_op: Annotated[
        Literal["AND", "OR"],
        "Operator to use for string guarantee list. AND means all string_guarantee "
        "items must be present in all articles. OR means at least one of the items must "
        "be present.",
    ] = ("AND",)
    reverse_string_guarantee: Annotated[
        Optional[List[str]],
        "If defined, the search will only occur on articles "
        "that do not contain strings in this list. This is powerful "
        "for avoiding articles with a particular name or concept. It is optional.",
    ] = (None,)
    entity_guarantee: Annotated[
        Optional[List[str]],
        "Entities that must be present in the retrieved articles. This is a list of strings, "
        "where each string includes entity type and entity value separated by a "
        "colon. The first element is the entity type and the second element is "
        "the entity value. For example ['Location:Paris', 'Person:John']. "
        "Allowed entity types include: Location, Person, Organization, Product, Technology",
    ] = (None,)
    entity_guarantee_op: Annotated[
        Literal["AND", "OR"],
        "Operator to use for entity guarantee list. AND means all entity_guarantee "
        "items must be present in all articles. OR means at least one of the items "
        "must be present.",
    ] = ("OR",)
    countries: Annotated[
        Optional[List[str]],
        "Article source countries to filter by, this is the two-letter ISO country code"
        "For example: United States is 'US', France is 'FR', Sweden is 'SE'.",
    ] = (None,)
    continents: Annotated[
        Optional[
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
        ],
        "The articles must be geographically focused on this continent.",
    ] = (None,)
    sentiment: Annotated[
        Optional[Literal["negative", "neutral", "positive"]], "Sentiment to filter articles by."
    ] = None


class FilterParamsMetadata(BaseModel):
    title: str


class FilterParamsResponse(BaseModel):
    metadata: FilterParamsMetadata
    filter_params: FilterParams
