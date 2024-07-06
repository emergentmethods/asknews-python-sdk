from typing import AsyncIterator, Dict, Iterator, List, Literal, Optional, Union

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.chat import (
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    CreateChatCompletionResponseStream,
    ForecastResponse,
    HeadlineQuestionsResponse,
    ListModelResponse,
)
from asknews_sdk.response import EventSource


class ChatAPI(BaseAPI):
    """
    Chat API

    https://add-docs.review.docs.asknews.app/en/reference#tag--chat
    """

    def get_chat_completions(
        self,
        messages: List[Dict[str, str]],
        model: Literal[
            "gpt-3.5-turbo-16k",
            "gpt-4-1106-preview",
            "open-mixtral-8x7b",
            "meta-llama/Meta-Llama-3-70B-Instruct",
            "claude-3-5-sonnet-20240620",
            "gpt-4o",
        ] = "gpt-3.5-turbo-16k",
        stream: bool = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> Union[CreateChatCompletionResponse, Iterator[CreateChatCompletionResponseStream]]:
        """
        Get chat completions for a given user message.

        https://docs.asknews.app/en/reference#post-/v1/openai/chat/completions

        :param messages: List of messages in the conversation.
        :type messages: List[Dict[str, str]]
        :param model: Model to use for chat completion, defaults to "gpt-3.5-turbo-16k"
        :type model: Literal[
            "gpt-3.5-turbo-16k", "gpt-4-1106-preview", "mistral-small",
            "mixtral-8x7b-32768"
        ]
        :param stream: Whether to stream the response, defaults to False
        :type stream: bool
        :param inline_citations: Inline citations format, defaults to "markdown_link"
        :type inline_citations: Literal["markdown_link", "numbered", "none"]
        :param append_references: Whether to append references, defaults to True
        :type append_references: bool
        :param asknews_watermark: Whether to add AskNews watermark, defaults to True
        :type asknews_watermark: bool
        :param journalist_mode: Whether to enable journalist mode, defaults to True
        :type journalist_mode: bool
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: Chat completions
        :rtype: Union[
            CreateChatCompletionResponse, Iterator[CreateChatCompletionResponseStream]
        ]
        """
        response = self.client.request(
            method="POST",
            endpoint="/v1/openai/chat/completions",
            body=CreateChatCompletionRequest(
                messages=messages,
                model=model,
                stream=stream,
                inline_citations=inline_citations,
                append_references=append_references,
                asknews_watermark=asknews_watermark,
                journalist_mode=journalist_mode,
                conversational_awareness=conversational_awareness,
            ).model_dump(mode="json"),
            headers={
                **(http_headers or {}),
                "Content-Type": CreateChatCompletionRequest.__content_type__,
            },
            accept=[
                (CreateChatCompletionResponse.__content_type__, 1.0),
                (CreateChatCompletionResponseStream.__content_type__, 1.0),
            ],
            stream=stream,
            stream_type="lines",
        )

        if stream:

            def _stream():
                for event in EventSource.from_api_response(response):
                    if event.content == "[DONE]":
                        break
                    yield CreateChatCompletionResponseStream.model_validate_json(event.content)

            return _stream()
        else:
            return CreateChatCompletionResponse.model_validate(response.content)

    def list_chat_models(self, *, http_headers: Optional[Dict] = None) -> ListModelResponse:
        """
        List available chat models.

        https://docs.asknews.app/en/reference#get-/v1/openai/models

        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: List of available chat models
        :rtype: ListModelResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/openai/models",
            headers=http_headers,
            accept=[(ListModelResponse.__content_type__, 1.0)],
        )
        return ListModelResponse.model_validate(response.content)

    def get_headline_questions(
        self,
        queries: Optional[List[str]] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> HeadlineQuestionsResponse:
        """
        Get headline questions for a given query.

        https://docs.asknews.app/en/reference#get-/v1/chat/questions

        :param queries: List of queries to get headline questions for
        :type queries: Optional[List[str]]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: Headline questions
        :rtype: HeadlineQuestionsResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/chat/questions",
            headers=http_headers,
            query={"queries": queries},
        )
        return HeadlineQuestionsResponse.model_validate(response.content)

    def get_forecast(
        self,
        query: str,
        lookback: int = 14,
        articles_to_use: int = 14,
        method: Literal["nl", "kw", "both"] = "kw",
        model: Literal[
            "gpt-4o", "claude-3-5-sonnet-20240620", "command-nightly"
        ] = "claude-3-5-sonnet-20240620",
        cutoff_date: Optional[str] = None,
        use_reddit: bool = False,
        additional_context: Optional[str] = None,
        web_search: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> ForecastResponse:
        """
        Get an expert forecast, complete with full sources
        and reasoning.

        https://docs.asknews.app/en/reference#get-/v1/chat/forecast
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/chat/forecast",
            headers=http_headers,
            query={
                "query": query,
                "lookback": lookback,
                "articles_to_use": articles_to_use,
                "method": method,
                "model": model,
                "cutoff_date": cutoff_date,
                "use_reddit": use_reddit,
                "additional_context": additional_context,
                "web_search": web_search,
            },
        )
        return ForecastResponse.model_validate(response.content)


class AsyncChatAPI(BaseAPI):
    """
    Chat API

    https://api.asknews.app/docs#tag/chat
    """

    async def get_chat_completions(
        self,
        messages: List[Dict[str, str]],
        model: Literal[
            "gpt-3.5-turbo-16k",
            "gpt-4-1106-preview",
            "open-mixtral-8x7b",
            "meta-llama/Meta-Llama-3-70B-Instruct",
            "claude-3-5-sonnet-20240620",
            "gpt-4o",
        ] = "gpt-3.5-turbo-16k",
        stream: bool = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> Union[CreateChatCompletionResponse, AsyncIterator[CreateChatCompletionResponseStream]]:
        """
        Get chat completions for a given user message.

        https://docs.asknews.app/en/reference#post-/v1/openai/chat/completions

        :param messages: List of messages in the conversation.
        :type messages: List[Dict[str, str]]
        :param model: Model to use for chat completion, defaults to "gpt-3.5-turbo-16k"
        :type model: Literal[
            "gpt-3.5-turbo-16k", "gpt-4-1106-preview", "mistral-small",
            "mixtral-8x7b-32768"
        ]
        :param stream: Whether to stream the response, defaults to False
        :type stream: bool
        :param inline_citations: Inline citations format, defaults to "markdown_link"
        :type inline_citations: Literal["markdown_link", "numbered", "none"]
        :param append_references: Whether to append references, defaults to True
        :type append_references: bool
        :param asknews_watermark: Whether to add AskNews watermark, defaults to True
        :type asknews_watermark: bool
        :param journalist_mode: Whether to enable journalist mode, defaults to True
        :type journalist_mode: bool
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: Chat completions
        :rtype: Union[
            CreateChatCompletionResponse,
            AsyncIterator[CreateChatCompletionResponseStream]
        ]
        """
        response = await self.client.request(
            method="POST",
            endpoint="/v1/openai/chat/completions",
            body=CreateChatCompletionRequest(
                messages=messages,
                model=model,
                stream=stream,
                inline_citations=inline_citations,
                append_references=append_references,
                asknews_watermark=asknews_watermark,
                journalist_mode=journalist_mode,
                conversational_awareness=conversational_awareness,
            ).model_dump(mode="json"),
            headers={
                "Content-Type": CreateChatCompletionRequest.__content_type__,
                **(http_headers or {}),
            },
            accept=[
                (CreateChatCompletionResponse.__content_type__, 1.0),
                (CreateChatCompletionResponseStream.__content_type__, 1.0),
            ],
            stream=stream,
            stream_type="lines",
        )

        if stream:

            async def _stream():
                async for event in EventSource.from_api_response(response):
                    if event.content == "[DONE]":
                        break
                    yield CreateChatCompletionResponseStream.model_validate_json(event.content)

            return _stream()
        else:
            return CreateChatCompletionResponse.model_validate(response.content)

    async def list_chat_models(self, *, http_headers: Optional[Dict] = None) -> ListModelResponse:
        """
        List available chat models.

        https://docs.asknews.app/en/reference#get-/v1/openai/models

        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: List of available chat models
        :rtype: ListModelResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/openai/models",
            headers=http_headers,
            accept=[(ListModelResponse.__content_type__, 1.0)],
        )
        return ListModelResponse.model_validate(response.content)

    async def get_headline_questions(
        self,
        queries: Optional[List[str]] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> HeadlineQuestionsResponse:
        """
        Get headline questions for a given query.

        https://docs.asknews.app/en/reference#get-/v1/chat/questions

        :param queries: List of queries to get headline questions for
        :type queries: Optional[List[str]]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: Headline questions
        :rtype: HeadlineQuestionsResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/chat/questions",
            headers=http_headers,
            query={"queries": queries},
        )
        return HeadlineQuestionsResponse.model_validate(response.content)

    async def get_forecast(
        self,
        query: str,
        lookback: int = 14,
        articles_to_use: int = 14,
        method: Literal["nl", "kw", "both"] = "kw",
        model: Literal[
            "gpt-4o", "claude-3-5-sonnet-20240620", "command-nightly"
        ] = "claude-3-5-sonnet-20240620",
        cutoff_date: Optional[str] = None,
        use_reddit: bool = False,
        additional_context: Optional[str] = None,
        web_search: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> ForecastResponse:
        """
        Get an expert forecast, complete with full sources
        and reasoning.

        https://docs.asknews.app/en/reference#get-/v1/chat/forecast
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/chat/forecast",
            headers=http_headers,
            query={
                "query": query,
                "lookback": lookback,
                "articles_to_use": articles_to_use,
                "method": method,
                "model": model,
                "cutoff_date": cutoff_date,
                "use_reddit": use_reddit,
                "additional_context": additional_context,
                "web_search": web_search,
            },
        )
        return ForecastResponse.model_validate(response.content)
