# AskNews Python SDK

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/asknews?style=flat-square)

Python SDK for the AskNews API.

## Installation

```bash
pip install asknews
```

## Usage

```python
from asknews import AskNewsSDK

ask = AskNewsSDK()
query = "Effect of fed policy on tech sector"

# prompt-optimized string ready to go for any LLM:
news_context = ask.news.search_news(query).as_string
```

And you will have a prompt-optimized string ready to go for any LLM.

Find full details at the [AskNews API documentation](https://docs.asknews.app).

## Support

Join our [Discord](https://discord.gg/2Yw66XXEhY) to see what other people are building, and to get support with your projects.
