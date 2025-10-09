from typing import Dict, List, Optional

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.wiki import WikiSearchResponse


class WikiAPI(BaseAPI):
    """
    Wiki API

    https://docs.asknews.app/en/reference#tag--wiki
    """

    def search_wiki(
        self,
        query: str = "",
        n_documents: int = 10,
        neighbor_chunks: int = 1,
        full_articles: bool = False,
        hybrid_search: bool = False,
        diversify: float = 0.0,
        string_guarantee: List[str] = None,
        include_main_section: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiSearchResponse:
        """
        Search for wiki articles given a query.

        https://docs.asknews.app/en/reference#get-/v1/wiki/search

        :param query: Query string that can be any phrase, keyword, question, or
            paragraph.
        :type query: str

        :return: The search response.
        :rtype: SearchResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/wiki/search",
            query={
                "query": query,
                "n_documents": n_documents,
                "neighbor_chunks": neighbor_chunks,
                "full_articles": full_articles,
                "hybrid_search": hybrid_search,
                "string_guarantee": string_guarantee,
                "diversify": diversify,
                "include_main_section": include_main_section,
            },
            headers=http_headers,
            accept=[(WikiSearchResponse.__content_type__, 1.0)],
        )
        return WikiSearchResponse.model_validate(response.content)


class AsyncWikiAPI(BaseAPI):
    """
    News API

    https://docs.asknews.app/en/reference#tag--wiki
    """

    async def search_wiki(
        self,
        query: str = "",
        n_documents: int = 10,
        neighbor_chunks: int = 1,
        full_articles: bool = False,
        hybrid_search: bool = False,
        diversify: float = 0.0,
        string_guarantee: List[str] = None,
        include_main_section: bool = False,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiSearchResponse:
        """
        Search for news articles given a query.

        https://docs.asknews.app/en/reference#get-/v1/news/search

        :param query: Query string that can be any phrase, keyword, question, or
            paragraph.
            If method='nl', then this will be used as a natural language query.
            If method='kw', then this will be used as a direct keyword query.
        :type query: str
        :param n_articles: Number of articles to return, defaults to 10
        :type n_articles: Optional[int]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The search response.
        :rtype: SearchResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/wiki/search",
            query={
                "query": query,
                "n_documents": n_documents,
                "neighbor_chunks": neighbor_chunks,
                "full_articles": full_articles,
                "hybrid_search": hybrid_search,
                "string_guarantee": string_guarantee,
                "diversify": diversify,
                "include_main_section": include_main_section,
            },
            headers=http_headers,
            accept=[(WikiSearchResponse.__content_type__, 1.0)],
        )
        return WikiSearchResponse.model_validate(response.content)
