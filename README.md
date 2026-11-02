# AskNews Python SDK

![Static Badge](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?style=flat-square)


Python SDK for the AskNews API.

## Python support

Supported Python versions: **3.10–3.14**.

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

The API doesn't stop there, checkout the full set of recipes in the [Cookbook](cookbook/recipes/index.md) showing off a wide range of endpoints:

- /deepnews, a deep research agent that can explore the new knowledge graph, X, Reddit, Google, Wikipedia and more to build forecasts, reports, analytics, and anything else your system may need.
- /websearch, search the web and get back an LLM distillation of all the relevant web pages
- /wikipedia, high fidelity search on the Wikipedia corpus (open-sourced, https://huggingface.co/datasets/EmergentMethods/en_qdrant_wikipedia)
- /stories, high level event tracking and state of the art article clustering

Find full docs at the [AskNews API documentation](https://docs.asknews.app).

## Support

Join our [Discord](https://discord.gg/2Yw66XXEhY) to see what other people are building, and to get support with your projects.
