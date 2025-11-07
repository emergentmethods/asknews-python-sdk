from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, RootModel
from typing_extensions import Annotated

from asknews_sdk.dto.base import BaseSchema
from asknews_sdk.dto.common import FilterParams
from asknews_sdk.types import CronStr, HttpUrlString


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

ReportModel = Literal[
    # "gpt-5",
    "gpt-4o",
    "gpt-4.1-2025-04-14",
    "gpt-4.1-mini-2025-04-14" "gpt-4o-mini",
    "o3-mini",
    "claude-3-5-sonnet-latest",
    "claude-sonnet-4-20250514",
    "claude-sonnet-4-5-20250929",
    "meta-llama/Meta-Llama-3.1-405B-Instruct",
    "meta-llama/Meta-Llama-3.3-70B-Instruct",
]


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
    identifier: Literal["web"]
    params: WebSourceParams


class AskNewsSource(BaseModel):
    identifier: Literal["asknews"]
    params: Optional[FilterParams] = Field(None, description="The filter params to use")


class TelegramSourceParams(BaseModel):
    channel_name: str = Field(..., description="The channel name to use as a source")


class TelegramSource(BaseModel):
    identifier: Literal["telegram"]
    params: TelegramSourceParams


class BlueskySourceParams(BaseModel):
    query: Optional[str] = Field(None, description="The search query")


class BlueskySource(BaseModel):
    identifier: Literal["bluesky"]
    params: Optional[BlueskySourceParams] = Field(None, description="Bluesky source parameters")


Source = Annotated[
    Union[AskNewsSource, TelegramSource, BlueskySource, WebSource],
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


class ReportRequest(BaseModel):
    prompt: Optional[List[List[str]]] = Field(
        None,
        description=(
            "The optional prompt to use for report generation. The prompt should be a list of "
            "tuples where the first element is the author of the prompt and the second element "
            "is the prompt itself. For example, [['system', 'You are a helpful AI bot. Write a "
            "report based on summaries provided by the user.'], ['human', '{summaries}']]. "
            "If not provided, the default report prompt will be used. You can use {summaries} "
            "to insert the prompt optimized summaries into your report query."
        ),
        examples=[
            [
                "system",
                "You are a helpful AI bot. Write a report based on summaries provided by the user.",
            ],
            ["human", "{summaries}"],
        ],
    )
    model: Optional[ReportModel] = Field(
        None, description="The model to use for the report", examples=["gpt-4o"]
    )
    logo_url: Optional[HttpUrlString] = Field(
        None, description="The logo URL to use for the report"
    )


class CreateAlertRequest(BaseSchema):
    query: Optional[str] = Field(
        None,
        description=(
            "The query to run for the alert. For example you ask for "
            '"I want to be alerted if there is a protest in paris"'
        ),
        examples=[
            "I want to be alerted if the president of the US says something about the economy",
        ],
    )
    cron: CronStr = Field(
        ...,
        description=(
            "The cron schedule for the alert. For example hourly is '0 * * * *'."
            " See https://crontab.run/ for more examples"
        ),
        examples=[
            "*/15 * * * *",
        ],
    )
    model: Optional[CheckAlertModel] = Field(
        ...,
        description="The model to use for the alert check",
        examples=[
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
        ],
    )
    share_link: Optional[HttpUrlString] = Field(
        None, description="The newsplunker share link to update when the alert triggers"
    )
    sources: Sources = Field(..., description="The sources to use for the alert query")
    report: Optional[ReportRequest] = Field(
        None, description="The report to generate when the alert triggers"
    )
    triggers: Triggers = Field(..., description="The triggers to use for the alert")
    always_trigger: bool = Field(
        False,
        description=(
            "Whether to always trigger the alert. Default is False. This skips the "
            "alert check and run triggers immediately"
        ),
    )
    repeat: bool = Field(
        True,
        description=(
            "Whether to repeat the alert. Default is True. If False, the alert will be "
            "disabled after it triggers once"
        ),
    )
    active: bool = Field(True, description="Whether the alert is active or not. Default is True.")
    expires_at: Optional[datetime] = Field(
        None,
        description=(
            "The expiration date for the alert. Default is None. "
            "If set, the alert will be disabled after this date."
        ),
    )


class UpdateAlertRequest(BaseSchema):
    query: Optional[str] = Field(
        None,
        description=(
            "The query to run for the alert. For example you ask for "
            '"I want to be alerted if there is a protest in paris"'
        ),
        examples=[
            "I want to be alerted if the president of the US says something about the economy",
        ],
    )
    cron: Optional[CronStr] = Field(
        None,
        description=(
            "The cron schedule for the alert. For example hourly is '0 * * * *'."
            " See https://crontab.run/ for more examples"
        ),
        examples=[
            "*/15 * * * *",
        ],
    )
    model: Optional[CheckAlertModel] = Field(
        None,
        description="The model to use for the alert check",
        examples=[
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
        ],
    )
    share_link: Optional[HttpUrlString] = Field(
        None, description="The newsplunker share link to update when the alert triggers"
    )
    filter_params: Optional[FilterParams] = Field(
        None, description="The filter params to use for the alert query"
    )
    sources: Optional[Sources] = Field(None, description="The sources to use for the alert query")
    report: Optional[ReportRequest] = Field(
        None, description="The report to generate when the alert triggers"
    )
    triggers: Optional[Triggers] = Field(None, description="The triggers to use for the alert")
    always_trigger: Optional[bool] = Field(
        None,
        description=(
            "Whether to always trigger the alert. Default is False. This skips the "
            "alert check and run triggers immediately"
        ),
    )
    repeat: Optional[bool] = Field(
        None,
        description=(
            "Whether to repeat the alert. Default is True. If False, the alert will be "
            "disabled after it triggers once"
        ),
    )
    active: Optional[bool] = Field(
        None, description="Whether the alert is active or not. Default is True."
    )
    expires_at: Optional[datetime] = Field(
        None,
        description=(
            "The expiration date for the alert. Default is None. "
            "If set, the alert will be disabled after this date."
        ),
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
    model: Optional[str]
    share_link: Optional[str] = None
    sources: List[Dict[str, Any]]
    report: Optional[Dict[str, Any]] = None
    triggers: List[Dict[str, Any]]
    always_trigger: bool = False
    repeat: bool = True
    active: bool = True
