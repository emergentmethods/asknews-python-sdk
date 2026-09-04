import json
from inspect import getmembers, isclass
from typing import get_args, get_type_hints

import pytest
from pydantic import BaseModel

from asknews_sdk.api.chat import AsyncChatAPI, ChatAPI, ChatModel, DeepNewsModel
from asknews_sdk.dto import alert as alert_dto


GPT_6_ASTRA = "gpt-6-astra"


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
