# AskNews Python SDK

![Static Badge](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?style=flat-square)


Python SDK for the AskNews API.

## Installation

```bash
pip install asknews
```

## Usage

```python
from asknews_sdk import AskNewsSDK

ask = AskNewsSDK(
    client_id=<"YOUR_CLIENT_ID>",
    client_secret="<YOUR_CLIENT_SECRET>",
    scopes=["news", "chat", "stories", "analytics"]
)

query = "Effect of fed policy on tech sector"

# prompt-optimized string ready to go for any LLM:
news_context = ask.news.search_news(query).as_string
```

And you will have a prompt-optimized string ready to go for any LLM. The API doesn't stop there, explore a wide range of endpoints:

- /stories, high level event tracking and state of the art article clustering
- /forecasts, industry leading forecasting on any real-time event
- /analytics, time-series data on finance and politics
- /chat, an OpenAI compatible endpoint infused with news
- /graph, build any news knowledge graph imaginable from the largest news graph on the planet
- /websearch, search the web and get back an LLM distillation of all the relevant web pages

Find full details at the [AskNews API documentation](https://docs.asknews.app).

## Support

Join our [Discord](https://discord.gg/2Yw66XXEhY) to see what other people are building, and to get support with your projects.
