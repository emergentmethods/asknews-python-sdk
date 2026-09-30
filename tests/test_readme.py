import json
import re
from pathlib import Path

from tests.api.test_chat import MockCreateDeepNewsResponse
from tests.api.test_news import MockSearchResponse


def test_readme_usage_example_runs_with_mocked_responses(response_mock, capsys):
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
    examples = re.findall(r"```python\n(.*?)```", readme, re.DOTALL)
    assert examples

    news_response = MockSearchResponse.build(as_string="News context")
    deepnews_response = MockCreateDeepNewsResponse.build()
    news_route = response_mock.get("/v1/news/search").respond(
        content=news_response.model_dump_json()
    )
    research_route = response_mock.post("/v1/chat/deepnews").respond(
        content=deepnews_response.model_dump_json()
    )

    namespace = {}
    try:
        for example in examples:
            exec(compile(example, "README.md", "exec"), namespace)
        assert namespace["news_context"] == "News context"
        assert namespace["research"].model_dump(mode="json") == deepnews_response.model_dump(
            mode="json"
        )
        assert capsys.readouterr().out.strip() == (
            deepnews_response.choices[0].message.content.strip()
        )
        assert news_route.calls.last.request.url.params["query"] == namespace["query"]
        payload = json.loads(research_route.calls.last.request.content)
        assert payload["messages"][0]["role"] == "user"
        assert payload["sources"] == ["asknews", "google", "wiki"]
        assert payload["engine"] == "v1.5"
        assert payload["stream"] is False
        assert payload["model"] == "claude-sonnet-4-6"
    finally:
        if "ask" in namespace:
            namespace["ask"].close()
