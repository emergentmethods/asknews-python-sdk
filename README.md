# AskNews Python SDK

![Static Badge](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?style=flat-square)


Python SDK for the AskNews API.

## Installation

```bash
pip install asknews
```

## Usage

- Use `ask.news.search_news()` for a fast, surgical, single-search lookup when you already know the keywords or entities and do not need iterative discovery.
- Use DeepNews (`ask.chat.get_deep_news()` in this SDK) to attach your agent to deep, iterative research across news and other sources: finding and following leads, identifying unknown entities, and connecting evidence across sources.

```python
from asknews_sdk import AskNewsSDK

ask = AskNewsSDK(
    api_key="<YOUR API KEY>",
    scopes=["news", "chat", "stories", "analytics"]
)

query = "NVIDIA earnings"

# Fast lookup: prompt-optimized news context for your LLM.
news_context = ask.news.search_news(query).as_string

# Iterative discovery across news and other sources.
research = ask.chat.get_deep_news(
    messages=[{"role": "user", "content": "Find and follow leads on AI chip supply risks."}],
    sources=["asknews", "google", "wiki"],
    engine="v1.5",
)
print(research.choices[0].message.content)
```

The API doesn't stop there, explore a wide range of endpoints:

- /stories, high level event tracking and state of the art article clustering
- /forecasts, industry leading forecasting on any real-time event
- /analytics, time-series data on finance and politics
- /deepnews, a deep research agent that can explore the new knowledge graph, X, Reddit, Google, Wikipedia and more to build forecasts, reports, analytics, and anything else your system may need.
- /graph, build any news knowledge graph imaginable from the largest news graph on the planet
- /websearch, search the web and get back an LLM distillation of all the relevant web pages

Find full details at the [AskNews API documentation](https://docs.asknews.app).

## Examples

- [Exact-domain distribution Excel report](examples/distribution_report/README.md):
  bounded read-only export using your existing authorized credentials, with offline tests.

## Support

Join our [Discord](https://discord.gg/2Yw66XXEhY) to see what other people are building, and to get support with your projects.
