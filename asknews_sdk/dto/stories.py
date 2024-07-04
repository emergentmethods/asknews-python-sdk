from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import AnyUrl, AwareDatetime, BaseModel, Field
from typing_extensions import Annotated

from asknews_sdk.dto.base import Article, BaseSchema, Entities, RedditEntities


class RedditPerspective(BaseModel):
    sentiment: Annotated[Union[int, float], Field(title="Sentiment")]
    relevant: Annotated[bool, Field(title="Relevant")]
    summary: Annotated[str, Field(title="Summary")]


class RedditThread(BaseModel):
    author: Annotated[str, Field(title="Author")]
    author_comment_karma: Annotated[int, Field(title="Author Comment Karma")]
    author_link_karma: Annotated[int, Field(title="Author Link Karma")]
    body: Annotated[str, Field(title="Body")]
    classification: Annotated[Union[List[str], str], Field(title="Classification")]
    comments: Annotated[List[RedditComment], Field(title="Comments")]
    comments_count: Annotated[int, Field(title="Comments Count")]
    date: Annotated[AwareDatetime, Field(title="Date")]
    entities: RedditEntities
    id: Annotated[UUID, Field(title="Id")]
    key_takeaways: Annotated[List[str], Field(title="Key Takeaways")]
    keywords: Annotated[List[str], Field(title="Keywords")]
    sentiment: Annotated[Union[int, float], Field(title="Sentiment")]
    subreddit_name: Annotated[str, Field(title="Subreddit Name")]
    subreddit_url: Annotated[str, Field(title="Subreddit Url")]
    summary: Annotated[str, Field(title="Summary")]
    title: Annotated[str, Field(title="Title")]
    topic: Annotated[str, Field(title="Topic")]
    upvotes: Annotated[int, Field(title="Upvotes")]
    url: Annotated[str, Field(title="Url")]
    main_speculation: Annotated[str, Field(title="Main Speculation/conspiracy/discussion")]


class RedditComment(BaseModel):
    author: Annotated[str, Field(title="Author")]
    body: Annotated[str, Field(title="Body")]
    date: Annotated[AwareDatetime, Field(title="Date")]
    upvotes: Annotated[int, Field(title="Upvotes")]


class IntraClusterStatistics(BaseModel):
    cluster_articles_pct: Annotated[Optional[float], Field(0.0, title="Cluster Articles Pct")]
    cluster_countries_pct: Annotated[Optional[float], Field(0.0, title="Cluster Countries Pct")]
    cluster_domains_pct: Annotated[Optional[float], Field(0.0, title="Cluster Domains Pct")]
    cluster_languages_pct: Annotated[Optional[float], Field(0.0, title="Cluster Languages Pct")]
    cluster_probabilities: Annotated[
        Optional[Dict[str, Union[int, float]]], Field({}, title="Cluster Probabilities")
    ]


class GraphRelationships(BaseModel):
    nodes: List[Dict[Literal["id", "type", "detailed_type"], str]]
    edges: List[Dict[Literal["from", "to", "label"], str]]


class StoryResponseUpdate(BaseModel):
    uuid: Annotated[UUID, Field(title="Uuid")]
    cluster_articles: Annotated[List[Article], Field(title="Cluster Articles")]
    prompt_articles: Annotated[List[Article], Field(title="Prompt Articles")]
    n_articles: Annotated[int, Field(title="N Articles")]
    entities: Entities
    headline: Annotated[str, Field(title="Headline")]
    story: Annotated[str, Field(title="Story")]
    story_update_ts: Annotated[int, Field(title="Story Update Ts")]
    sources_urls: Annotated[Dict[str, int], Field(title="Sources Urls")]
    languages_pct: Annotated[Dict[str, float], Field(title="Languages Pct")]
    countries_pct: Annotated[Dict[str, float], Field(title="Countries Pct")]
    key_takeaways: Annotated[List[str], Field(title="Key Takeaways")]
    contradictions: Annotated[List[str], Field(title="Contradictions")]
    continent: Annotated[str, Field(title="Continent")]
    people: Annotated[List[str], Field(title="People")]
    locations: Annotated[List[str], Field(title="Locations")]
    new_information: Annotated[str, Field(title="New Information")]
    image_url: Annotated[AnyUrl, Field(title="Image Url")]
    url_safe_title: Annotated[str, Field(title="Url Safe Title")]
    story_uuid: Annotated[UUID, Field(title="Story Uuid")]
    categories: Annotated[List[str], Field(title="Categories")]
    image_prompt: Annotated[str, Field(title="Image Prompt")]
    reddit_perspective: RedditPerspective
    reddit_threads: Annotated[List[RedditThread], Field(title="Reddit Threads")]
    languages: Annotated[Dict[str, int], Field(title="Languages")]
    keywords: Annotated[List[str], Field(title="Keywords")]
    intra_cluster_statistics: IntraClusterStatistics
    silhouette_score: Annotated[Dict[str, Any], Field(title="Silhouette Score")]
    article_ids: Annotated[List[UUID], Field(title="Article Ids")]
    countries: Annotated[Dict[str, int], Field(title="Countries")]
    markdown_citations: Annotated[List[str], Field(title="Markdown Citations")]
    confidence: Annotated[Optional[float], Field(0.0, title="Confidence")]
    provocative: Annotated[
        str, Field(title="A measure of how provocative this story update is.")
    ] = "low"
    reporting_voice: Annotated[
        str,
        Field(
            title="An overview of the reporting voice for the articles "
            "comprising this story update."
        ),
    ] = "Unknown"
    relationships: Annotated[
        GraphRelationships, Field(title="Relationships mapped out between entities.")
    ]
    mermaid: Annotated[str, Field(title="Mermaid syntax for the relationships graph.")]
    alignment: Annotated[int, Field(title="Alignment")]


class StoryResponse(BaseSchema):
    uuid: Annotated[UUID, Field(title="Uuid")]
    categories: Annotated[List[str], Field(title="Categories")]
    countries: Annotated[Dict[str, int], Field(title="Countries")]
    countries_pct: Annotated[Dict[str, float], Field(title="Countries Pct")]
    current_update_uuid: Annotated[str, Field(title="Current Update Uuid")]
    requested_update_uuid: Annotated[str, Field(title="Requested Update Uuid")]
    generate_image: Annotated[bool, Field(title="Generate Image")]
    keywords: Annotated[List[str], Field(title="Keywords")]
    languages: Annotated[Dict[str, int], Field(title="Languages")]
    languages_pct: Annotated[Dict[str, float], Field(title="Languages Pct")]
    locations: Annotated[List[str], Field(title="Locations")]
    meta_type: Annotated[str, Field(title="Meta Type")]
    n_articles: Annotated[List[int], Field(title="N Articles")]
    n_updates: Annotated[int, Field(title="N Updates")]
    people: Annotated[List[str], Field(title="People")]
    reddit_sentiment: Annotated[List[Union[int, float]], Field(title="Reddit Sentiment")]
    reddit_sentiment_timestamps: Annotated[List[int], Field(title="Reddit Sentiment Timestamps")]
    rolling_sentiment: Annotated[List[float], Field(title="Rolling Sentiment")]
    sentiment: Annotated[List[int], Field(title="Sentiment")]
    sentiment_timestamps: Annotated[List[int], Field(title="Sentiment Timestamps")]
    sources: Annotated[Dict[str, int], Field(title="Sources")]
    sources_urls: Annotated[Dict[str, int], Field(title="Sources Urls")]
    topic: Annotated[str, Field(title="Topic")]
    topics: Annotated[List[str], Field(title="Topics")]
    updates: Annotated[List[StoryResponseUpdate], Field(title="Updates")]
    updated_ts: Annotated[int, Field(title="Updated Ts")]
    update_uuids: Annotated[List[UUID], Field(title="Update Uuids")]


class StoriesResponse(BaseSchema):
    stories: Annotated[List[StoryResponse], Field(title="Stories")]
    offset: Annotated[Optional[Union[int, str]], Field(title="Offset")]
