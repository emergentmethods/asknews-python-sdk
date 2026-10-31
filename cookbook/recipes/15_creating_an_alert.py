# %% [markdown]
# # Creating an alert
#
# An alert runs on a cron schedule, gathers information, optionally checks
# a condition, optionally writes a report, and fires triggers (email,
# webhook, Google Docs). The AskNews side does the scheduling, so you do
# not need to run anything yourself.
#
# ## Choose the alert type
#
# | `alert_type` | Behavior | Use it for |
# |---|---|---|
# | `"ReportAbout"` | Every run writes a report and fires triggers. | Daily/weekly briefings, monitoring reports |
# | `"AlwaysAlertWhen"` | Every run checks the `query` condition against the sources; fires whenever it is met. | "Tell me every time X happens" |
# | `"AlertOnceIf"` | Same check, but disables itself after the first hit. | "Tell me when X finally happens" |
#
# ## The pieces
#
# - `cron`: when to run, in UTC. `"0 13 * * 1-5"` is 13:00 UTC on weekdays.
#   See https://crontab.run.
# - `report`: a `DeepNewsReportRequest` (or a list of them; their outputs
#   are concatenated in order into one report). The `prompt` is the
#   research instruction and `params` is a `DeepNewsReportParams` with the
#   same knobs as `get_deep_news` (model, sources, depth, filter_params).
# - `triggers`: what happens when the alert fires. Email, webhook, or
#   Google Docs.
# - `query` + `sources` + `model`: for condition alerts. `sources` says
#   where to look (AskNews search, web, DeepNews, Telegram, Bluesky),
#   `query` is the condition, and `model` is the (small, cheap) model that
#   checks it. This is a different model from the report model.
#
# Best practices:
#
# - **Put all the research instructions in the report prompt.** For a
#   report, the prompt *is* the alert. Everything in
#   [14 Prompting deep research](14_prompting_deep_research.md) applies:
#   tool parameters, per-item procedures, strict date rules.
# - **Size depth to the prompt** ([13 Deep research depth](13_deep_research_depth.md)).
#   A 50-entity monitor with `search_depth=2` will skip most entities.
# - **Enforce recency in two places**: in the prompt ("last 24 hours only,
#   never expand hours_back") and in `filter_params` (`hours_back`,
#   `time_filter="pub_date"`). Match `hours_back` to the cron interval.
# - **Split big monitors into several reports** in one alert (one per
#   theme or list). Each gets its own prompt and depth, and the outputs are
#   concatenated.
# - **Test with `run_alert`** before you wait for the schedule, and read
#   `list_alert_logs` to see what happened.
# - Alert reports use DeepNews `engine="v1.5"`.

# %%
import os

from asknews_sdk import AskNewsSDK
from asknews_sdk.dto.alert import (
    CreateAlertRequest,
    DeepNewsReportParams,
    DeepNewsReportRequest,
    UpdateAlertRequest,
)


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["chat", "news"],
)

# %% [markdown]
# ## A daily DeepNews report (ReportAbout)
#
# A weekday-morning portfolio briefing, emailed. The prompt follows the
# patterns from recipe 14, abbreviated here.

# %%
companies = """
| Company | Description | X.com Handle | Website |
|---------|-------------|--------------|---------|
| Ramp | Corporate spend management: cards, bill pay, expense tracking | tryramp | ramp.com |
| Databricks | Data and AI lakehouse platform for analytics and ML | databricks | databricks.com |
| Anduril Industries | Defense technology: autonomous systems and software | anduriltech | anduril.com |
"""

portfolio_prompt = f"""
You are a senior investment research analyst monitoring the portfolio companies listed between ------Company Portfolio Start------ and ------Company Portfolio End------.

You have access to search_news, search_x_twitter, and search_google tools.

## Research Instructions

For each company, perform Step 1 then Step 2, then move to the next company. Both steps are required for every company. Only developments **from the last 24 hours**.

### Step 1: News/Web Search
<search_news params>
entity_guarantee="Organization:[Company Name]"
query="[Company Description], [X.com Handle], [Website], Funding, Valuation, M&A, Partnerships, Leadership Changes, Product Launches, Regulatory Actions, Lawsuits"
hours_back=24
time_filter="pub_date"
n_articles=5
</search_news params>

If search_news returns nothing, use search_google:
<search_google params>
google_keywords="[Company Name] [one to six relevant keywords]"
lookback=24
strict=True
</search_google params>

### Step 2: Social Media
<search_x_twitter params>
advanced_search_expression="(from:[handle] OR @[handle]) min_faves:20"
lookback=24
</search_x_twitter params>

**IMPORTANT: Always use hours_back=24 and lookback=24. Never expand these values.**

## Report Instructions
- Concise title with the report date. No preamble.
- One subsection per company with material news. Omit companies with no news.
- Explain why each development matters to equity owners.
- Every claim needs an inline source link. Omit items you cannot date to the last 24 hours.

------Company Portfolio Start------
{companies}
------Company Portfolio End------
"""

payload = CreateAlertRequest(
    title="Daily Portfolio Briefing",
    alert_type="ReportAbout",
    cron="0 13 * * 1-5",  # 13:00 UTC, Monday-Friday
    report=[
        DeepNewsReportRequest(
            identifier="deepnews",
            prompt=portfolio_prompt,
            include_appendix=False,
            timezone="America/New_York",
            params=DeepNewsReportParams(
                model="claude-sonnet-5-5",
                engine="v1.5",
                sources=["asknews", "x", "google"],
                search_depth=6,  # 3 companies x 2 steps
                max_depth=12,
                max_parallel_tool_calls=1,
                enable_source_pruning=True,
                filter_params={
                    "n_articles": 5,
                    "time_filter": "pub_date",
                    "hours_back": 24,
                    "languages": ["en"],
                    "page_rank": 100000,
                },
            ),
        ),
    ],
    triggers=[
        {
            "action": "email",
            "params": {"to": "analyst@example.com", "subject": "Daily Portfolio Briefing"},
        },
    ],
)

alert = ask.chat.create_alert(payload)
print("alert id:", alert.id)

# %% [markdown]
# ## Several reports in one alert
#
# Each `DeepNewsReportRequest` has its own prompt and depth. The outputs
# are concatenated, in order, into one email. Share the common settings.

# %%
def theme_report(prompt: str) -> DeepNewsReportRequest:
    return DeepNewsReportRequest(
        identifier="deepnews",
        prompt=prompt,
        include_appendix=True,
        params=DeepNewsReportParams(
            model="claude-sonnet-5-5",
            engine="v1.5",
            sources=["asknews", "x", "google"],
            search_depth=5,
            max_depth=10,
            filter_params={"n_articles": 5, "time_filter": "pub_date", "hours_back": 24},
        ),
    )


multi_report = CreateAlertRequest(
    title="Daily Themes",
    alert_type="ReportAbout",
    cron="10 13 * * 1-5",
    report=[
        theme_report("Track ownership changes of professional sports teams ... (last 24 hours only)"),
        theme_report("Track material news for billionaires based in the American West ... (last 24 hours only)"),
        theme_report("Track sales and acquisitions of ski resorts in North America ... (last 24 hours only)"),
    ],
    triggers=[{"action": "email", "params": {"to": "analyst@example.com", "subject": "Daily Themes"}}],
)
# ask.chat.create_alert(multi_report)

# %% [markdown]
# ## A condition alert with a webhook (AlwaysAlertWhen)
#
# Check AskNews every 15 minutes and post to a webhook whenever the
# condition is met. The AskNews source `params` are the `search_news`
# filters. In a webhook `payload`, `{message}` is replaced with the alert
# message.

# %%
condition_alert = CreateAlertRequest(
    title="Paris protests",
    alert_type="AlwaysAlertWhen",
    query="Alert me if there is a protest or demonstration happening in Paris.",
    cron="*/15 * * * *",
    model="gpt-4o-mini",
    sources=[
        {
            "identifier": "asknews",
            "params": {
                "query": "protest, demonstration, rally, march, strike, clashes",
                "entity_guarantee": ["Location:Paris"],
                "hours_back": 1,
                "time_filter": "crawl_date",
                "n_articles": 20,
            },
        },
    ],
    triggers=[
        {
            "action": "webhook",
            "params": {
                "url": "https://example.com/hooks/asknews",
                "payload": {"text": "Paris protest alert: {message}"},
            },
        },
    ],
)
# ask.chat.create_alert(condition_alert)

# %% [markdown]
# ## Managing alerts

# %%
# Run now instead of waiting for the schedule (best way to test a prompt).
ask.chat.run_alert(alert_id=alert.id)

# What happened on each run: whether it fired, why, and the report.
logs = ask.chat.list_alert_logs(alert_id=alert.id, per_page=5)
for log in logs.items:
    print(log.created_at, "fired" if log.alert else "not fired", log.report_url)
    print(log.reasoning)

# Partial update: only the fields you set change.
ask.chat.update_alert(
    alert_id=alert.id,
    payload=UpdateAlertRequest(cron="30 12 * * 1-5"),
)

# Pause and resume.
ask.chat.update_alert(alert_id=alert.id, payload=UpdateAlertRequest(active=False))

# List all of your alerts.
for a in ask.chat.list_alerts(all=True).items:
    print(a.id, a.title, a.cron, "active" if a.active else "paused")

# Delete.
ask.chat.delete_alert(alert_id=alert.id)
