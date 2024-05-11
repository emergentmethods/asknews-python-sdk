from typing import List, Literal, Optional, Union
from uuid import UUID

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.news import Article, SearchResponse, SourceReportResponse


class NewsAPI(BaseAPI):
    """
    News API

    https://docs.asknews.app/en/reference#tag--news
    """

    def get_article(self, article_id: Union[str, UUID]):
        response = self.client.request(
            method="GET",
            endpoint="/v1/news/{article_id}",
            params={"article_id": article_id},
        )
        return Article.model_validate(response.content)

    def search_news(
        self,
        query: str,
        n_articles: int = 10,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        return_type: Literal["string", "dicts", "both"] = "dicts",
        historical: bool = False,
        method: Literal["nl", "kw"] = "nl",
        similarity_score_threshold: float = 0.5,
        offset: int = 0,
        categories: Optional[
            List[
                Literal[
                    "All",
                    "Business",
                    "Crime",
                    "Politics",
                    "Science",
                    "Sports",
                    "Technology",
                    "Military",
                    "Health",
                    "Entertainment",
                    "Finance",
                    "Culture",
                    "Climate",
                    "Environment",
                    "World",
                ]
            ]
        ] = None,
        doc_start_delimiter: str = "<doc>",
        doc_end_delimiter: str = "</doc>",
    ) -> SearchResponse:
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
        :param start_timestamp: Start timestamp to search from, defaults to None
        :type start_timestamp: Optional[int]
        :param end_timestamp: End timestamp to search to, defaults to None
        :type end_timestamp: Optional[int]
        :param return_type: Type of return value. 'string' means that the return is
            prompt-optimized and ready to be immediately injected into any prompt.
            'dicts' means that the return is a structured dictionary, containing
            more information such as full article content, and additional metadata
            (like a classic news api). Can be 'string' or 'dicts', or 'both', defaults
            to "dicts".
        :type return_type: Literal["string", "dicts", "both"]
        :param historical: Search on archive of historical news. Defaults to False,
            meaning that the search will only look through the most recent news
            (48 hours)
        :type historical: bool
        :param method: Method to use for searching. 'nl' means Natural Language, which
            is a string that can be any phrase, keyword, question, or paragraph that
            will be used for semantic search on the news. 'kw' means Keyword, which can
            also be any keyword(s), phrase, or paragraph, however the search is a direct
            keyword search on the database.
        :type method: Literal["nl", "kw"]
        :param similarity_score_threshold: Similarity score threshold, defaults to 0.5
        :type similarity_score_threshold: float
        :param offset: Offset for pagination
        :type offset: int
        :param categories: Categories of news to filter on, defaults to ["All"]
        :type categories: Optional[List[
            Literal[
                "All", "Business", "Crime", "Politics", "Science", "Sports",
                "Technology", "Military", "Health", "Entertainment", "Finance",
                "Culture", "Climate", "Environment", "World"
            ]
        ]]
        :param doc_start_delimiter: Document start delimiter, defaults to "<doc>"
        :type doc_start_delimiter: str
        :param doc_end_delimiter: Document end delimiter, defaults to "</doc>"
        :type doc_end_delimiter: str
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/news/search",
            query={
                "query": query,
                "n_articles": n_articles,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "return_type": return_type,
                "method": method,
                "historical": historical,
                "offset": offset,
                "categories": categories if categories is not None else ["All"],
                "similarity_score_threshold": similarity_score_threshold,
                "doc_start_delimiter": doc_start_delimiter,
                "doc_end_delimiter": doc_end_delimiter,
            },
            accept=[(SearchResponse.__content_type__, 1.0)],
        )
        return SearchResponse.model_validate(response.content)

    def get_sources_report(
        self,
        n_points: int = 100,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        metric: str = "countries_diversity",
        sampling: str = "1h",
    ) -> SourceReportResponse:
        """
        Get the sources report.

        https://docs.asknews.app/en/reference#get-/v1/sources

        :param n_points: The number of points.
        :type n_points: int
        :param start_timestamp: The start timestamp.
        :type start_timestamp: Optional[int]
        :param end_timestamp: The end timestamp.
        :type end_timestamp: Optional[int]
        :param metric: The metric.
        :type metric: str
        :param sampling: The sampling.
        :type sampling: str
        :return: The source report response.
        :rtype: SourceReportResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/sources",
            query={
                "n_points": n_points,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "metric": metric,
                "sampling": sampling,
            },
            accept=[(SourceReportResponse.__content_type__, 1.0)],
        )
        return SourceReportResponse.model_validate(response.content)


class AsyncNewsAPI(BaseAPI):
    """
    News API

    https://docs.asknews.app/en/reference#tag--news
    """

    async def get_article(self, article_id: Union[str, UUID]):
        response = await self.client.request(
            method="GET",
            endpoint="/v1/news/{article_id}",
            params={"article_id": article_id},
        )
        return Article.model_validate(response.content)

    async def search_news(
        self,
        query: str,
        n_articles: int = 10,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        return_type: Literal["string", "dicts", "both"] = "dicts",
        historical: bool = False,
        method: Literal["nl", "kw"] = "nl",
        similarity_score_threshold: float = 0.5,
        offset: int = 0,
        categories: Optional[
            List[
                Literal[
                    "All",
                    "Business",
                    "Crime",
                    "Politics",
                    "Science",
                    "Sports",
                    "Technology",
                    "Military",
                    "Health",
                    "Entertainment",
                    "Finance",
                    "Culture",
                    "Climate",
                    "Environment",
                    "World",
                ]
            ]
        ] = None,
        doc_start_delimiter: str = "<doc>",
        doc_end_delimiter: str = "</doc>",
    ) -> SearchResponse:
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
        :param start_timestamp: Start timestamp to search from, defaults to None
        :type start_timestamp: Optional[int]
        :param end_timestamp: End timestamp to search to, defaults to None
        :type end_timestamp: Optional[int]
        :param return_type: Type of return value. 'string' means that the return is
            prompt-optimized and ready to be immediately injected into any prompt.
            'dicts' means that the return is a structured dictionary, containing more
            information such as full article content, and additional metadata (like a
            classic news api). Can be 'string' or 'dicts', or 'both', defaults to
            "dicts".
        :type return_type: Literal["string", "dicts", "both"]
        :param historical: Search on archive of historical news. Defaults to False,
            meaning that the search will only look through the most recent news
            (48 hours)
        :type historical: bool
        :param method: Method to use for searching. 'nl' means Natural Language, which
            is a string that can be any phrase, keyword, question, or paragraph that
            will be used for semantic search on the news. 'kw' means Keyword, which can
            also be any keyword(s), phrase, or paragraph, however the search is a direct
            keyword search on the database.
        :type method: Literal["nl", "kw"]
        :param similarity_score_threshold: Similarity score threshold, defaults to 0.5
        :type similarity_score_threshold: float
        :param offset: Offset for pagination
        :type offset: int
        :param categories: Categories of news to filter on, defaults to ["All"]
        :type categories: Optional[List[
            Literal[
                "All", "Business", "Crime", "Politics", "Science", "Sports",
                "Technology", "Military", "Health", "Entertainment", "Finance",
                "Culture", "Climate", "Environment", "World"
            ]
        ]]
        :param doc_start_delimiter: Document start delimiter, defaults to "<doc>"
        :type doc_start_delimiter: str
        :param doc_end_delimiter: Document end delimiter, defaults to "</doc>"
        :type doc_end_delimiter: str
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/news/search",
            query={
                "query": query,
                "n_articles": n_articles,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "return_type": return_type,
                "method": method,
                "historical": historical,
                "offset": offset,
                "categories": categories if categories is not None else ["All"],
                "similarity_score_threshold": similarity_score_threshold,
                "doc_start_delimiter": doc_start_delimiter,
                "doc_end_delimiter": doc_end_delimiter,
            },
            accept=[(SearchResponse.__content_type__, 1.0)],
        )
        return SearchResponse.model_validate(response.content)

    async def get_sources_report(
        self,
        n_points: int = 100,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        metric: str = "countries_diversity",
        sampling: str = "1h",
    ) -> SourceReportResponse:
        """
        Get the sources report.

        https://docs.asknews.app/en/reference#get-/v1/sources

        :param n_points: The number of points.
        :type n_points: int
        :param start_timestamp: The start timestamp.
        :type start_timestamp: Optional[int]
        :param end_timestamp: The end timestamp.
        :type end_timestamp: Optional[int]
        :param metric: The metric.
        :type metric: str
        :param sampling: The sampling.
        :type sampling: str
        :return: The source report response.
        :rtype: SourceReportResponse
        """
        response = await self.client.request(
            endpoint="/v1/stories/sources",
            query={
                "n_points": n_points,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "metric": metric,
                "sampling": sampling,
            },
            accept=[(SourceReportResponse.__content_type__, 1.0)],
        )
        return SourceReportResponse.model_validate(response.content)
