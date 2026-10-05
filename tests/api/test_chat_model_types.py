import json
from pathlib import Path
from typing import get_args, get_type_hints

import pytest
from pydantic import TypeAdapter, ValidationError

from asknews_sdk.api.chat import AsyncChatAPI, ChatAPI, ChatModel, DeepNewsModel
from asknews_sdk.dto import alert as alert_dto
from asknews_sdk.dto.deepnews import CreateDeepNewsRequest


GPT_6_ASTRA = "gpt-6-astra"
CLAUDE_FABLE_MODELS = ("claude-fable-5", "claude-fable-5-1")
NEW_DEEPNEWS_MODELS = ("claude-sonnet-5-5", "claude-opus-5-5", "gpt-6.1-sol")
ADVANCED_DEEPNEWS_MODELS = (*NEW_DEEPNEWS_MODELS, "gpt-6-sol", "kimi-k3")
PRODUCTION_CONTRACT = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "production_contract_0323.json").read_text()
)
PRODUCTION_DEEPNEWS_MODELS = PRODUCTION_CONTRACT["deepnews_models"]


def test_gpt_6_astra_is_a_deepnews_model_not_a_chat_model():
    assert GPT_6_ASTRA in get_args(DeepNewsModel)
    assert GPT_6_ASTRA not in get_args(ChatModel)


@pytest.mark.parametrize("api_type", [ChatAPI, AsyncChatAPI])
def test_gpt_6_astra_is_scoped_to_get_deep_news(api_type):
    deepnews_model = get_type_hints(api_type.get_deep_news)["model"]
    forecast_model = get_type_hints(api_type.get_forecast)["model"]

    assert GPT_6_ASTRA in get_args(deepnews_model)
    assert GPT_6_ASTRA not in get_args(forecast_model)


def test_gpt_6_astra_matches_updated_alert_contracts():
    assert GPT_6_ASTRA in get_args(alert_dto.DeepNewsModel)
    assert GPT_6_ASTRA in get_args(alert_dto.AlertReportModel)
    assert GPT_6_ASTRA not in get_args(alert_dto.CheckAlertModel)
    assert alert_dto.LegacyReportRequest(model=GPT_6_ASTRA).model == GPT_6_ASTRA


@pytest.mark.parametrize("model", ADVANCED_DEEPNEWS_MODELS)
@pytest.mark.parametrize("api_type", [ChatAPI, AsyncChatAPI])
def test_advanced_models_are_scoped_to_deepnews_and_preserve_legacy_contracts(model, api_type):
    assert model in get_args(DeepNewsModel)
    assert model in get_args(get_type_hints(api_type.get_deep_news)["model"])
    assert model not in get_args(ChatModel)
    assert model not in get_args(alert_dto.CheckAlertModel)
    assert model not in get_args(alert_dto.AlertReportModel)


@pytest.mark.parametrize("model", ADVANCED_DEEPNEWS_MODELS)
def test_advanced_deepnews_models_serialize_in_requests(model):
    request = CreateDeepNewsRequest(messages=[{"role": "user", "content": "query"}], model=model)

    assert request.model_dump(mode="json")["model"] == model


@pytest.mark.parametrize("model", PRODUCTION_DEEPNEWS_MODELS)
@pytest.mark.parametrize(
    "request_type", [alert_dto.CreateAlertRequest, alert_dto.UpdateAlertRequest]
)
def test_active_alert_source_and_report_models_validate_and_serialize(model, request_type):
    assert model in get_args(alert_dto.DeepNewsModel)
    request = request_type(
        cron="0 9 * * *",
        triggers=[],
        sources=[{"identifier": "deepnews", "params": {"model": model}}],
        report={"identifier": "deepnews", "params": {"model": model}},
    )
    payload = json.loads(request.model_dump_json())

    assert payload["sources"][0]["params"]["model"] == model
    assert payload["report"]["params"]["model"] == model


@pytest.mark.parametrize("model_type", [DeepNewsModel, alert_dto.DeepNewsModel])
def test_deepnews_model_contracts_reject_misspelled_gpt_id(model_type):
    with pytest.raises(ValidationError):
        TypeAdapter(model_type).validate_python("gpt-sol-6.1")


def test_active_alert_model_defaults_are_unchanged():
    assert alert_dto.DeepNewsSourceParams().model == "gemini-3-flash"
    assert alert_dto.DeepNewsReportParams().model == "claude-sonnet-4-6"
    assert alert_dto.LegacyReportRequest().model == "claude-sonnet-4-6"


@pytest.mark.parametrize("model", CLAUDE_FABLE_MODELS)
def test_claude_fable_models_match_deepnews_and_alert_report_contracts(model):
    assert model in get_args(DeepNewsModel)
    assert model in get_args(alert_dto.DeepNewsModel)
    assert model in get_args(alert_dto.AlertReportModel)


@pytest.mark.parametrize("model_type", [DeepNewsModel, alert_dto.DeepNewsModel])
def test_deepnews_catalog_matches_production_schema(model_type):
    assert set(get_args(model_type)) == set(PRODUCTION_DEEPNEWS_MODELS)


@pytest.mark.parametrize(
    "request_type", [alert_dto.CreateAlertRequest, alert_dto.UpdateAlertRequest]
)
def test_new_legacy_report_option_serializes(request_type):
    request = request_type(
        cron="0 9 * * *",
        triggers=[],
        sources=[],
        report={"identifier": "legacy", "model": GPT_6_ASTRA},
    )
    assert json.loads(request.model_dump_json())["report"]["model"] == GPT_6_ASTRA


def test_new_legacy_report_option_is_authoritative_and_defaults_are_preserved():
    assert GPT_6_ASTRA in PRODUCTION_CONTRACT["legacy_report_models"]
    assert alert_dto.LegacyReportRequest().model == "claude-sonnet-4-6"
    assert alert_dto.DeepNewsSourceParams().engine == "v1"
    assert alert_dto.DeepNewsReportParams().engine == "v1"
