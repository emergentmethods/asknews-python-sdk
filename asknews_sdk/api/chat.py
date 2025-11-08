from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Optional, Union, overload
from uuid import UUID

from pydantic import TypeAdapter

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.alert import AlertLog, AlertResponse, CreateAlertRequest, UpdateAlertRequest
from asknews_sdk.dto.chat import (
    ChartResponse,
    CreateChartRequest,
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    CreateChatCompletionResponseStream,
    CreateChatCompletionResponseStreamError,
    FilterParamsResponse,
    ForecastResponse,
    HeadlineQuestionsResponse,
    ListModelResponse,
    WebSearchResponse,
)
from asknews_sdk.dto.common import PaginatedResponse
from asknews_sdk.dto.deepnews import (
    CreateDeepNewsRequest,
    CreateDeepNewsResponse,
    CreateDeepNewsResponseStream,
    CreateDeepNewsResponseStreamChunk,
    CreateDeepNewsResponseStreamError,
    CreateDeepNewsResponseStreamSource,
)
from asknews_sdk.errors import APIError
from asknews_sdk.response import AsyncEventSource, EventSource


ChatModel = Literal[
    "gpt-4o-mini",
    "gpt-4-1106-preview",
    "open-mixtral-8x7b",
    "meta-llama/Meta-Llama-3-70B-Instruct",
    "meta-llama/Meta-Llama-3.1-70B-Instruct",
    "meta-llama/Meta-Llama-3.3-70B-Instruct",
    "meta-llama/Meta-Llama-3.1-405B-Instruct",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet-latest",
    "gpt-4o",
    "o3-mini",
]
DeepNewsModel = Literal[
    "gpt-5",
    "claude-3-7-sonnet-latest",
    "deepseek",
    "deepseek-basic",
    "deepseek-r1-0528",
    "o3-mini",
    "claude-sonnet-4-20250514",
    "claude-opus-4-20250514",
    "claude-sonnet-4-5-20250929",
    "gemini-2.5-pro",
    "o3",
]


class ChatAPI(BaseAPI[APIClient]):
    """
    Chat API

    https://add-docs.review.docs.asknews.app/en/reference#tag--chat
    """

    @overload
    def get_chat_completions(
        self,
        messages: List[Dict[str, str]],
        model: ChatModel = "gpt-4o-mini",
        stream: Literal[False] = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> CreateChatCompletionResponse: ...

    @overload
    def get_chat_completions(
        self,
        messages: List[Dict[str, str]],
        model: ChatModel = "gpt-4o-mini",
        stream: bool = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> Iterator[CreateChatCompletionResponseStream]: ...

    def get_chat_completions(
        self,
        messages: List[Dict[str, str]],
        model: ChatModel = "gpt-4o-mini",
        stream: bool = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> Union[CreateChatCompletionResponse, Iterator[CreateChatCompletionResponseStream]]:
        """
        Get chat completions for a given user message.

        https://docs.asknews.app/en/reference#post-/v1/openai/chat/completions

        :param messages: List of messages in the conversation.
        :type messages: List[Dict[str, str]]
        :param model: Model to use for chat completion, defaults to "gpt-3.5-turbo-16k"
        :type model: ChatModel
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
                filter_params=filter_params,
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

                    token = TypeAdapter(
                        Union[
                            CreateChatCompletionResponseStreamError,
                            CreateChatCompletionResponseStream,
                        ]
                    ).validate_json(event.content)

                    if isinstance(token, CreateChatCompletionResponseStreamError):
                        raise APIError(
                            response=response,
                            detail=token.error.message,
                            code=token.error.code,
                        )

                    yield token

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
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4.1-2025-04-14",
            "claude-3-5-sonnet-latest",
            "claude-3-5-sonnet-20240620",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-sonnet-4-5-20250929",
            "o3-mini",
            "o3",
        ] = "gpt-4.1-2025-04-14",
        cutoff_date: Optional[str] = None,
        use_reddit: bool = False,
        additional_context: Optional[str] = None,
        web_search: bool = False,
        expert: Literal["general", "sports"] = "general",
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
                "expert": expert,
            },
        )
        return ForecastResponse.model_validate(response.content)

    def live_web_search(
        self,
        queries: List[str],
        lookback: Optional[int] = None,
        domains: Optional[List[str]] = None,
        strict: Optional[bool] = False,
        offset: Optional[int] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WebSearchResponse:
        """
        Run a live websearch, results fully distilled and analyzed
        by LLMs

        https://docs.asknews.app/en/reference#get-/v1/chat/websearch
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/chat/websearch",
            headers=http_headers,
            query={
                "queries": queries,
                "lookback": lookback,
                "domains": domains,
                "strict": strict,
                "offset": offset,
            },
        )
        return WebSearchResponse.model_validate(response.content)

    def get_autofilter(
        self,
        query: str,
        *,
        http_headers: Optional[Dict] = None,
    ) -> FilterParamsResponse:
        """
        Generate filter parameters automatically for the AskNews API.

        The output from this can be passed to /news, /chat, /graph, and /forecast

        https://docs.asknews.app/en/reference#get-/v1/chat/autofilter
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/chat/autofilter",
            headers=http_headers,
            query={
                "query": query,
            },
        )
        return FilterParamsResponse.model_validate(response.content)

    def create_alert(
        self,
        payload: Union[CreateAlertRequest, Dict[str, Any]],
        *,
        http_headers: Optional[Dict] = None,
    ) -> AlertResponse:
        """
        Create an alert.

        https://docs.asknews.app/en/reference#post-/v1/chat/alerts

        :param payload: The alert payload.
        :type payload: CreateAlertRequest
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The created alert.
        :rtype: AlertResponse
        """
        response = self.client.request(
            method="POST",
            endpoint="/v1/chat/alerts",
            body=payload.model_dump(mode="json")
            if isinstance(payload, CreateAlertRequest)
            else payload,
            headers={
                **(http_headers or {}),
                "Content-Type": CreateAlertRequest.__content_type__,
            },
            accept=[
                (AlertResponse.__content_type__, 1.0),
            ],
        )
        return AlertResponse.model_validate(response.content)

    def get_alert(
        self,
        alert_id: Union[UUID, str],
        *,
        http_headers: Optional[Dict] = None,
    ) -> AlertResponse:
        """
        Get an alert.

        https://docs.asknews.app/en/reference#get-/v1/chat/alerts/{alert_id}

        :param alert_id: The alert ID.
        :type alert_id: Union[UUID, str]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: Alert details.
        :rtype: AlertResponse
        """
        response = self.client.request(
            method="GET",
            endpoint=f"/v1/chat/alerts/{alert_id}",
            headers=http_headers,
        )
        return AlertResponse.model_validate(response.content)

    def list_alerts(
        self,
        page: int = 1,
        per_page: int = 10,
        all: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> PaginatedResponse[AlertResponse]:
        """
        List alerts.

        https://docs.asknews.app/en/reference#get-/v1/chat/alerts

        :param page: The page number.
        :type page: int
        :param per_page: The number of items per page.
        :type per_page: int
        :param all: Whether to return all alerts.
        :type all: bool
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: List of alerts.
        :rtype: PaginatedResponse[AlertResponse]
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/chat/alerts",
            headers=http_headers,
            query={"page": page, "per_page": per_page, "all": all},
        )
        return PaginatedResponse[AlertResponse].model_validate(response.content)

    def update_alert(
        self,
        alert_id: Union[UUID, str],
        payload: Union[UpdateAlertRequest, Dict[str, Any]],
        *,
        http_headers: Optional[Dict] = None,
    ) -> AlertResponse:
        """
        Update an alert.

        https://docs.asknews.app/en/reference#put-/v1/chat/alerts/{alert_id}

        :param alert_id: The alert ID.
        :type alert_id: Union[UUID, str]
        :param payload: The alert payload.
        :type payload: UpdateAlertRequest
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The updated alert.
        :rtype: AlertResponse
        """
        response = self.client.request(
            method="PUT",
            endpoint=f"/v1/chat/alerts/{alert_id}",
            body=payload.model_dump(mode="json", exclude_unset=True)
            if isinstance(payload, UpdateAlertRequest)
            else payload,
            headers={
                **(http_headers or {}),
                "Content-Type": UpdateAlertRequest.__content_type__,
            },
            accept=[
                (AlertResponse.__content_type__, 1.0),
            ],
        )
        return AlertResponse.model_validate(response.content)

    def delete_alert(
        self,
        alert_id: Union[UUID, str],
        *,
        http_headers: Optional[Dict] = None,
    ) -> None:
        """
        Delete an alert.

        https://docs.asknews.app/en/reference#delete-/v1/chat/alerts/{alert_id}

        :param alert_id: The alert ID.
        :type alert_id: Union[UUID, str]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: None
        :rtype: None
        """
        self.client.request(
            method="DELETE",
            endpoint=f"/v1/chat/alerts/{alert_id}",
            headers=http_headers,
        )

    def list_alert_logs(
        self,
        alert_id: Union[UUID, str],
        page: int = 1,
        per_page: int = 10,
        all: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> PaginatedResponse[AlertLog]:
        """
        List alert logs.

        https://docs.asknews.app/en/reference#get-/v1/chat/alerts

        :param alert_id: The alert ID.
        :type alert_id: Union[UUID, str]
        :param page: The page number.
        :type page: int
        :param per_page: The number of items per page.
        :type per_page: int
        :param all: Whether to return all alerts.
        :type all: bool
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: List of alerts.
        :rtype: PaginatedResponse[AlertResponse]
        """
        response = self.client.request(
            method="GET",
            endpoint=f"/v1/chat/alerts/{alert_id}/logs",
            headers=http_headers,
            query={"page": page, "per_page": per_page, "all": all},
        )
        return PaginatedResponse[AlertLog].model_validate(response.content)

    @overload
    def get_deep_news(
        self,
        messages: List[Dict[str, str]],
        model: DeepNewsModel = "deepseek",
        stream: Literal[False] = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        sources: Optional[List[str]] = None,
        search_depth: int = 3,
        max_depth: int = 5,
        return_sources: bool = True,
        *,
        http_headers: Optional[Dict] = None,
    ) -> CreateDeepNewsResponse: ...

    @overload
    def get_deep_news(
        self,
        messages: List[Dict[str, str]],
        model: DeepNewsModel = "deepseek",
        stream: Literal[True] = True,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        sources: Optional[List[str]] = None,
        search_depth: int = 3,
        max_depth: int = 5,
        return_sources: bool = True,
        *,
        http_headers: Optional[Dict] = None,
    ) -> Iterator[CreateDeepNewsResponseStream]: ...

    def get_deep_news(
        self,
        messages: List[Dict[str, str]],
        model: DeepNewsModel = "deepseek",
        stream: bool = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        sources: Optional[List[str]] = None,
        search_depth: int = 3,
        max_depth: int = 5,
        return_sources: bool = True,
        *,
        http_headers: Optional[Dict] = None,
    ) -> Union[CreateDeepNewsResponse, Iterator[CreateDeepNewsResponseStream]]:
        """
        Get deep news research!

        https://docs.asknews.app/en/reference#post-/v1/openai/chat/deepnews
        """
        response = self.client.request(
            method="POST",
            endpoint="/v1/chat/deepnews",
            body=CreateDeepNewsRequest(
                messages=messages,
                model=model,
                stream=stream,
                inline_citations=inline_citations,
                append_references=append_references,
                asknews_watermark=asknews_watermark,
                journalist_mode=journalist_mode,
                conversational_awareness=conversational_awareness,
                filter_params=filter_params,
                sources=sources if sources else ["asknews"],
                search_depth=search_depth,
                max_depth=max_depth,
                return_sources=return_sources,
            ).model_dump(mode="json"),
            headers={
                **(http_headers or {}),
                "Content-Type": CreateDeepNewsRequest.__content_type__,
            },
            accept=[
                (CreateDeepNewsResponse.__content_type__, 1.0),
                (CreateDeepNewsResponseStreamChunk.__content_type__, 1.0),
                (CreateDeepNewsResponseStreamSource.__content_type__, 1.0),
            ],
            stream=stream,
            stream_type="lines",
        )

        if stream:

            def _stream():
                for event in EventSource.from_api_response(response):
                    if event.content == "[DONE]":
                        break

                    token = TypeAdapter(
                        Union[CreateDeepNewsResponseStreamError, CreateDeepNewsResponseStream]
                    ).validate_json(event.content)

                    if isinstance(token, CreateDeepNewsResponseStreamError):
                        raise APIError(
                            response=response,
                            detail=token.error.message,
                            code=token.error.code,
                        )

                    yield token

            return _stream()
        else:
            return CreateDeepNewsResponse.model_validate(response.content)

    def create_chart(
        self,
        payload: CreateChartRequest,
        *,
        http_headers: Optional[Dict] = None,
    ) -> ChartResponse:
        """
        Create a chart based on news data using a natural language query
        """

        response = self.client.request(
            method="POST",
            endpoint="/v1/chat/charts",
            body=payload.model_dump(mode="json")
            if isinstance(payload, CreateChartRequest)
            else payload,
            headers={
                **(http_headers or {}),
                "Content-Type": CreateChartRequest.__content_type__,
            },
            accept=[
                (ChartResponse.__content_type__, 1.0),
            ],
        )
        return ChartResponse.model_validate(response.content)


class AsyncChatAPI(BaseAPI[AsyncAPIClient]):
    """
    Chat API

    https://api.asknews.app/docs#tag/chat
    """

    @overload
    async def get_chat_completions(
        self,
        messages: List[Dict[str, str]],
        model: ChatModel = "gpt-4o-mini",
        stream: Literal[False] = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> CreateChatCompletionResponse: ...

    @overload
    async def get_chat_completions(
        self,
        messages: List[Dict[str, str]],
        model: ChatModel = "gpt-4o-mini",
        stream: Literal[True] = True,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> AsyncIterator[CreateChatCompletionResponseStream]: ...

    async def get_chat_completions(
        self,
        messages: List[Dict[str, str]],
        model: ChatModel = "gpt-4o-mini",
        stream: bool = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
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
                filter_params=filter_params,
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
                async for event in AsyncEventSource.from_api_response(response):
                    if event.content == "[DONE]":
                        break

                    token = TypeAdapter(
                        Union[
                            CreateChatCompletionResponseStreamError,
                            CreateChatCompletionResponseStream,
                        ]
                    ).validate_json(event.content)

                    if isinstance(token, CreateChatCompletionResponseStreamError):
                        raise APIError(
                            response=response,
                            detail=token.error.message,
                            code=token.error.code,
                        )

                    yield token

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
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4.1-2025-04-14",
            "claude-3-5-sonnet-latest",
            "claude-3-5-sonnet-20240620",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "o3-mini",
            "claude-sonnet-4-5-20250929",
            "o3",
        ] = "gpt-4.1-2025-04-14",
        cutoff_date: Optional[str] = None,
        use_reddit: bool = False,
        additional_context: Optional[str] = None,
        web_search: bool = False,
        expert: Literal["general", "sports"] = "general",
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
                "expert": expert,
            },
        )
        return ForecastResponse.model_validate(response.content)

    async def live_web_search(
        self,
        queries: List[str],
        lookback: Optional[int] = None,
        domains: Optional[List[str]] = None,
        strict: Optional[bool] = False,
        offset: Optional[int] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WebSearchResponse:
        """
        Run a live websearch, results fully distilled and analyzed
        by LLMs.

        https://docs.asknews.app/en/reference#get-/v1/chat/websearch
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/chat/websearch",
            headers=http_headers,
            query={
                "queries": queries,
                "lookback": lookback,
                "domains": domains,
                "strict": strict,
                "offset": offset,
            },
        )
        return WebSearchResponse.model_validate(response.content)

    async def get_autofilter(
        self,
        query: str,
        *,
        http_headers: Optional[Dict] = None,
    ) -> FilterParamsResponse:
        """
        Generate filter parameters automatically for the AskNews API.

        The output from this can be passed to /news, /chat, /graph, and /forecast

        https://docs.asknews.app/en/reference#get-/v1/chat/autofilter
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/chat/autofilter",
            headers=http_headers,
            query={
                "query": query,
            },
        )
        return FilterParamsResponse.model_validate(response.content)

    async def create_alert(
        self,
        payload: Union[CreateAlertRequest, Dict[str, Any]],
        *,
        http_headers: Optional[Dict] = None,
    ) -> AlertResponse:
        """
        Create an alert.

        https://docs.asknews.app/en/reference#post-/v1/chat/alerts

        :param payload: The alert payload.
        :type payload: CreateAlertRequest
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The created alert.
        :rtype: AlertResponse
        """
        response = await self.client.request(
            method="POST",
            endpoint="/v1/chat/alerts",
            body=payload.model_dump(mode="json")
            if isinstance(payload, CreateAlertRequest)
            else payload,
            headers={
                **(http_headers or {}),
                "Content-Type": CreateAlertRequest.__content_type__,
            },
            accept=[
                (AlertResponse.__content_type__, 1.0),
            ],
        )
        return AlertResponse.model_validate(response.content)

    async def get_alert(
        self,
        alert_id: Union[UUID, str],
        *,
        http_headers: Optional[Dict] = None,
    ) -> AlertResponse:
        """
        Get an alert.

        https://docs.asknews.app/en/reference#get-/v1/chat/alerts/{alert_id}

        :param alert_id: The alert ID.
        :type alert_id: Union[UUID, str]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: Alert details.
        :rtype: AlertResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint=f"/v1/chat/alerts/{alert_id}",
            headers=http_headers,
        )
        return AlertResponse.model_validate(response.content)

    async def list_alerts(
        self,
        page: int = 1,
        per_page: int = 10,
        all: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> PaginatedResponse[AlertResponse]:
        """
        List alerts.

        https://docs.asknews.app/en/reference#get-/v1/chat/alerts

        :param page: The page number.
        :type page: int
        :param per_page: The number of items per page.
        :type per_page: int
        :param all: Whether to return all alerts.
        :type all: bool
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: List of alerts.
        :rtype: PaginatedResponse[AlertResponse]
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/chat/alerts",
            headers=http_headers,
            query={"page": page, "per_page": per_page, "all": all},
        )
        return PaginatedResponse[AlertResponse].model_validate(response.content)

    async def update_alert(
        self,
        alert_id: Union[UUID, str],
        payload: Union[UpdateAlertRequest, Dict[str, Any]],
        *,
        http_headers: Optional[Dict] = None,
    ) -> AlertResponse:
        """
        Update an alert.

        https://docs.asknews.app/en/reference#put-/v1/chat/alerts/{alert_id}

        :param alert_id: The alert ID.
        :type alert_id: Union[UUID, str]
        :param payload: The alert payload.
        :type payload: UpdateAlertRequest
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The updated alert.
        :rtype: AlertResponse
        """
        response = await self.client.request(
            method="PUT",
            endpoint=f"/v1/chat/alerts/{alert_id}",
            body=payload.model_dump(mode="json", exclude_unset=True)
            if isinstance(payload, UpdateAlertRequest)
            else payload,
            headers={
                **(http_headers or {}),
                "Content-Type": UpdateAlertRequest.__content_type__,
            },
            accept=[
                (AlertResponse.__content_type__, 1.0),
            ],
        )
        return AlertResponse.model_validate(response.content)

    async def delete_alert(
        self,
        alert_id: Union[UUID, str],
        *,
        http_headers: Optional[Dict] = None,
    ) -> None:
        """
        Delete an alert.

        https://docs.asknews.app/en/reference#delete-/v1/chat/alerts/{alert_id}

        :param alert_id: The alert ID.
        :type alert_id: Union[UUID, str]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: None
        :rtype: None
        """
        await self.client.request(
            method="DELETE",
            endpoint=f"/v1/chat/alerts/{alert_id}",
            headers=http_headers,
        )

    async def list_alert_logs(
        self,
        alert_id: Union[UUID, str],
        page: int = 1,
        per_page: int = 10,
        all: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> PaginatedResponse[AlertLog]:
        """
        List alert logs.

        https://docs.asknews.app/en/reference#get-/v1/chat/alerts

        :param alert_id: The alert ID.
        :type alert_id: Union[UUID, str]
        :param page: The page number.
        :type page: int
        :param per_page: The number of items per page.
        :type per_page: int
        :param all: Whether to return all alerts.
        :type all: bool
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: List of alerts.
        :rtype: PaginatedResponse[AlertResponse]
        """
        response = await self.client.request(
            method="GET",
            endpoint=f"/v1/chat/alerts/{alert_id}/logs",
            headers=http_headers,
            query={"page": page, "per_page": per_page, "all": all},
        )
        return PaginatedResponse[AlertLog].model_validate(response.content)

    @overload
    async def get_deep_news(
        self,
        messages: List[Dict[str, str]],
        model: DeepNewsModel = "deepseek",
        stream: Literal[False] = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        sources: Optional[List[str]] = None,
        return_sources: bool = True,
        search_depth: int = 3,
        max_depth: int = 5,
        *,
        http_headers: Optional[Dict] = None,
    ) -> CreateDeepNewsResponse: ...

    @overload
    async def get_deep_news(
        self,
        messages: List[Dict[str, str]],
        model: DeepNewsModel = "deepseek",
        stream: Literal[True] = True,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        sources: Optional[List[str]] = None,
        return_sources: bool = True,
        search_depth: int = 3,
        max_depth: int = 5,
        *,
        http_headers: Optional[Dict] = None,
    ) -> AsyncIterator[CreateDeepNewsResponseStream]: ...

    async def get_deep_news(
        self,
        messages: List[Dict[str, str]],
        model: DeepNewsModel = "deepseek",
        stream: bool = False,
        inline_citations: Literal["markdown_link", "numbered", "none"] = "markdown_link",
        append_references: bool = True,
        asknews_watermark: bool = True,
        journalist_mode: bool = True,
        conversational_awareness: bool = False,
        filter_params: Optional[Dict] = None,
        sources: Optional[List[str]] = None,
        return_sources: bool = True,
        search_depth: int = 3,
        max_depth: int = 5,
        *,
        http_headers: Optional[Dict] = None,
    ) -> Union[CreateDeepNewsResponse, AsyncIterator[CreateDeepNewsResponseStream]]:
        """
        Get deep news research!

        https://docs.asknews.app/en/reference#post-/v1/openai/chat/deepnews
        """
        response = await self.client.request(
            method="POST",
            endpoint="/v1/chat/deepnews",
            body=CreateDeepNewsRequest(
                messages=messages,
                model=model,
                stream=stream,
                inline_citations=inline_citations,
                append_references=append_references,
                asknews_watermark=asknews_watermark,
                journalist_mode=journalist_mode,
                conversational_awareness=conversational_awareness,
                filter_params=filter_params,
                sources=sources if sources else ["asknews"],
                search_depth=search_depth,
                max_depth=max_depth,
                return_sources=return_sources,
            ).model_dump(mode="json"),
            headers={
                **(http_headers or {}),
                "Content-Type": CreateDeepNewsRequest.__content_type__,
            },
            accept=[
                (CreateDeepNewsResponse.__content_type__, 1.0),
                (CreateDeepNewsResponseStreamChunk.__content_type__, 1.0),
                (CreateDeepNewsResponseStreamSource.__content_type__, 1.0),
            ],
            stream=stream,
            stream_type="lines",
        )

        if stream:

            async def _stream():
                async for event in AsyncEventSource.from_api_response(response):
                    if event.content == "[DONE]":
                        break

                    token = TypeAdapter(
                        Union[CreateDeepNewsResponseStreamError, CreateDeepNewsResponseStream]
                    ).validate_json(event.content)

                    if isinstance(token, CreateDeepNewsResponseStreamError):
                        raise APIError(
                            response=response,
                            detail=token.error.message,
                            code=token.error.code,
                        )

                    yield token

            return _stream()
        else:
            return CreateDeepNewsResponse.model_validate(response.content)

    async def create_chart(
        self,
        payload: CreateChartRequest,
        *,
        http_headers: Optional[Dict] = None,
    ) -> ChartResponse:
        """
        Create a chart based on news data using a natural language query
        """

        response = await self.client.request(
            method="POST",
            endpoint="/v1/chat/charts",
            body=payload.model_dump(mode="json")
            if isinstance(payload, CreateChartRequest)
            else payload,
            headers={
                **(http_headers or {}),
                "Content-Type": CreateChartRequest.__content_type__,
            },
            accept=[
                (ChartResponse.__content_type__, 1.0),
            ],
        )
        return ChartResponse.model_validate(response.content)
