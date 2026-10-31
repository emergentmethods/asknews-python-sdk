# %% [markdown]
# # Prompting deep research with surgical precision
#
# DeepNews is an agent with tools. The single biggest quality lever is
# telling it **exactly how to use those tools**: which tool, in what order,
# with which parameters, and what to do when a search comes back empty.
# Leaving it to guess works for simple questions and fails for monitoring
# and reporting.
#
# The patterns below come from production daily monitoring reports.
#
# ## 1. Name the role, the goal, and the tools
#
# ```text
# You are a senior investment research analyst monitoring a portfolio of
# companies and key individuals.
#
# You have access to search_news, search_x_twitter, and search_google tools
# to conduct your research.
# ```
#
# Refer to tools by name, the same way every time. Stream a run once
# ([12 Deep research basics](12_deep_research_basics.md)) to see the exact
# tool names and argument names the agent uses.
#
# ## 2. Put inputs in delimited, structured blocks
#
# Markdown tables between explicit start/end markers. Include everything
# the agent needs to build a good search: a description (for the query),
# an X handle (for the X search), a website.
#
# ```text
# ------Company Portfolio Start------
# | Company | Description | X.com Handle | Website |
# |---------|-------------|--------------|---------|
# | Ramp | Corporate spend management: cards, bill pay, expenses | tryramp | ramp.com |
# ------Company Portfolio End------
# ```
#
# ## 3. Give a per-item procedure, and make it mandatory
#
# For list-shaped tasks, agents tend to go deep on the first few items and
# skim the rest. Prevent that by prescribing a loop:
#
# ```text
# For each company, perform Step 1 (news/web), then Step 2 (social media),
# then move to the next company and repeat. Both steps are required for
# every company before moving on.
# ```
#
# Size `search_depth` to the loop: items x steps. See
# [13 Deep research depth](13_deep_research_depth.md).
#
# ## 4. Show the exact tool parameters, with placeholders
#
# This is the "surgical" part. Write the call you want, in a tagged block:
#
# ```text
# <search_news params>
# entity_guarantee="Organization:[Company Name]"
# query="[Company Description], [X.com Handle], [Website], Funding, M&A, ..."
# hours_back=24
# time_filter="pub_date"
# n_articles=5
# </search_news params>
# ```
#
# Everything in [09 Tracking a company](09_tracking_a_company.md) and
# [11 Tracking a product, brand, or industry](11_tracking_a_product_brand_or_industry.md)
# applies here: you are teaching the agent your best `search_news`
# parameters.
#
# ## 5. Say which parameters are fixed and which are a starting point
#
# Fixed (the agent must not change them):
#
# ```text
# **IMPORTANT: Always set hours_back=24 in search_news calls. Never expand
# this value.**
# **IMPORTANT: Always use min_faves:20 as the engagement threshold. Do not
# lower it.**
# ```
#
# Starting point (the agent may adapt):
#
# ```text
# These are good starting parameters. You can shift them to dig deeper into
# a deal you found, or broaden them if you find nothing.
# ```
#
# Agents widen time windows when they find nothing. If recency is the point
# of the report, say so in bold.
#
# ## 6. Define a fallback chain
#
# ```text
# If search_news returns nothing for a company, follow up with search_google:
# google_keywords="[Company Name] [1-6 relevant keywords]"
# lookback=24
# strict=True
# ```
#
# And a follow-up rule for the opposite case:
#
# ```text
# If a company has a lot of news, run a second search focused on the most
# important topic from the first search.
# ```
#
# ## 7. Define fuzzy terms
#
# If the task says "tech company", "material", or "rumor", define it,
# including what to exclude. Ask for dedicated searches for things that are
# easy to miss (e.g. rumors: "in talks to acquire", "exploring sale",
# "people familiar with the matter").
#
# ## 8. Be strict about dates and citations in the report
#
# ```text
# - Every claim must have a verifiable source link. Omit unsourced claims.
# - If you cannot confirm a source was published within the last 24 hours,
#   omit the item entirely. Do not include it with a caveat.
# - If a recent source only follows up on a deal announced more than 24
#   hours ago, omit it. Inclusion requires a new primary development.
# ```
#
# ## 9. Specify the output precisely
#
# Section order, per-item headers, what to omit (entities with no news),
# no preamble, ordering of priority items, and cross-references (e.g. a
# CEO's update links to their company's section).
#
# ## Full example
#
# The prompt below combines all of the above for a daily portfolio and
# people monitor.

# %%
import os

from asknews_sdk import AskNewsSDK


ask = AskNewsSDK(
    api_key=os.environ["ASKNEWS_API_KEY"],
    scopes=["chat", "news"],
)

companies = """
| Company | Description | X.com Handle | Website |
|---------|-------------|--------------|---------|
| Ramp | Corporate spend management platform with cards, bill pay, expense tracking, and accounting automation | tryramp | ramp.com |
| Databricks | Unified data and AI lakehouse platform for analytics, data engineering, and machine learning | databricks | databricks.com |
| Anduril Industries | Defense technology company building autonomous systems and software for national security | anduriltech | anduril.com |
| Figma | Collaborative interface design platform with real-time editing, prototyping, and dev handoff | figma | figma.com |
"""

individuals = """
| Name | Description | X.com Handle |
|------|-------------|--------------|
| Dylan Field | Co-founder and CEO of Figma | zoink |
| Palmer Luckey | Founder of Anduril Industries; founder of Oculus VR | PalmerLuckey |
"""

prompt = f"""
You are a senior investment research analyst monitoring a portfolio of technology companies (listed between ------Company Portfolio Start------ and ------Company Portfolio End------) and key individuals (listed between ------Key Individuals Start------ and ------Key Individuals End------).

You have access to search_news, search_x_twitter, and search_google tools to conduct your research.

Your goal is to produce a concise briefing on material developments relevant to equity owners.

## Research Instructions

For each company and each individual, identify material developments **from the last 24 hours only**.

For each company or person, perform Step 1 (news/web), then Step 2 (social media), then move to the next one and repeat. Both steps are required for every company and every person.

### Step 1: News/Web Search

Search one company or person at a time.

<search_news params for a company>
entity_guarantee="Organization:[Company Name]"
query="[Company Description], [X.com Handle], [Website], Funding, Valuation, IPO, Debt, Partnerships, M&A, Leadership Changes, Product Launches, Regulatory Actions, Lawsuits, Executive Statements"
hours_back=24
time_filter="pub_date"
n_articles=5
</search_news params for a company>

<search_news params for a person>
entity_guarantee="Person:[Name]"
query="[Description], [X.com Handle], public statement, interview, board appointment, role change, investments, new venture, legal issues, stock sales"
hours_back=24
time_filter="pub_date"
n_articles=5
</search_news params for a person>

If there is a lot of news for a company or person, run a second search focused on the most important topic you found.

If search_news returns nothing, follow up with search_google:

<search_google params>
google_keywords="[Name] [one to six relevant keywords]"
lookback=24
strict=True
</search_google params>

**IMPORTANT: Always use hours_back=24 and lookback=24. Never expand these values.**

### Step 2: Social Media

If the company or person has an X.com handle, you MUST search X. Look for product announcements, partnership or customer wins, executive statements, and posts with unusually high engagement.

<search_x_twitter params>
advanced_search_expression="(from:[handle] OR @[handle]) min_faves:20"
lookback=24
</search_x_twitter params>

**IMPORTANT: Only include posts from the last 24 hours. Do not lower min_faves.**

## Report Instructions

- Write a concise title with the report date. No preamble or executive summary.
- Only include companies and people with material news. Omit the rest entirely, and omit a section if it would be empty.
- Explain why each development matters to equity owners, not just what happened. Quantify where possible.
- Every claim needs an inline source link. If several sources support a claim, cite each.
- If you cannot confirm a source was published within the last 24 hours, omit the item.
- Flag contradictions between sources, and label unconfirmed reports as such.
- Do not list sources at the end.

Structure:

## Portfolio Company Updates
One subsection per company. Ramp and Databricks first (if they have news), then the others.
Add a line "**Key Individuals**: [Name]" when a key individual is involved.

## Key Individual Updates
One subsection per person.
Add a line "**Portfolio Companies**: [Company]" when a portfolio company is involved.

------Company Portfolio Start------
{companies}
------Company Portfolio End------

------Key Individuals Start------
{individuals}
------Key Individuals End------
"""

n_items = 4 + 2
response = ask.chat.get_deep_news(
    messages=[{"role": "user", "content": prompt}],
    sources=["asknews", "x", "google"],
    model="claude-sonnet-5-5",
    engine="v2.0",
    search_depth=n_items * 2,
    max_depth=n_items * 4,
    max_parallel_tool_calls=1,  # keep the per-entity order
    enable_source_pruning=True,
    filter_params={
        "n_articles": 5,
        "time_filter": "pub_date",
        "hours_back": 24,
        "languages": ["en"],
        "page_rank": 100000,
    },
)
print(response.choices[0].message.content)

# %% [markdown]
# ## Example: a theme instead of a list
#
# For a theme there is no per-item loop. Give a starting search and a rule
# for following up on what it finds.
#
# ```text
# You are a senior investment research analyst. Track transfers of
# ownership, acquisitions, sales, or significant ownership changes for
# professional sports teams based in the American West, from the last
# 24 hours only.
#
# ### Step 1: News/Web Search
# <search_news params>
# query="West sports team ownership transfer acquisition sale NFL NBA MLB NHL MLS"
# hours_back=24
# time_filter="pub_date"
# n_articles=5
# </search_news params>
#
# If a specific team or individual surfaces, follow up with a targeted
# search using entity_guarantee="Organization:[Team Name]" or
# entity_guarantee="Person:[Name]".
#
# ### Step 2: Social Media
# <search_x_twitter params>
# advanced_search_expression="sports team ownership sale acquisition min_faves:20"
# lookback=24
# </search_x_twitter params>
#
# For each development report: Deal/Development, Status
# (Rumor/Announced/Confirmed/Closed), and inline source links.
# ```
#
# Depth for a single theme: `search_depth=5`, `max_depth=10`.
#
# ## Example: "what's on every front page"
#
# Steering toward high-credibility sources with parameters instead of
# just asking for them:
#
# ```text
# <search_news params>
# query="Bloomberg, TechCrunch, The Information, Axios, Financial Times, Reuters top tech headlines"
# categories=["Technology", "Business", "Finance"]
# page_rank=10000
# time_filter="pub_date"
# </search_news params>
#
# Use X to verify how much attention a topic is getting:
# <search_x_twitter params>
# advanced_search_expression="(TechCrunch OR Bloomberg OR Reuters) min_faves:1000"
# lookback=24
# </search_x_twitter params>
#
# Write the top 5 headlines, one sentence each, as bullet points.
# ```
#
# Depth: `search_depth=15`, `max_depth=20`.
