# AskNews SDK Cookbook

Runnable recipes for the AskNews Python SDK. Each page is generated from
the matching file in `cookbook/recipes/`.

- [Get started: setup and core concepts](00_get_started.md): **Use this when** you are starting with the SDK, or choosing which AskNews endpoint fits your task. Every other recipe builds on the concepts here.
- [Search live news](01_search_live_news.md): **Use this when** your application or agent needs what is being reported now: current context for an LLM, the latest on a topic, or new coverage as it arrives.
- [Search historical news](02_search_historical_news.md): **Use this when** the question is about a defined period in the past: how an event developed, what was reported at a given moment, or dated context for forecasting research and backtests. Coverage goes back to 2023.
- [Paginate news search results](03_paginate_news_search.md): **Use this when** one page of results is not enough: you need every match for a query, or a bulk pull over a long period.
- [Build LLM context from news](04_build_llm_context.md): **Use this when** you retrieve news for your own LLM and want context it can reason over and cite.
- [Search Wikipedia for background](05_search_wikipedia.md): **Use this when** your model needs the background behind the news: who a person is, what a company or institution does, or the history behind an event.
- [Search X (Twitter)](06_search_x_twitter.md): **Use this when** you need what was said on X: an account's own statements, or how people are reacting to an event.
- [Search the live web (Google)](07_search_the_live_web.md): **Use this when** the answer lives on the wider web rather than in news coverage: company blogs, press releases, regulator and court sites, documentation, or pages published minutes ago.
- [Search podcasts](08_search_podcasts.md): **Use this when** you want what people said rather than what was reported: interviews, opinion, and long-form commentary from podcast episodes.
- [Monitor a company](09_monitor_a_company.md): **Use this when** you follow one organization's coverage over time: launches, deals, earnings, leadership changes, and legal issues.
- [Monitor a person](10_monitor_a_person.md): **Use this when** you follow coverage of one person, such as an executive or a politician: what they said, and what was reported about them.
- [Monitor a product, brand, or industry](11_monitor_a_product_brand_or_industry.md): **Use this when** what you follow is a product, a brand, or an industry or market rather than one company, so no single entity filter covers it.
- [Run deep research (DeepNews)](12_run_deep_research.md): **Use this when** you want a researched, cited answer rather than a list of articles: a question that takes more than one search, such as an investigation, a fact-check, a forecast, or a report across many companies. DeepNews plans the searches, follows what it finds across your chosen sources, and writes the answer.
- [Set deep research depth](13_set_deep_research_depth.md): **Use this when** a DeepNews answer or report misses things, or does more research than the question needs. Depth sets how much the agent searches before it answers.
- [Prompt deep research](14_prompt_deep_research.md): **Use this when** you want to guide how DeepNews does its research: which tools it uses and how, what it focuses on, and how it formats the output.
- [Create an alert](15_create_an_alert.md): **Use this when** a question needs revisiting on a schedule: a recurring research report, or a notification when a described event happens.
- [Connect to the AskNews MCP server](16_connect_to_the_mcp_server.md): **Use this when** an LLM should decide which AskNews searches to run: inside an assistant such as Claude, ChatGPT, or Cursor, or in an agent you build.
- [Build an agent on the MCP server](17_build_an_agent_on_mcp.md): **Use this when** you want your own model, loop, and prompt to do the research on AskNews tools, instead of calling DeepNews.
