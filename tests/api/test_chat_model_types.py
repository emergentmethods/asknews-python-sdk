import json
from inspect import getmembers, isclass
from typing import get_args, get_type_hints

import pytest
from pydantic import BaseModel

from asknews_sdk.api.chat import AsyncChatAPI, ChatAPI, ChatModel, DeepNewsModel
from asknews_sdk.dto import alert as alert_dto
from asknews_sdk.dto.deepnews import CreateDeepNewsRequest


GPT_6_ASTRA = "gpt-6-astra"
CLAUDE_FABLE_MODELS = ("claude-fable-5", "claude-fable-5-1")
ADVANCED_DEEPNEWS_MODELS = ("claude-opus-5-5", "gpt-6-sol")


def test_gpt_6_astra_is_a_direct_deepnews_model_only():
    assert GPT_6_ASTRA in get_args(DeepNewsModel)
    assert GPT_6_ASTRA not in get_args(ChatModel)


@pytest.mark.parametrize("api_type", [ChatAPI, AsyncChatAPI])
def test_gpt_6_astra_is_scoped_to_get_deep_news(api_type):
    deepnews_model = get_type_hints(api_type.get_deep_news)["model"]
    forecast_model = get_type_hints(api_type.get_forecast)["model"]

    assert GPT_6_ASTRA in get_args(deepnews_model)
    assert GPT_6_ASTRA not in get_args(forecast_model)


def test_gpt_6_astra_is_absent_from_alert_model_contracts():
    alert_model_types = (
        alert_dto.DeepNewsModel,
        alert_dto.CheckAlertModel,
        alert_dto.AlertReportModel,
    )
    for model_type in alert_model_types:
        assert GPT_6_ASTRA not in get_args(model_type)

    for name, model in getmembers(alert_dto, isclass):
        if model.__module__ == alert_dto.__name__ and issubclass(model, BaseModel):
            assert GPT_6_ASTRA not in json.dumps(model.model_json_schema()), name


@pytest.mark.parametrize("model", ADVANCED_DEEPNEWS_MODELS)
@pytest.mark.parametrize("api_type", [ChatAPI, AsyncChatAPI])
def test_advanced_models_are_scoped_to_deepnews_and_preserve_alert_contracts(model, api_type):
    assert model in get_args(DeepNewsModel)
    assert model in get_args(get_type_hints(api_type.get_deep_news)["model"])
    assert model not in get_args(ChatModel)
    assert model not in get_args(alert_dto.DeepNewsModel)
    assert model not in get_args(alert_dto.CheckAlertModel)
    assert model not in get_args(alert_dto.AlertReportModel)


@pytest.mark.parametrize("model", ADVANCED_DEEPNEWS_MODELS)
def test_advanced_deepnews_models_serialize_in_requests(model):
    request = CreateDeepNewsRequest(messages=[{"role": "user", "content": "query"}], model=model)

    assert request.model_dump(mode="json")["model"] == model


@pytest.mark.parametrize("model", CLAUDE_FABLE_MODELS)
def test_claude_fable_models_match_deepnews_and_alert_report_contracts(model):
    assert model in get_args(DeepNewsModel)
    assert model in get_args(alert_dto.DeepNewsModel)
    assert model in get_args(alert_dto.AlertReportModel)
