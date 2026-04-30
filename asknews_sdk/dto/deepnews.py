from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union, get_args
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict, Discriminator, Field, Tag
from typing_extensions import Annotated, TypeAlias

from asknews_sdk.dto.base import BaseSchema
from asknews_sdk.dto.chat import ChartResponse, WebSearchResult
from asknews_sdk.dto.news import SearchResponseDictItem


def object_discriminator(v: Any) -> str:
    if isinstance(v, dict):
        return v.get("object", "")
    return getattr(v, "object", "")


def kind_discriminator(v: Any) -> str:
    if isinstance(v, dict):
        return v.get("kind", "")
    return getattr(v, "kind", "")


class DeepNewsSources(BaseModel):
    news: Annotated[List[SearchResponseDictItem], Field(title="News")]
    web: Annotated[List[WebSearchResult], Field(title="Web")]
    charts: Annotated[List[ChartResponse], Field(title="Charts")]


class CreateDeepNewsRequestMessage(BaseModel):
    role: Annotated[str, Field(title="Role")]
    content: Annotated[str, Field(title="Content")]
    name: Annotated[Optional[str], Field(None, title="Name")]
    function_call: Annotated[Optional[Dict[str, Any]], Field(None, title="Function Call")]


class CreateDeepNewsResponseChoice(BaseModel):
    index: Annotated[int, Field(title="Index")]
    message: CreateDeepNewsRequestMessage
    finish_reason: Annotated[Optional[str], Field(None, title="Finish Reason")]


class CreateDeepNewsResponseStreamChoice(BaseModel):
    index: Annotated[int, Field(title="Index")]
    delta: CreateDeepNewsRequestMessage
    finish_reason: Annotated[Optional[str], Field(None, title="Finish Reason")]


class CreateDeepNewsResponseUsage(BaseModel):
    prompt_tokens: Annotated[int, Field(title="Prompt Tokens")]
    completion_tokens: Annotated[int, Field(title="Completion Tokens")]
    total_tokens: Annotated[int, Field(title="Total Tokens")]
    tool_usage: Annotated[Optional[Dict[str, int]], Field(None, title="Tool Usage")]


DeepNewsSourceType = Literal["asknews", "google", "graph", "wiki", "x", "reddit", "charts", "email"]
DeepNewsSourceTypeDefault: DeepNewsSourceType = "asknews"

DeepNewsInlineCitationType = Literal["markdown_link", "numbered", "none"]
DeepNewsInlineCitationTypeDefault: DeepNewsInlineCitationType = "markdown_link"


class CreateDeepNewsRequest(BaseSchema):
    model_config = ConfigDict(
        extra="allow",
    )
    messages: Annotated[
        List[CreateDeepNewsRequestMessage],
        Field(
            title=(
                "The messages to send to DeepNews. Each message should have 'role' and "
                "'content' keys. "
                "Use this to specify what research/monitoring task DeepNews should perform. The "
                "'content' for the final 'user' message should be your Alert query."
            )
        ),
    ]
    model: Annotated[
        Optional[str],
        Field(
            title=("The model to use for DeepNews research. Check API reference for default model.")
        ),
    ] = None
    filter_params: Annotated[
        Optional[Dict[str, Any]],
        Field(title="Any filter param available on the /news endpoint."),
    ] = None
    search_depth: Annotated[
        Optional[int],
        Field(
            title=("The search depth for deep research. Higher values mean more thorough research.")
        ),
    ] = 2
    max_depth: Annotated[Optional[int], Field(title="The maximum research depth allowed.")] = 10
    sources: Annotated[
        Optional[
            Union[
                DeepNewsSourceType,
                List[DeepNewsSourceType],
            ]
        ],
        Field(
            title=(
                "Which data sources DeepNews should query. Can be a single source or a list. "
                "Available sources are: "
                f"{', '.join(get_args(DeepNewsSourceType))}"
            ),
        ),
    ] = DeepNewsSourceTypeDefault
    inline_citations: Annotated[
        Optional[DeepNewsInlineCitationType],
        Field(
            title=(
                "How to format inline citations in the response. Defaults to: "
                f"{DeepNewsInlineCitationTypeDefault}. Available options: "
                f"{', '.join(get_args(DeepNewsInlineCitationType))}"
            )
        ),
    ] = DeepNewsInlineCitationTypeDefault
    start_citation_number: Annotated[
        Optional[int],
        Field(
            title=(
                "Starting number for inline citations. Offsets fetched source citation keys. "
                "Useful if you are providing the agent outside sources with numbered citation keys."
            )
        ),
    ] = 1
    return_sources: Annotated[
        Optional[bool],
        Field(title="Return all collected sources as objects as the last token of the stream."),
    ] = True
    only_cited_sources: Annotated[
        Optional[bool],
        Field(
            title=(
                "Whether to return only of sources that are cited/referenced in the generated "
                "response content."
            )
        ),
    ] = True
    append_references: Annotated[
        Optional[bool],
        Field(title="Whether to append a 'Cited Articles' section at the end of the response."),
    ] = True
    journalist_mode: Annotated[
        Optional[bool],
        Field(
            title=(
                "Activate journalist mode, with improved alignment for making claims"
                "with supporting evidence. Improved journalistic style."
            ),
        ),
    ] = True
    conversational_awareness: Annotated[
        Optional[bool], Field(title="Whether to use conversational awareness.")
    ] = False
    include_entities: Annotated[
        Optional[bool],
        Field(
            title=(
                "Include entities of the sources in the internal context. "
                "Activating this will increase internal token usage. "
                "This is useful if you want the LLM to better understand "
                "which entities are associated with which types in the context."
            ),
        ),
    ] = True
    include_graphs: Annotated[
        Optional[bool],
        Field(
            title=(
                "Include graphs of the sources in the internal context. "
                "Activating this will increase internal token usage. "
                "This is useful if you want the LLM to understand graph "
                "relationships between the entities in the sources."
            ),
        ),
    ] = False
    include_coordinates: Annotated[
        Optional[bool],
        Field(
            title=(
                "Include geocoordinates of the sources in the internal context. "
                "Activating this will increase internal token usage. "
                "This is useful if you need the LLM to report exact coordinates "
                "to you."
            ),
        ),
    ] = False
    asknews_watermark: Annotated[
        Optional[bool], Field(title="Append 'Generated by AskNews AI' watermark")
    ] = True
    stream: Annotated[
        Optional[bool], Field(title="Whether to stream the response as server-sent events.")
    ] = False
    stop: Annotated[
        Optional[Union[str, List[str]]],
        Field(title="Sequence(s) where the model will stop generating further tokens."),
    ] = None
    temperature: Annotated[
        Optional[float], Field(title="The temperature of the DeepNews agent model.")
    ] = 0.9
    top_p: Annotated[
        Optional[float],
        Field(
            title=(
                "Nucleus sampling parameter. Only tokens with cumulative probability up "
                "to top_p are considered."
            )
        ),
    ] = 1.0
    n: Annotated[Optional[int], Field(title="Number of completions to generate.")] = 1
    max_tokens: Annotated[
        Optional[int], Field(title="Maximum number of tokens to generate in the response.")
    ] = 9999
    presence_penalty: Annotated[
        Optional[int],
        Field(
            title=(
                "Penalizes new tokens based on whether they appear in the text so far, "
                "encouraging new topics."
            )
        ),
    ] = 0
    frequency_penalty: Annotated[
        Optional[int],
        Field(
            title=(
                "Penalizes new tokens based on their frequency in the text so far, "
                "reducing repetition."
            )
        ),
    ] = 0
    user: Annotated[
        Optional[str],
        Field(
            title=("A unique identifier for the end-user, useful for tracking and abuse detection.")
        ),
    ] = None
    thread_id: Annotated[
        Optional[UUID], Field(title="ID of an existing thread to continue the conversation.")
    ] = None
    engine: Annotated[
        Optional[Literal["v1", "v1.5", "v2.0"]],
        Field(
            title=(
                "Which engine to use for the DeepNews response. 'v1' is the original engine, while "
                "'v1.5' is an improved engine with better performance and capabilities. "
                "Check API reference for more details on the differences between the engines."
            )
        ),
    ] = "v1"
    max_parallel_tool_calls: Annotated[
        Optional[int],
        Field(
            default=1,
            ge=1,
            le=4,
            title=(
                "The maximum number of tool calls that can be executed in parallel. "
                "This is useful to limit the number of concurrent calls to external APIs "
                "or tools that the DeepNews agent might use during its research process."
            ),
        ),
    ] = 1
    enable_source_pruning: Annotated[
        Optional[bool],
        Field(
            title=(
                "Whether to enable source pruning during the research process. "
                "When enabled, the DeepNews agent will attempt to prune irrelevant sources "
                "from its context to optimize token usage and focus on the most relevant "
                "iinformation. This can lead to more efficient research and better responses, "
                "especially for complex queries with many sources."
            )
        ),
    ] = False
    cutoff_datetime: Annotated[
        Optional[Union[datetime, str]],
        Field(
            title=("The cutoff datetime to pass to the LLM for cutting off knowledge across tools.")
        ),
    ] = None


class CreateDeepNewsResponse(BaseSchema):
    id: Annotated[str, Field(title="Id")]
    created: Annotated[int, Field(title="Created")]
    object: Annotated[Optional[str], Field("chat.completion", title="Object")]
    model: Annotated[Optional[str], Field("deepseek", title="Model")]
    usage: CreateDeepNewsResponseUsage
    choices: Annotated[List[CreateDeepNewsResponseChoice], Field(title="Choices")]
    sources: Annotated[DeepNewsSources, Field(title="Sources")]


class CreateDeepNewsResponseStreamChunk(BaseSchema):
    __content_type__ = "text/event-stream"

    id: Annotated[str, Field(title="Id")]
    created: Annotated[int, Field(title="Created")]
    object: Annotated[Optional[str], Field("chat.completion.chunk", title="Object")]
    model: Annotated[Optional[str], Field("deepseek", title="Model")]
    usage: CreateDeepNewsResponseUsage
    choices: Annotated[List[CreateDeepNewsResponseStreamChoice], Field(title="Choices")]


class CreateDeepNewsResponseStreamSourcesNewsSource(BaseModel):
    kind: Literal["news"] = "news"
    data: SearchResponseDictItem


class CreateDeepNewsResponseStreamSourcesWebSource(BaseModel):
    kind: Literal["web"] = "web"
    data: WebSearchResult


class CreateDeepNewsResponseStreamSourcesGraphSource(BaseModel):
    kind: Literal["graph"] = "graph"
    data: AnyUrl


class CreateDeepNewsResponseStreamSourcesChartSource(BaseModel):
    kind: Literal["chart"] = "chart"
    data: ChartResponse


class CreateDeepNewsResponseStreamSource(BaseSchema):
    __content_type__ = "text/event-stream"

    id: Annotated[str, Field(title="Id")]
    created: Annotated[int, Field(title="Created")]
    object: Annotated[Optional[str], Field(title="Object")] = "chat.completion.sources"
    source: Annotated[
        Union[
            Annotated[CreateDeepNewsResponseStreamSourcesNewsSource, Tag("news")],
            Annotated[CreateDeepNewsResponseStreamSourcesWebSource, Tag("web")],
            Annotated[CreateDeepNewsResponseStreamSourcesGraphSource, Tag("graph")],
            Annotated[CreateDeepNewsResponseStreamSourcesChartSource, Tag("chart")],
        ],
        Field(title="Source"),
        Discriminator(kind_discriminator),
    ]


class CreateDeepNewsResponseStreamErrorDetails(BaseModel):
    code: Annotated[int, Field(title="Code")]
    message: Annotated[str, Field(title="Message")]


class CreateDeepNewsResponseStreamError(BaseSchema):
    __content_type__ = "text/event-stream"

    error: Annotated[CreateDeepNewsResponseStreamErrorDetails, Field(title="Error")]


CreateDeepNewsResponseStream: TypeAlias = Annotated[
    Union[
        Annotated[CreateDeepNewsResponseStreamChunk, Tag("chat.completion.chunk")],
        Annotated[CreateDeepNewsResponseStreamSource, Tag("chat.completion.source")],
    ],
    Discriminator(object_discriminator),
]


# ── v2.0 Anthropic-style content-block events ────────────────────────────────


def _event_type_discriminator(v: Any) -> str:
    if isinstance(v, dict):
        return v.get("type", "")
    return getattr(v, "type", "")


class AnthropicTextBlock(BaseModel):
    type: Literal["text"] = "text"
    text: str = ""


class AnthropicThinkingBlock(BaseModel):
    type: Literal["thinking"] = "thinking"
    thinking: str = ""


class AnthropicToolUseBlock(BaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: Dict[str, Any] = Field(default_factory=dict)


AnthropicContentBlock = Annotated[
    Union[
        Annotated[AnthropicTextBlock, Tag("text")],
        Annotated[AnthropicThinkingBlock, Tag("thinking")],
        Annotated[AnthropicToolUseBlock, Tag("tool_use")],
    ],
    Discriminator(_event_type_discriminator),
]


class AnthropicTextDelta(BaseModel):
    type: Literal["text_delta"] = "text_delta"
    text: str


class AnthropicThinkingDelta(BaseModel):
    type: Literal["thinking_delta"] = "thinking_delta"
    thinking: str


class AnthropicInputJsonDelta(BaseModel):
    type: Literal["input_json_delta"] = "input_json_delta"
    partial_json: str


AnthropicDeltaPayload = Annotated[
    Union[
        Annotated[AnthropicTextDelta, Tag("text_delta")],
        Annotated[AnthropicThinkingDelta, Tag("thinking_delta")],
        Annotated[AnthropicInputJsonDelta, Tag("input_json_delta")],
    ],
    Discriminator(_event_type_discriminator),
]


class MessageStartEvent(BaseModel):
    type: Literal["message_start"] = "message_start"
    role: Literal["assistant"] = "assistant"


class ContentBlockStartEvent(BaseModel):
    type: Literal["content_block_start"] = "content_block_start"
    index: int
    content_block: AnthropicContentBlock


class ContentBlockDeltaEvent(BaseModel):
    type: Literal["content_block_delta"] = "content_block_delta"
    index: int
    delta: AnthropicDeltaPayload


class ContentBlockStopEvent(BaseModel):
    type: Literal["content_block_stop"] = "content_block_stop"
    index: int


class MessageStopEvent(BaseModel):
    type: Literal["message_stop"] = "message_stop"


ContentBlockEvent = Annotated[
    Union[
        Annotated[MessageStartEvent, Tag("message_start")],
        Annotated[ContentBlockStartEvent, Tag("content_block_start")],
        Annotated[ContentBlockDeltaEvent, Tag("content_block_delta")],
        Annotated[ContentBlockStopEvent, Tag("content_block_stop")],
        Annotated[MessageStopEvent, Tag("message_stop")],
    ],
    Discriminator(_event_type_discriminator),
]


class CreateDeepNewsResponseStreamChoiceV2(BaseModel):
    index: Annotated[int, Field(title="Index")]
    delta: ContentBlockEvent
    finish_reason: Annotated[Optional[str], Field(None, title="Finish Reason")]


class CreateDeepNewsResponseStreamChunkV2(BaseSchema):
    """Chunk type yielded by engine='v2.0' streams."""

    __content_type__ = "text/event-stream"

    id: Annotated[str, Field(title="Id")]
    created: Annotated[int, Field(title="Created")]
    object: Annotated[Optional[str], Field("chat.completion.chunk", title="Object")]
    model: Annotated[Optional[str], Field(title="Model")] = None
    usage: CreateDeepNewsResponseUsage
    choices: Annotated[List[CreateDeepNewsResponseStreamChoiceV2], Field(title="Choices")]


CreateDeepNewsResponseStreamV2: TypeAlias = Annotated[
    Union[
        Annotated[CreateDeepNewsResponseStreamChunkV2, Tag("chat.completion.chunk")],
        Annotated[CreateDeepNewsResponseStreamSource, Tag("chat.completion.source")],
    ],
    Discriminator(object_discriminator),
]
