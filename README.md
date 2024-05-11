# AskNews Python SDk

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/asknews?style=flat-square)

Python SDK for the AskNews API.

## Installation

```bash
pip install asknews
```

## Usage

```python
import asyncio
from datetime import datetime, timedelta
from asknews_sdk import AskNewsSDK
from openai import AsyncOpenAI

an_client = AskNewsSDK(
        client_id="your_client_id",
        client_secret="your_client_secret",
        scopes={"chat", "news", "stories"},
)
oai_client = AsyncOpenAI(api_key="")


async def main():
    """
    Example usage of the AskNews SDK
    """
    # Let's say you have some context from a conversation:
    user = {"role": "user", "content": "What is the current political situation in Germany?"}

    # and you want your LLM to have access to up-to-the-minute news.
    # Grab a prompt-optimized string ready to go for your LLM:
    response = await an_client.news.search_news(
        query=user["content"], # any natural language query
        n_articles=10, # control the number of articles to build
        return_type="string",  # you can also ask for "dicts" if you want more info
        method="nl"  # use "bl" for natural language for your search, or "kw" for keyword search
    )
    # now you have a prompt optimized string:
    news_artices = response.as_string

    # simply infuse that string into the prompt:
    system = {"role": "system", "content": f"A chat between a curious user and an artificial intelligence Assistant. The Assistant has access to the following news articles that may be useful for answering the User's questions: {news_articles}"}
    response = await oai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system, user]
    )

    ## Getting AskNews custom stories and reddit info
    # search through AskNews stories 
    response = await sdk.stories.search_stories(
        query="American politics",
        method="kw",
        sort_by="coverage",
        categories=["Politics"],
        reddit=3
    )

    # get news sentiment timeseries for a specific asset
    response = await sdk.analytics.get_asset_sentiment(
        slug="amazon",
        metric="news_positive",
        date_from=datetime.now() - timedelta(days=7),
        date_to=datetime.now(),
    )

if __name__ == "__main__":
    asyncio.run(main())
```
