from typing import ClassVar, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import AnyUrl, AwareDatetime, BaseModel, Field
from typing_extensions import Annotated


class GeoCoordinate(BaseModel):
    latitude: Annotated[float, Field(title="Latitude")]
    longitude: Annotated[float, Field(title="Longitude")]
    metadata: Annotated[Dict, Field(title="Metadata")]


class GraphRelationships(BaseModel):
    nodes: List[Dict[Literal["id", "type", "detailed_type", "ner_type"], str]]
    edges: List[Dict[Literal["from", "to", "label"], str]]


class Assets(BaseModel):
    images: Annotated[Optional[List[str]], Field(None, title="Images")]
    vidoes: Annotated[Optional[List[str]], Field(None, title="Videos")]


class SocialEmbeds(BaseModel):
    instagram: List[str] = []
    facebook: List[str] = []
    x: List[str] = []
    bluesky: List[str] = []


class BaseSchema(BaseModel):
    __content_type__: ClassVar[str] = "application/json"


class RedditEntities(BaseModel):
    DATE: Annotated[Optional[List[str]], Field([], title="Date")]
    EVENT: Annotated[Optional[List[str]], Field([], title="Event")]
    GPE: Annotated[Optional[List[str]], Field([], title="Gpe")]
    ORG: Annotated[Optional[List[str]], Field([], title="Org")]
    PERSON: Annotated[Optional[List[str]], Field([], title="Person")]
    NORP: Annotated[Optional[List[str]], Field([], title="Norp")]
    CARDINAL: Annotated[Optional[List[str]], Field([], title="Cardinal")]


class Entities(BaseModel):
    Person: Annotated[Optional[List[str]], Field([], title="Person")]
    Organization: Annotated[Optional[List[str]], Field([], title="Organization")]
    Location: Annotated[Optional[List[str]], Field([], title="Location")]
    Nationality: Annotated[Optional[List[str]], Field([], title="Nationality")]
    Date: Annotated[Optional[List[str]], Field([], title="Date")]
    Event: Annotated[Optional[List[str]], Field([], title="Event")]
    Money: Annotated[Optional[List[str]], Field([], title="Money")]
    Law: Annotated[Optional[List[str]], Field([], title="Law")]
    Quantity: Annotated[Optional[List[str]], Field([], title="Quantity")]
    Time: Annotated[Optional[List[str]], Field([], title="Time")]
    Sports: Annotated[Optional[List[str]], Field([], title="Sports")]
    Politics: Annotated[Optional[List[str]], Field([], title="Politics")]
    Title: Annotated[Optional[List[str]], Field([], title="Title")]
    Number: Annotated[Optional[List[str]], Field([], title="Number")]
    Arms: Annotated[Optional[List[str]], Field([], title="Arms")]
    Product: Annotated[Optional[List[str]], Field([], title="Product")]
    Media: Annotated[Optional[List[str]], Field([], title="Media")]
    Transportation: Annotated[Optional[List[str]], Field([], title="Transportation")]
    Religion: Annotated[Optional[List[str]], Field([], title="Religion")]
    Technology: Annotated[Optional[List[str]], Field([], title="Technology")]
    Space: Annotated[Optional[List[str]], Field([], title="Space")]
    Medicine: Annotated[Optional[List[str]], Field([], title="Medicine")]
    Language: Annotated[Optional[List[str]], Field([], title="Language")]
    Science: Annotated[Optional[List[str]], Field([], title="Science")]


class Author(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None


class Article(BaseModel):
    article_url: Annotated[AnyUrl, Field(title="Article Url")]
    article_id: Annotated[UUID, Field(title="Article Id")]
    classification: Annotated[Union[List[str], str], Field(title="Classification")]
    country: Annotated[str, Field(title="Country")]
    source_id: Annotated[str, Field(title="Source Id")]
    page_rank: Annotated[int, Field(title="Page Rank")]
    domain_url: Annotated[str, Field(title="Domain Url")]
    eng_title: Annotated[str, Field(title="Eng Title")]
    entities: Annotated[Entities, Field(title="Entities")]
    image_url: Annotated[Optional[str], Field(None, title="Image Url")]
    keywords: Annotated[List[str], Field(title="Keywords")]
    language: Annotated[str, Field(title="Language")]
    pub_date: Annotated[AwareDatetime, Field(title="Pub Date")]
    summary: Annotated[str, Field(title="Summary. Deprecated, please use Key Points instead.")]
    key_points: Annotated[Optional[List[str]], Field(None, title="Key Points")]
    title: Annotated[str, Field(title="Title")]
    sentiment: Annotated[int, Field(title="Sentiment")]
    medoid_distance: Annotated[Optional[float], Field(title="Medoid Distance")] = None
    markdown_citation: Annotated[Optional[str], Field("", title="Markdown Citation")]
    provocative: Annotated[
        str, Field(title="A measure of how provocative this story update is.")
    ] = "low"
    reporting_voice: Annotated[str, Field(title="The reporting voice of the article.")] = "Unknown"
    entity_relation_graph: Annotated[
        Optional[GraphRelationships], Field(None, title="Entity Relation Graph")
    ] = None
    geo_coordinates: Annotated[
        Optional[Dict[str, GeoCoordinate]], Field(None, title="Geo Coordinates")
    ] = None
    continent: Optional[
        Literal[
            "Africa", "Asia", "Europe", "Middle East", "North America", "South America", "Oceania"
        ]
    ] = None
    assets: Optional[Assets] = None
    social_embeds: Optional[SocialEmbeds] = None
    bias: Optional[
        Literal[
            "Political",
            "Gender",
            "Cultural",
            "Age",
            "Religious",
            "Statement",
            "Illogical Claims",
            "Slant",
            "Source Selection",
            "Omission of Source Attribution",
            "Spin",
            "Sensationalism",
            "Negativity",
            "Subjective Adjectives",
            "Ad Hominem",
            "Mind Reading",
            "Opinion-as-Fact",
            "None",
            "Unknown",
        ]
    ] = None
    authors: Optional[List[Author]] = None


class PingResponse(BaseSchema):
    app: Annotated[str, Field(title="App")]
    version: Annotated[str, Field(title="Version")]
