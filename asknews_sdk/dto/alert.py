from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, RootModel

from asknews_sdk.dto.common import FilterParams
from asknews_sdk.types import CronStr, HttpUrlString


CheckAlertModel = Literal["meta-llama/Meta-Llama-3.1-8B-Instruct", "gpt-4o-mini"]

ReportModel = Literal[
    "gpt-4o", "claude-3-5-sonnet-latest", "meta-llama/Meta-Llama-3.1-405B-Instruct"
]


class ReportParams(BaseModel):
    query: Optional[List[List[str, str]]] = Field(
        None,
        description=(
            "The optional prompt to use for report generation. The prompt should be a list of "
            "tuples where the first element is the author of the prompt and the second element "
            "is the prompt itself. For example, [['system', 'You are a helpful AI bot. Write a "
            "report based on summaries provided by the user.'], ['human', '{summaries}']]. "
            "If not provided, the default report prompt will be used. You can use {summaries} "
            "to insert the prompt optimized summaries into your report query."
        ),
        example=[
            [
                "system",
                "You are a helpful AI bot. Write a report based on summaries provided by the user.",
            ],
            ["human", "{summaries}"],
        ],
    )
    model: Optional[ReportModel] = Field(
        None, description="The model to use for the report", example="gpt-4o"
    )


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


class ReportAction(BaseModel):
    action: Literal["report"]
    params: ReportParams


class WebhookAction(BaseModel):
    action: Literal["webhook"]
    params: WebhookParams


class EmailAction(BaseModel):
    action: Literal["email"]
    params: EmailParams


class GoogleDocsAction(BaseModel):
    action: Literal["google_docs"]
    params: GoogleDocsParams


Trigger = Annotated[
    ReportAction | WebhookAction | EmailAction | GoogleDocsAction,
    Field(discriminator="action"),
]


class Triggers(RootModel):
    root: List[Trigger]


class CreateAlertRequest(BaseModel):
    query: Optional[str] = Field(
        None,
        description=(
            "The query to run for the alert. For example you ask for "
            '"I want to be alerted if there is a protest in paris"'
        ),
        example="I want to be alerted if the president of the US says something about the economy",
    )
    cron: CronStr = Field(
        ...,
        description=(
            "The cron schedule for the alert. For example every 15 minutes is '*/15 * * * *'."
            " See https://crontab.run/ for more examples"
        ),
        example="*/15 * * * *",
    )
    model: Optional[CheckAlertModel] = Field(
        ...,
        description="The model to use for the alert check",
        example="meta-llama/Meta-Llama-3.1-8B-Instruct",
    )
    share_link: Optional[HttpUrlString] = Field(
        None, description="The newsplunker share link to update when the alert triggers"
    )
    filter_params: Optional[FilterParams] = Field(
        None, description="The filter params to use for the alert query"
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


class UpdateAlertRequest(BaseModel):
    query: Optional[str] = Field(
        None,
        description=(
            "The query to run for the alert. For example you ask for "
            '"I want to be alerted if there is a protest in paris"'
        ),
        example="I want to be alerted if the president of the US says something about the economy",
    )
    cron: Optional[CronStr] = Field(
        None,
        description=(
            "The cron schedule for the alert. For example every 15 minutes is '*/15 * * * *'."
            " See https://crontab.run/ for more examples"
        ),
        example="*/15 * * * *",
    )
    model: Optional[CheckAlertModel] = Field(
        None,
        description="The model to use for the alert check",
        example="meta-llama/Meta-Llama-3.1-8B-Instruct",
    )
    share_link: Optional[HttpUrlString] = Field(
        None, description="The newsplunker share link to update when the alert triggers"
    )
    filter_params: Optional[FilterParams] = Field(
        None, description="The filter params to use for the alert query"
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


class AlertResponse(BaseModel):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_id: UUID
    query: Optional[str] = None
    cron: str
    model: Optional[str]
    share_link: Optional[str] = None
    filter_params: Optional[Dict[str, Any]] = None
    triggers: List[Dict[str, Any]]
    always_trigger: bool = False
    repeat: bool = True
    active: bool = True
