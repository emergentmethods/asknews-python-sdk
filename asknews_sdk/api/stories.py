from typing import Dict, List, Literal, Optional, Union
from uuid import UUID

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.stories import StoriesResponse, StoryResponse


class StoriesAPI(BaseAPI):
    """
    Stories API

    https://docs.asknews.app/en/reference#tag--stories
    """

    def search_stories(
        self,
        query: Optional[str] = None,
        categories: Optional[
            List[
                Literal[
                    "Politics",
                    "Economy",
                    "Finance",
                    "Science",
                    "Technology",
                    "Sports",
                    "Climate",
                    "Environment",
                    "Culture",
                    "Entertainment",
                    "Business",
                    "Health",
                    "International",
                ]
            ]
        ] = None,
        uuids: Optional[List[UUID]] = None,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        sort_by: Optional[
            Literal["published", "coverage", "sentiment", "confidence", "relevance"]
        ] = None,
        sort_type: Optional[Literal["asc", "desc"]] = None,
        continent: Optional[
            Literal[
                "Africa",
                "Asia",
                "Europe",
                "Middle East",
                "North America",
                "South America",
                "Oceania",
            ]
        ] = None,
        offset: Optional[Union[int, str]] = None,
        limit: int = 50,
        expand_updates: bool = False,
        max_updates: int = 11,
        max_articles: int = 5,
        reddit: int = 0,
        method: Literal["nl", "kw", "both"] = "kw",
        obj_type: Optional[List[Literal["story", "story_update"]]] = None,
        provocative: Literal["unknown", "low", "medium", "high", "all"] = "all",
        citation_method: Literal["brackets", "urls", "none"] = "brackets",
        strategy: Literal[
            "default", "topstories", "topstories_continents", "topstories_categories"
        ] = "default",
        *,
        http_headers: Optional[Dict] = None,
    ) -> StoriesResponse:
        """
        Get the news stories.

        https://docs.asknews.app/en/reference#get-/v1/stories

        :param query: The query.
        :type query: Optional[str]
        :param categories: The categories.
        :type categories: Optional[str]
        :param start_timestamp: The start timestamp.
        :type start_timestamp: Optional[int]
        :param end_timestamp: The end timestamp.
        :type end_timestamp: Optional[int]
        :param sort_by_time: Whether to sort by time.
        :type sort_by_time: bool
        :param continent: The continent to filter by.
        :type continent: Optional[str]
        :param offset: The offset.
        :type offset: int
        :param limit: The limit.
        :type limit: int
        :param expand_updates: Whether to expand updates.
        :type expand_updates: bool
        :param max_updates: The max updates per story.
        :type max_updates: int
        :param max_articles: The max articles per update.
        :type max_articles: int
        :param reddit: Amount of reddit threads to include per update.
        :type reddit: int
        :param method: The method to use for searching.
        :type method: str
        :param obj_type: The object type to filter on.
        :type obj_type: List[str]
        :param provocative: The provocative level.
        :type provocative: str
        :param citation_method: The citation method.
        :type citation_method: str
        :param http_headers: The HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The stories response.
        :rtype: StoriesResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/stories",
            query={
                "query": query,
                "categories": categories,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "offset": offset,
                "method": method,
                "sort_by": sort_by,
                "sort_type": sort_type,
                "continent": continent,
                "obj_type": obj_type if obj_type is not None else ["story"],
                "reddit": reddit,
                "limit": limit,
                "expand_updates": expand_updates,
                "max_updates": max_updates,
                "max_articles": max_articles,
                "uuids": uuids,
                "provocative": provocative,
                "citation_method": citation_method,
                "strategy": strategy,
            },
            headers=http_headers,
            accept=[(StoriesResponse.__content_type__, 1.0)],
        )

        return StoriesResponse.model_validate(response.content)

    def get_story(
        self,
        story_id: Union[UUID, str],
        expand_updates: bool = True,
        max_updates: int = 11,
        max_articles: int = 5,
        reddit: int = 0,
        citation_method: Literal["brackets", "urls", "none"] = "brackets",
        condense_auxillary_updates: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> StoryResponse:
        """
        Get a single news story given the ID.

        https://docs.asknews.app/en/reference#get-/v1/stories/-story_id-

        :param story_id: The story ID or URL safe title.
        :type story_id: str
        :param expand_updates: Whether to expand updates.
        :type expand_updates: bool
        :param max_updates: The max updates per story.
        :type max_updates: int
        :param max_articles: The max articles per update.
        :type max_articles: int
        :param reddit: Amount of reddit threads to include per update.
        :type reddit: int
        :param citation_method: The citation method.
        :type citation_method: Literal["brackets", "urls", "none"]
        :param condense_auxillary_updates: Whether to condense auxillary updates.
        :type condense_auxillary_updates: bool
        :param http_headers: The HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The story response.
        :rtype: StoryResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/stories/{story_id}",
            query={
                "expand_updates": expand_updates,
                "max_updates": max_updates,
                "max_articles": max_articles,
                "reddit": reddit,
                "citation_method": citation_method,
                "condense_auxillary_updates": condense_auxillary_updates,
            },
            params={"story_id": story_id},
            headers=http_headers,
            accept=[(StoryResponse.__content_type__, 1.0)],
        )
        return StoryResponse.model_validate(response.content)


class AsyncStoriesAPI(BaseAPI):
    """
    Stories API

    https://docs.asknews.app/en/reference#tag--stories
    """

    async def search_stories(
        self,
        query: Optional[str] = None,
        categories: Optional[
            List[
                Literal[
                    "Politics",
                    "Economy",
                    "Finance",
                    "Science",
                    "Technology",
                    "Sports",
                    "Climate",
                    "Environment",
                    "Culture",
                    "Entertainment",
                    "Business",
                    "Health",
                    "International",
                ]
            ]
        ] = None,
        uuids: Optional[List[UUID]] = None,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        sort_by: Optional[
            Literal["published", "coverage", "sentiment", "relevance", "confidence"]
        ] = None,
        sort_type: Optional[Literal["asc", "desc"]] = None,
        continent: Optional[
            Literal[
                "Africa",
                "Asia",
                "Europe",
                "Middle East",
                "North America",
                "South America",
                "Oceania",
            ]
        ] = None,
        offset: Optional[Union[int, str]] = None,
        limit: int = 50,
        expand_updates: bool = False,
        max_updates: int = 11,
        max_articles: int = 5,
        reddit: int = 0,
        method: Literal["nl", "kw", "both"] = "kw",
        obj_type: Optional[List[Literal["story", "story_update"]]] = None,
        provocative: Literal["unknown", "low", "medium", "high", "all"] = "all",
        citation_method: Literal["brackets", "urls", "none"] = "brackets",
        strategy: Literal[
            "default", "topstories", "topstories_continents", "topstories_categories"
        ] = "default",
        *,
        http_headers: Optional[Dict] = None,
    ) -> StoriesResponse:
        """
        Get the news stories.

        https://docs.asknews.app/en/reference#get-/v1/stories

        :param query: The query.
        :type query: Optional[str]
        :param categories: The categories.
        :type categories: Optional[str]
        :param start_timestamp: The start timestamp.
        :type start_timestamp: Optonal[int]
        :param end_timestamp: The end timestamp.
        :type end_timestamp: Optonal[int]
        :param sort_by_time: Whether to sort by time.
        :type sort_by_time: bool
        :param continent: The continent to filter by.
        :type continent: Optional[str]
        :param offset: The offset.
        :type offset: int
        :param limit: The limit.
        :type limit: int
        :param expand_updates: Whether to expand updates.
        :type expand_updates: bool
        :param max_updates: The max updates per story.
        :type max_updates: int
        :param max_articles: The max articles per update.
        :type max_articles: int
        :param reddit: Amount of reddit threads to include per update.
        :type reddit: int
        :param method: The method to use for searching.
        :type method: str
        :param obj_type: The object type to filter on.
        :type obj_type: List[str]
        :param provocative: The provocative level.
        :type provocative: str
        :param citation_method: The citation method.
        :type citation_method: str
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The stories response.
        :rtype: StoriesResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/stories",
            query={
                "query": query,
                "categories": categories,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "offset": offset,
                "method": method,
                "sort_by": sort_by,
                "sort_type": sort_type,
                "continent": continent,
                "obj_type": obj_type if obj_type is not None else ["story"],
                "reddit": reddit,
                "limit": limit,
                "expand_updates": expand_updates,
                "max_updates": max_updates,
                "max_articles": max_articles,
                "uuids": uuids,
                "provocative": provocative,
                "citation_method": citation_method,
                "strategy": strategy,
            },
            headers=http_headers,
            accept=[(StoriesResponse.__content_type__, 1.0)],
        )

        return StoriesResponse.model_validate(response.content)

    async def get_story(
        self,
        story_id: Union[UUID, str],
        expand_updates: bool = True,
        max_updates: int = 11,
        max_articles: int = 5,
        reddit: int = 0,
        citation_method: Literal["brackets", "urls", "none"] = "brackets",
        condense_auxillary_updates: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> StoryResponse:
        """
        Get a single news story given the ID.

        https://docs.asknews.app/en/reference#get-/v1/stories/-story_id-

        :param story_id: The story ID or URL safe title.
        :type story_id: str
        :param expand_updates: Whether to expand updates.
        :type expand_updates: bool
        :param max_updates: The max updates per story.
        :type max_updates: int
        :param max_articles: The max articles per update.
        :type max_articles: int
        :param reddit: Amount of reddit threads to include per update.
        :type reddit: int
        :param citation_method: The citation method.
        :type citation_method: Literal["brackets", "urls", "none"]
        :param condense_auxillary_updates: Whether to condense auxillary updates.
        :type condense_auxillary_updates: bool
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The story response.
        :rtype: StoryResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/stories/{story_id}",
            query={
                "expand_updates": expand_updates,
                "max_updates": max_updates,
                "max_articles": max_articles,
                "reddit": reddit,
                "citation_method": citation_method,
                "condense_auxillary_updates": condense_auxillary_updates,
            },
            params={"story_id": story_id},
            headers=http_headers,
            accept=[(StoryResponse.__content_type__, 1.0)],
        )
        return StoryResponse.model_validate(response.content)
