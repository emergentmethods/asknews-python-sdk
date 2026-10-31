# %% [markdown]
# # Tracking a person
#
# Same pattern as companies: `entity_guarantee=["Person:<Full Name>"]` to
# guarantee the person is in the article, and a `query` that describes
# who they are and what kinds of developments you care about.
#
# Best practices:
#
# - Use the full name the press uses (`"Person:Jensen Huang"`, not
#   `"Person:Huang"`).
# - Put their role and affiliations in the query. It is what disambiguates
#   two people with the same name, and it ranks role-relevant coverage
#   first.
# - Say what you want: statements, board changes, deals, legal issues,
#   wealth events. A query that lists the *kinds* of developments works
#   much better than the name alone.
# - Use `authors=[...]` when you want articles *written by* someone (a
#   journalist), not *about* them.

# %%
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["news", "chat"],
)

# %% [markdown]
# ## Daily person monitor

# %%
PERSON_EVENTS = (
    "public statement, interview, keynote, board appointment, role change, "
    "investments or deals they are associated with, new venture, "
    "legal or regulatory issues, SEC filings, insider trading disclosures, "
    "stock sales, philanthropy, controversy"
)

response = ask.news.search_news(
    entity_guarantee=["Person:Jensen Huang"],
    query=f"Jensen Huang, co-founder and CEO of NVIDIA, {PERSON_EVENTS}",
    hours_back=24,
    time_filter="pub_date",
    n_articles=10,
    return_type="both",
    premium=True,
)
print(response.as_string)

# %% [markdown]
# ## Person in a specific context
#
# Guarantee two entities with `entity_guarantee_op="AND"` to find articles
# that involve both, e.g. a person and a company or a place.

# %%
response = ask.news.search_news(
    entity_guarantee=["Person:Daniel Ek", "Organization:Helsing"],
    entity_guarantee_op="AND",
    query="Daniel Ek Helsing chairman defense AI investment",
    hours_back=720,
    historical=True,
    n_articles=10,
    return_type="dicts",
    premium=True,
)

# %% [markdown]
# ## Articles written by a journalist

# %%
response = ask.news.search_news(
    authors=["Kaitlan Collins"],
    hours_back=168,
    historical=True,
    n_articles=10,
    return_type="dicts",
)

# %% [markdown]
# ## A watchlist of people
#
# Search each person separately. One search with ten names in the entity
# guarantee returns whoever dominates the news cycle and hides everyone
# else.

# %%
watchlist = [
    ("Vlad Tenev", "co-founder and CEO of Robinhood", "vladtenev"),
    ("Dylan Field", "co-founder and CEO of Figma", "zoink"),
    ("Arthur Mensch", "co-founder and CEO of Mistral AI", "arthurmensch"),
]

briefing = {}
for name, description, handle in watchlist:
    news = ask.news.search_news(
        entity_guarantee=[f"Person:{name}"],
        query=f"{name}, {description}, {PERSON_EVENTS}",
        hours_back=24,
        time_filter="pub_date",
        n_articles=5,
        return_type="string",
        premium=True,
    )
    posts = ask.chat.live_web_search(
        queries=[f"(from:{handle} OR @{handle}) min_faves:20"],
        domains=["x.com"],
        lookback=24,
    )
    briefing[name] = {"news": news.as_string, "x": posts.as_string}

# %% [markdown]
# For a watchlist that should run every morning and land in an inbox, let
# DeepNews do these searches inside an alert. See
# [15 Creating an alert](15_creating_an_alert.md).
