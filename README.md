# AskNews Python SDK

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/asknews?style=flat-square)

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
    scopes=["news"]
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

Find full details at the [AskNews API documentation](https://docs.asknews.app).

## Support

Join our [Discord](https://discord.gg/2Yw66XXEhY) to see what other people are building, and to get support with your projects.
