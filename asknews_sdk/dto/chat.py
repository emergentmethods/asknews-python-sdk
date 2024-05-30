from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel
from typing_extensions import Annotated

from asknews_sdk.dto.base import BaseSchema


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


class HeadlineQuestionsResponse(BaseSchema, RootModel[Dict[str, List[str]]]):
    ...
