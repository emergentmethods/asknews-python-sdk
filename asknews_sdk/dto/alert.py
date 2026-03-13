from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union, get_args
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, RootModel
from typing_extensions import Annotated

from asknews_sdk.dto.base import BaseSchema
from asknews_sdk.dto.common import FilterParams
from asknews_sdk.dto.deepnews import DeepNewsSourceType
from asknews_sdk.types import CronStr, HttpUrlString


# DeepNewsModel defined locally to avoid circular import with api.chat
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
    "gemini-3-pro",
    "claude-sonnet-4-6",
    "claude-opus-4-6",
    "claude-opus-4-5-20251101",
    "gemini-2.5-flash",
    "o3",
    "open-source-best"
]


CheckAlertModel = Literal[
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "gpt-4o-mini",
    # "gpt-5-mini",
    # "gpt-5-nano",
    "gpt-4o",
    "o3-mini",
    "meta-llama/Meta-Llama-3.3-70B-Instruct",
    "gpt-4.1-2025-04-14",
    "gpt-4.1-nano-2025-04-14",
    "gpt-4.1-mini-2025-04-14",
]
CheckAlertModelDefault: CheckAlertModel = "gpt-4o"

AlertReportModel = Literal[
    # "gpt-5",
    "gpt-4o",
    "gpt-4.1-2025-04-14",
    "gpt-4.1-mini-2025-04-14",
    "gpt-4o-mini",
    "o3-mini",
    "claude-3-5-sonnet-latest",
    "claude-sonnet-4-20250514",
    "claude-sonnet-4-5-20250929",
    "claude-opus-4-5-20251101",
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "meta-llama/Meta-Llama-3.1-405B-Instruct",
    "meta-llama/Meta-Llama-3.3-70B-Instruct",
]
AlertReportModelDefault: AlertReportModel = "claude-sonnet-4-5-20250929"

DeepNewsSourceModelDefault: DeepNewsModel = "open-source-best"
DeepNewsReportModelDefault: DeepNewsModel = "claude-sonnet-4-6"

DeepNewsSourceTypeDefault: List[DeepNewsSourceType] = ["asknews", "google", "wiki", "x"]


class DeepNewsParams(BaseModel):
    """Base parameters shared between DeepNews source and report configurations."""

    sources: Optional[Union[DeepNewsSourceType, List[DeepNewsSourceType]]] = Field(
        default=DeepNewsSourceTypeDefault,
        description=(
            "Which data sources DeepNews should use. Can be a single source or a list. "
            f"Available sources are: {', '.join(get_args(DeepNewsSourceType))}. "
            f"Defaults to {DeepNewsSourceTypeDefault}."
        ),
    )
    filter_params: Optional[FilterParams] = Field(
        default=None,
        description="Filter parameters to apply to the AskNews search within DeepNews.",
    )
    include_entities: Optional[bool] = Field(
        default=True,
        description="Whether to provide extracted entities to the agent. Defaults to True.",
    )
    include_graphs: Optional[bool] = Field(
        default=False,
        description="Whether to provide knowledge graphs to the agent. Defaults to False.",
    )
    include_coordinates: Optional[bool] = Field(
        default=False,
        description="Whether to provide geo coordinates to the agent. Defaults to False.",
    )


class DeepNewsSourceParams(DeepNewsParams):
    """Parameters for DeepNews alert source.

    DeepNews performs deep research using multiple tools.
    """
    model: Optional[DeepNewsModel] = Field(
        default=DeepNewsSourceModelDefault,
        description=(
            f"The model to use for DeepNews research. Defaults to {DeepNewsSourceModelDefault}"
        ),
        examples=["claude-sonnet-4-5-20250929"],
    )
    search_depth: Optional[int] = Field(
        default=2,
        ge=1,
        le=10,
        description=(
            "The search depth for deep research. Higher values mean more "
            "thorough research. Defaults to 2."
        ),
    )
    max_depth: Optional[int] = Field(
        default=4,
        ge=1,
        le=10,
        description="The maximum research depth allowed. Defaults to 4.",
    )


class DeepNewsReportParams(DeepNewsParams):
    """Parameters for DeepNews alert report.

    DeepNews performs deep research using multiple tools.
    """
    model: Optional[DeepNewsModel] = Field(
        default=DeepNewsReportModelDefault,
        description=(
            f"The model to use for DeepNews research. Defaults to {DeepNewsReportModelDefault}"
        ),
        examples=["claude-sonnet-4-5-20250929"],
    )
    search_depth: Optional[int] = Field(
        default=2,
        ge=1,
        le=80,
        description=(
            "The search depth for deep research. Higher values mean more "
            "thorough research. Defaults to 2."
        ),
    )
    max_depth: Optional[int] = Field(
        default=4,
        ge=1,
        le=100,
        description="The maximum research depth allowed. Defaults to 4.",
    )
    start_citation_number: Optional[int] = Field(
        default=1,
        description=(
            "Starting number for inline citations. Offsets fetched source citation keys. "
            "Useful if you are providing the agent outside sources with numbered citation keys. "
            "Defaults to 1."
        ),
    )
    journalist_mode: Optional[bool] = Field(
        default=True,
        description=(
            "Whether to use journalist mode for more factual reporting. Defaults to True."
        ),
    )


class WebSourceParams(BaseModel):
    queries: List[str] = Field(
        ...,
        description="The queries to use for the web search. This is a list of strings.",
    )
    domains: Optional[List[str]] = Field(
        None, description="The domains to restrict the web search to."
    )
    strict: bool = Field(
        True,
        description=(
            "If true, the web search will only return results that have "
            "a known publication date and are within the lookback period."
        ),
    )
    lookback: int = Field(
        24,
        description=(
            "The number of hours back to accept for the web search. "
            "If not provided, no lookback will be applied."
        ),
    )


class WebSource(BaseModel):
    identifier: Literal["web"] = "web"
    params: WebSourceParams


class AskNewsSource(BaseModel):
    identifier: Literal["asknews"] = "asknews"
    params: Optional[FilterParams] = Field(None, description="The filter params to use")


class TelegramSourceParams(BaseModel):
    channel_name: str = Field(..., description="The channel name to use as a source")


class TelegramSource(BaseModel):
    identifier: Literal["telegram"] = "telegram"
    params: TelegramSourceParams


class BlueskySourceParams(BaseModel):
    query: Optional[str] = Field(None, description="The search query")


class BlueskySource(BaseModel):
    identifier: Literal["bluesky"] = "bluesky"
    params: Optional[BlueskySourceParams] = Field(None, description="Bluesky source parameters")


class DeepNewsSource(BaseModel):
    identifier: Literal["deepnews"] = "deepnews"
    params: DeepNewsSourceParams = Field(default_factory=DeepNewsSourceParams)


Source = Annotated[
    Union[AskNewsSource, TelegramSource, BlueskySource, WebSource, DeepNewsSource],
    Field(discriminator="identifier"),
]


class Sources(RootModel):
    root: List[Source]


class WebhookParams(BaseModel):
    url: HttpUrlString = Field(
        ..., description="The URL to send the webhook when the alert triggers"
    )
    headers: Optional[Dict[str, str]] = Field(
        None, description="The headers to send with the webhook."
    )
    payload: Optional[Dict[str, Any]] = Field(
        None, description="The payload to send with the webhook."
    )


class EmailParams(BaseModel):
    to: EmailStr = Field(..., description="The email to send the alert to when it triggers")
    subject: Optional[str] = Field(
        None,
        description="The subject of the email. If not provided, the default subject will be used.",
    )
    asknews_watermark: Optional[bool] = Field(
        default=True, description='Append "Generated by AskNews AI" watermark.'
    )


class GoogleDocsParams(BaseModel):
    client_json: Dict[str, Any] = Field(
        ...,
        description=(
            "The google service account json. This should be a dict. You can get this "
            "from the google cloud console. The document will be created in the service "
            "account's google drive and shared with the user."
        ),
    )
    emails: Optional[List[EmailStr]] = Field(None, description="The emails to share the doc with")
    asknews_watermark: Optional[bool] = Field(
        default=True, description='Append "Generated by AskNews AI" watermark.'
    )


class WebhookAction(BaseModel):
    action: Literal["webhook"] = Field("webhook")
    params: WebhookParams


class EmailAction(BaseModel):
    action: Literal["email"] = Field("email")
    params: EmailParams


class GoogleDocsAction(BaseModel):
    action: Literal["google_docs"] = Field("google_docs")
    params: GoogleDocsParams


Trigger = Annotated[
    Union[WebhookAction, EmailAction, GoogleDocsAction],
    Field(discriminator="action"),
]


class Triggers(RootModel):
    root: List[Trigger]


class ReportRequestParams(BaseModel):
    """Base parameters shared between legacy and DeepNews report configurations."""
    logo_url: Optional[HttpUrlString] = Field(
        default=None, description="The logo URL to use for the report"
    )
    include_appendix: bool = Field(
        default=False,
        description="Whether to append thinking and search traces as an appendix to the report.",
    )
    asknews_watermark: bool = Field(
        default=True,
        description='Append "Generated by AskNews AI" watermark.',
    )


class LegacyReportRequest(ReportRequestParams):
    """DEPRECATED - Use DeepNewsReportRequest instead.
    Legacy report configuration (original format).
    This is the original ReportRequest format that uses a simple model field
    for report generation without DeepNews capabilities.
    """
    identifier: Literal["legacy"] = "legacy"
    model: AlertReportModel = Field(
        default=AlertReportModelDefault,
        description=f"The model to use for the report. Defaults to {AlertReportModelDefault}.",
        examples=["gpt-4o"],
    )


class DeepNewsReportRequest(ReportRequestParams):
    """DeepNews report configuration.

    Uses DeepNews deep research capabilities for information retrieval and report generation.
    """
    identifier: Literal["deepnews"] = "deepnews"
    params: DeepNewsReportParams = Field(default_factory=DeepNewsReportParams)
    prompt: Optional[str] = Field(
        default=None,
        description=(
            "Optional prompt to use for report generation instructions, such as specific "
            "formatting requests, or, if you are providing a list of report requests, specify "
            "both your query and any formatting instructions here."
        ),
        examples=[
            "Format your findings as a bullet point list.",
            "Analyze current trends in the crypto market and shoe industry. Give each sector "
            "its own section."
        ],
    )


# Type alias for discriminated union (used in type hints)
ReportRequestType = Annotated[
    Union[LegacyReportRequest, DeepNewsReportRequest], Field(discriminator="identifier")
]


def ReportRequest(**kwargs: Any) -> Union[LegacyReportRequest, DeepNewsReportRequest]:
    """Factory function for creating report configurations.

    Maintains backwards compatibility with the original ReportRequest API while
    also supporting DeepNews reports via the identifier parameter.

    Args:
        identifier: "legacy" (default) or "deepnews"
        **kwargs: Report configuration parameters

    Returns:
        LegacyReportRequest if identifier is "legacy" or not provided
        DeepNewsReportRequest if identifier is "deepnews"

    Usage:
        # Legacy format (DEPRECATED)
        ReportRequest(model="gpt-4o", logo_url="https://...")

        # DeepNews format
        ReportRequest(identifier="deepnews", logo_url="https://...")

        # DeepNews with params
        ReportRequest(identifier="deepnews", params={"model": "claude-opus-4-6"})
    """
    identifier = kwargs.get("identifier", "legacy")

    if identifier == "deepnews":
        return DeepNewsReportRequest(**kwargs)
    else:
        # Default to legacy, ensure identifier is set
        if "identifier" not in kwargs:
            kwargs["identifier"] = "legacy"
        return LegacyReportRequest(**kwargs)


AlertType = Literal["AlwaysAlertWhen", "AlertOnceIf", "ReportAbout"]


class CreateAlertRequest(BaseSchema):
    query: str = Field(
        ...,
        description=(
            "The query to run for the alert. If you are providing a list of report requests, "
            "specify each report's individual query in the report prompt."
        ),
        examples=[
            "I want to be alerted if the president of the US says something about the economy",
        ],
    )
    sources: Sources = Field(
        ...,
        description=(
            "The sources to use for the alert query. Available sources are: "
            f"{', '.join([arg.__name__ for arg in get_args(get_args(Source)[0])])}"
        ),
    )
    alert_type: Optional[AlertType] = Field(
        default=None,
        description=(
            "The type of alert. If specified, overrides `repeat` and `always_trigger`. "
            "'AlwaysAlertWhen': trigger alert actions any time the alert query is "
            "satisfied (`repeat=True`, `always_trigger=False`). "
            "Add Report model if you want a report when this is triggered. "
            "'AlertOnceIf': trigger alert actions when the alert query is satisfied "
            "and then disable the alert (`repeat=False`, `always_trigger=False`). "
            "Add Report model if you want a report when this is triggered. "
            "'ReportAbout': always trigger alert actions according to cron schedule "
            "and write a report (`repeat=True`, `always_trigger=True`). "
            "Defaults to using DeepNews for the report unless specified."
        ),
    )
    model: CheckAlertModel = Field(
        default=CheckAlertModelDefault,
        description=(
            "The model that is used to check if the alert conditions are satisfied by "
            "sources (this is not the same as the model used to write the report.) "
            f"Defaults to {CheckAlertModelDefault}."
        ),
        examples=["gpt-4o-mini"],
    )
    cron: CronStr = Field(
        ...,
        description=(
            "How often or when to check sources for this alert, specified as a cron expression. "
            "Examples: '0 * * * *' (hourly), "
            "'0 9 * * *' (daily at 9am), '0 9 * * 1' (Mondays at 9am). "
            " See https://crontab.run/ for more examples."
        ),
        examples=[
            "'0 0 * * *' (daily at midnight UTC)",
        ],
    )
    triggers: Triggers = Field(
        ...,
        description=(
            "Configuration for actions to trigger for the alert. Available actions are: "
            f"{', '.join([arg.__name__ for arg in get_args(get_args(Trigger)[0])])}"
        ),
    )
    always_trigger: bool = Field(
        default=False,
        description=(
            "Whether to always trigger the actions when sources are scanned. This skips the "
            "check for if the alert conditions are satisfied and run triggers immediately. "
            "Defaults to False."
        ),
    )
    repeat: bool = Field(
        default=True,
        description=(
            "Whether to repeat the alert. Default is True. If False, the alert will be "
            "disabled after it triggers once."
        ),
    )
    active: bool = Field(
        default=True, description="Whether the alert is active or not. Default is True."
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description=(
            "The expiration date for the alert. Default is None. "
            "If set, the alert will be disabled after this date."
        ),
    )
    report: Optional[Union[ReportRequestType, List[ReportRequestType]]] = Field(
        default=None,
        description=(
            "Configuration for generating a written report when the alert triggers. "
            "If report is a list, the individual reports will be concatenated into "
            "one report in the order they are defined. "
            "Use ReportRequest(identifier='deepnews', ...) for DeepNews reports."
            "Use ReportRequest(...) or ReportRequest(identifier='legacy', ...) for "
            "legacy reports (DEPRECATED). Requests without identifier default to "
            "'deepnews'. Only DeepNews reports can be used in list."
        ),
    )
    title: Optional[str] = Field(
        default=None,
        description="The title of the alert. If not provided, no title will be used.",
        examples=["Alert for US President's statements on the economy"],
    )
    share_link: Optional[HttpUrlString] = Field(
        default=None, description="The newsplunker share link to update when the alert triggers."
    )


class UpdateAlertRequest(BaseSchema):
    query: Optional[str] = Field(
        default=None,
        description=(
            "The query to run for the alert. If you are providing a list of report requests, "
            "specify each report's individual query in the report prompt."
        ),
        examples=[
            "I want to be alerted if the president of the US says something about the economy",
        ],
    )
    sources: Optional[Sources] = Field(
        default=None,
        description=(
            "The sources to use for the alert query. Available sources are: "
            f"{', '.join([arg.__name__ for arg in get_args(get_args(Source)[0])])}"
        ),
    )
    alert_type: Optional[AlertType] = Field(
        default=None,
        description=(
            "The type of alert. If specified, overrides `repeat` and `always_trigger`. "
            "'AlwaysAlertWhen': trigger alert actions any time the alert query is "
            "satisfied (`repeat=True`, `always_trigger=False`). "
            "Add Report model if you want a report when this is triggered. "
            "'AlertOnceIf': trigger alert actions when the alert query is satisfied "
            "and then disable the alert (`repeat=False`, `always_trigger=False`). "
            "Add Report model if you want a report when this is triggered. "
            "'ReportAbout': always trigger alert actions according to cron schedule "
            "and write a report (`repeat=True`, `always_trigger=True`). "
            "Defaults to using DeepNews for the report unless specified."
        ),
    )
    model: Optional[CheckAlertModel] = Field(
        default=None,
        description=(
            "The model that is used to check if the alert conditions are satisfied by "
            "sources (this is not the same as the model used to write the report.)"
        ),
        examples=["gpt-4o-mini"],
    )
    cron: Optional[CronStr] = Field(
        default=None,
        description=(
            "How often or when to check sources for this alert, specified as a cron expression. "
            "Examples: '0 * * * *' (hourly), "
            "'0 9 * * *' (daily at 9am), '0 9 * * 1' (Mondays at 9am). "
            " See https://crontab.run/ for more examples."
        ),
        examples=["'0 0 * * *' (daily at midnight UTC)"],
    )
    triggers: Optional[Triggers] = Field(
        default=None,
        description=(
            "Configuration for actions to trigger for the alert. Available actions are: "
            f"{', '.join([arg.__name__ for arg in get_args(get_args(Trigger)[0])])}"
        ),
    )
    always_trigger: Optional[bool] = Field(
        default=None,
        description=(
            "Whether to always trigger the actions when sources are scanned. This skips the "
            "check for if the alert conditions are satisfied and run triggers immediately. "
            "Defaults to False."
        ),
    )
    repeat: Optional[bool] = Field(
        default=None,
        description=(
            "Whether to repeat the alert. Default is True. If False, the alert will be "
            "disabled after it triggers once."
        ),
    )
    active: Optional[bool] = Field(
        default=None, description="Whether the alert is active or not. Default is True."
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description=(
            "The expiration date for the alert. Default is None. "
            "If set, the alert will be disabled after this date."
        ),
    )
    report: Optional[Union[ReportRequestType, List[ReportRequestType]]] = Field(
        default=None,
        description=(
            "Configuration for generating a written report when the alert triggers. "
            "If report is a list, the individual reports will be concatenated into "
            "one report in the order they are defined. "
            "Use ReportRequest(identifier='deepnews', ...) for DeepNews reports."
            "Use ReportRequest(...) or ReportRequest(identifier='legacy', ...) for "
            "legacy reports (DEPRECATED). Requests without identifier default to "
            "'deepnews'. Only DeepNews reports can be used in list."
        ),
    )
    title: Optional[str] = Field(
        default=None,
        description="The title of the alert. If not provided, no title will be used.",
        examples=["Alert for US President's statements on the economy"],
    )
    share_link: Optional[HttpUrlString] = Field(
        default=None, description="The newsplunker share link to update when the alert triggers."
    )


class AlertLog(BaseModel):
    id: UUID
    created_at: datetime
    alert_id: UUID
    user_id: UUID
    alert: bool
    reasoning: str
    report: Optional[str] = None
    report_url: Optional[str] = None
    article_ids: List[UUID]
    webhook: Optional[Dict[str, Any]] = None


class AlertResponse(BaseSchema):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    user_id: UUID
    query: Optional[str] = None
    cron: str
    model: Optional[str] = None
    share_link: Optional[str] = None
    sources: List[Dict[str, Any]]
    report: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None
    triggers: List[Dict[str, Any]]
    always_trigger: bool = False
    repeat: bool = True
    active: bool = True
    alert_type: Optional[AlertType] = None
    title: Optional[str] = None
