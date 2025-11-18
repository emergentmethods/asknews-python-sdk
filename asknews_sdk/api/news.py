from datetime import datetime
from typing import Dict, List, Literal, Optional, Union
from uuid import UUID

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.client import APIClient, AsyncAPIClient
from asknews_sdk.dto.news import (
    ArticleResponse,
    GraphResponse,
    IndexCountsResponse,
    RedditResponse,
    SearchResponse,
    SourceReportResponse,
)


class NewsAPI(BaseAPI[APIClient]):
    """
    News API

    https://docs.asknews.app/en/reference#tag--news
    """

    def get_article(
        self, article_id: Union[str, UUID], *, http_headers: Optional[Dict] = None
    ) -> ArticleResponse:
        """
        Get a news article by its UUID.

        https://docs.asknews.app/en/reference#get-/v1/news/-article_id-

        :param article_id: The UUID of the article.
        :type article_id: Union[str, UUID]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The article response.
        :rtype: ArticleResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/news/{article_id}",
            params={"article_id": article_id},
            headers=http_headers,
            accept=[(ArticleResponse.__content_type__, 1.0)],
        )
        return ArticleResponse.model_validate(response.content)

    def get_articles(
        self, article_ids: Union[List[str], List[UUID]], *, http_headers: Optional[Dict] = None
    ) -> List[ArticleResponse]:
        """
        Get news articles by their UUIDs.

        https://docs.asknews.app/en/reference#get-/v1/news

        :param article_ids: The UUIDs of the articles.
        :type article_ids: Union[List[str], List[UUID]]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The articles response.
        :rtype: List[ArticleResponse]
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/news",
            query={"article_ids": article_ids},
            headers=http_headers,
            accept=[(ArticleResponse.__content_type__, 1.0)],
        )
        return [ArticleResponse.model_validate(item) for item in response.content]

    def search_news(
        self,
        query: str = "",
        n_articles: int = 10,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        time_filter: Literal["crawl_date", "pub_date"] = "crawl_date",
        return_type: Literal["string", "dicts", "both"] = "string",
        historical: bool = False,
        method: Literal["nl", "kw", "both"] = "kw",
        similarity_score_threshold: float = 0.5,
        offset: Union[int, str] = 0,
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
        provocative: Optional[str] = "all",
        reporting_voice: Optional[Union[List[str], str]] = None,
        domain_url: Optional[Union[List[str], str]] = None,
        bad_domain_url: Optional[Union[List[str], str]] = None,
        page_rank: Optional[int] = None,
        diversify_sources: Optional[bool] = False,
        strategy: Literal["latest news", "news knowledge", "default"] = "default",
        hours_back: Optional[int] = 24,
        string_guarantee: Optional[List[str]] = None,
        string_guarantee_op: Optional[str] = "OR",
        reverse_string_guarantee: Optional[List[str]] = None,
        entity_guarantee: Optional[List[str]] = None,
        entity_guarantee_op: Optional[str] = "OR",
        return_graphs: Optional[bool] = False,
        return_geo: Optional[bool] = False,
        countries: Optional[List[str]] = None,
        countries_blacklist: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        continents: Optional[List[str]] = None,
        sentiment: Optional[Literal["negative", "neutral", "positive"]] = None,
        premium: Optional[bool] = False,
        authors: Optional[List[str]] = None,
        *,
        http_headers: Optional[Dict] = None,
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
        :param method: Method to use for searching. Both `kw` and `nl`
            support natural language queries. `kw` tries to match keywords,
            while `nl` tries to match the meaning of the query.
        :type method: Literal["nl", "kw", "both"]
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
        :param provocative: Provocative, defaults to "all"
        :type provocative: Optional[str]
        :param reporting_voice: Reporting voice, defaults to "all"
        :type reporting_voice: Optional[str]
        :param domain_url: Domain URL, defaults to None
        :type domain_url: Optional[str]
        :param page_rank: Page rank, defaults to None
        :type page_rank: Optional[int]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The search response.
        :rtype: SearchResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/news/search",
            query={
                "query": query,
                "n_articles": n_articles,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "time_filter": time_filter,
                "return_type": return_type,
                "method": method,
                "historical": historical,
                "offset": offset,
                "categories": categories if categories is not None else ["All"],
                "similarity_score_threshold": similarity_score_threshold,
                "doc_start_delimiter": doc_start_delimiter,
                "doc_end_delimiter": doc_end_delimiter,
                "provocative": provocative,
                "reporting_voice": reporting_voice,
                "domain_url": domain_url,
                "bad_domain_url": bad_domain_url,
                "page_rank": page_rank,
                "diversify_sources": diversify_sources,
                "strategy": strategy,
                "hours_back": hours_back,
                "string_guarantee": string_guarantee,
                "string_guarantee_op": string_guarantee_op,
                "reverse_string_guarantee": reverse_string_guarantee,
                "entity_guarantee": entity_guarantee,
                "entity_guarantee_op": entity_guarantee_op,
                "return_graphs": return_graphs,
                "return_geo": return_geo,
                "countries": countries,
                "countries_blacklist": countries_blacklist,
                "languages": languages,
                "continents": continents,
                "sentiment": sentiment,
                "premium": premium,
                "authors": authors,
            },
            headers=http_headers,
            accept=[(SearchResponse.__content_type__, 1.0)],
        )
        return SearchResponse.model_validate(response.content)

    def get_index_counts(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        sampling: Literal["5m", "1h", "12h", "1d", "1w", "1m"] = "1d",
        time_filter: Literal["crawl_date", "pub_date"] = "pub_date",
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
        provocative: Optional[str] = "all",
        reporting_voice: Optional[Union[List[str], str]] = None,
        domains: Optional[Union[List[str], str]] = None,
        bad_domain_url: Optional[Union[List[str], str]] = None,
        page_rank: Optional[int] = None,
        string_guarantee: Optional[List[str]] = None,
        string_guarantee_op: Optional[str] = "OR",
        reverse_string_guarantee: Optional[List[str]] = None,
        entity_guarantee: Optional[List[str]] = None,
        entity_guarantee_op: Optional[str] = "OR",
        countries: Optional[List[str]] = None,
        countries_blacklist: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        continents: Optional[List[str]] = None,
        sentiment: Optional[Literal["negative", "neutral", "positive"]] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> IndexCountsResponse:
        """
        Get index counts over time.

        https://docs.asknews.app/en/reference#get-/v1/index_counts

        :param start_datetime: The start datetime.
        :type start_datetime: datetime
        :param end_datetime: The end datetime.
        :type end_datetime: datetime
        :param time_filter: The time filter.
        :type time_filter: Literal["crawl_date", "pub_date"]
        :param categories: The categories.
        :type categories: Optional[List[
            Literal[
                "All", "Business", "Crime", "Politics", "Science", "Sports",
                "Technology", "Military", "Health", "Entertainment", "Finance",
                "Culture", "Climate", "Environment", "World"
            ]
        ]]
        :param sampling: The sampling.
        :type sampling: Literal["5m", "1h", "12h", "1d", "1w", "1m"]
        :param provocative: The provocative filter.
        :type provocative: Optional[str]
        :param reporting_voice: The reporting voice filter.
        :type reporting_voice: Optional[Union[List[str], str]]
        :param domains: The domains filter.
        :type domains: Optional[Union[List[str], str]]
        :param bad_domain_url: The bad domain URL filter.
        :type bad_domain_url: Optional[Union[List[str], str]]
        :param page_rank: The page rank filter.
        :type page_rank: Optional[int]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The index counts response.
        :rtype: IndexCountsResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/index_counts",
            query={
                "start_datetime": start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_datetime": end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                "time_filter": time_filter,
                "categories": categories,
                "provocative": provocative,
                "reporting_voice": reporting_voice,
                "sampling": sampling,
                "domains": domains,
                "bad_domain_url": bad_domain_url,
                "page_rank": page_rank,
                "string_guarantee": string_guarantee,
                "string_guarantee_op": string_guarantee_op,
                "reverse_string_guarantee": reverse_string_guarantee,
                "entity_guarantee": entity_guarantee,
                "entity_guarantee_op": entity_guarantee_op,
                "countries": countries,
                "countries_blacklist": countries_blacklist,
                "languages": languages,
                "continents": continents,
                "sentiment": sentiment,
                "premium": True,
            },
            headers=http_headers,
            accept=[(IndexCountsResponse.__content_type__, 1.0)],
        )
        return IndexCountsResponse.model_validate(response.content)

    def get_sources_report(
        self,
        n_points: int = 100,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        metric: str = "countries_diversity",
        sampling: str = "1h",
        *,
        http_headers: Optional[Dict] = None,
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
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
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
            headers=http_headers,
            accept=[(SourceReportResponse.__content_type__, 1.0)],
        )
        return SourceReportResponse.model_validate(response.content)

    def search_reddit(
        self,
        keywords: List[str],
        n_threads: int = 5,
        method: Literal["nl", "kw"] = "kw",
        deep: bool = True,
        return_type: Literal["dicts", "string", "both"] = "string",
        time_filter: Literal["all", "day", "hour", "month", "week", "year"] = "all",
        sort: Literal["relevance", "hot", "top", "new", "comments"] = "relevance",
        *,
        http_headers: Optional[Dict] = None,
    ) -> RedditResponse:
        """
        Search Reddit, summarize and analyze the threads,
        Return the list of threads and analyses.
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/reddit/search",
            query={
                "keywords": keywords,
                "n_threads": n_threads,
                "method": method,
                "deep": deep,
                "return_type": return_type,
                "time_filter": time_filter,
                "sort": sort,
            },
            headers=http_headers,
            accept=[(RedditResponse.__content_type__, 1.0)],
        )
        return RedditResponse.model_validate(response.content)

    def build_graph(
        self,
        query: str = "",
        return_articles: bool = False,
        min_cluster_probability: float = 0.9,
        geo_disambiguation: bool = False,
        filter_params: Optional[Dict] = None,
        constrained_disambiguations: Optional[List[Dict]] = None,
        docs_upload: Optional[List[Dict]] = None,
        visualize_with: Optional[str] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> GraphResponse:
        response = self.client.request(
            method="POST",
            endpoint="/v1/news/graph",
            body={
                "query": query,
                "return_articles": return_articles,
                "min_cluster_probability": min_cluster_probability,
                "geo_disambiguation": geo_disambiguation,
                "filter_params": filter_params,
                "constrained_disambiguations": constrained_disambiguations,
                "docs_upload": docs_upload,
                "visualize_with": visualize_with,
            },
            headers=http_headers,
            accept=[(GraphResponse.__content_type__, 1.0)],
        )
        return GraphResponse.model_validate(response.content)


class AsyncNewsAPI(BaseAPI[AsyncAPIClient]):
    """
    News API

    https://docs.asknews.app/en/reference#tag--news
    """

    async def get_article(
        self, article_id: Union[str, UUID], *, http_headers: Optional[Dict] = None
    ):
        """
        Get a news article by its UUID.

        https://docs.asknews.app/en/reference#get-/v1/news/-article_id-

        :param article_id: The UUID of the article.
        :type article_id: Union[str, UUID]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The article response.
        :rtype: ArticleResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/news/{article_id}",
            params={"article_id": article_id},
            headers=http_headers,
            accept=[(ArticleResponse.__content_type__, 1.0)],
        )
        return ArticleResponse.model_validate(response.content)

    async def get_articles(
        self, article_ids: Union[List[str], List[UUID]], *, http_headers: Optional[Dict] = None
    ) -> List[ArticleResponse]:
        """
        Get news articles by their UUIDs.

        https://docs.asknews.app/en/reference#get-/v1/news

        :param article_ids: The UUIDs of the articles.
        :type article_ids: Union[List[str], List[UUID]]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The articles response.
        :rtype: List[ArticleResponse]
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/news",
            query={"article_ids": article_ids},
            headers=http_headers,
            accept=[(ArticleResponse.__content_type__, 1.0)],
        )
        return [ArticleResponse.model_validate(item) for item in response.content]

    async def search_news(
        self,
        query: str = "",
        n_articles: int = 10,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        time_filter: Literal["crawl_date", "pub_date"] = "crawl_date",
        return_type: Literal["string", "dicts", "both"] = "string",
        historical: bool = False,
        method: Literal["nl", "kw", "both"] = "kw",
        similarity_score_threshold: float = 0.5,
        offset: Union[int, str] = 0,
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
        provocative: Optional[str] = "all",
        reporting_voice: Optional[Union[List[str], str]] = None,
        domain_url: Optional[Union[List[str], str]] = None,
        bad_domain_url: Optional[Union[List[str], str]] = None,
        page_rank: Optional[int] = None,
        diversify_sources: Optional[bool] = False,
        strategy: Literal["latest news", "news knowledge", "default"] = "default",
        hours_back: Optional[int] = 24,
        string_guarantee: Optional[List[str]] = None,
        string_guarantee_op: Optional[str] = "OR",
        reverse_string_guarantee: Optional[List[str]] = None,
        entity_guarantee: Optional[List[str]] = None,
        entity_guarantee_op: Optional[str] = "OR",
        return_graphs: Optional[bool] = False,
        return_geo: Optional[bool] = False,
        countries: Optional[List[str]] = None,
        countries_blacklist: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        continents: Optional[List[str]] = None,
        sentiment: Optional[Literal["negative", "neutral", "positive"]] = None,
        premium: Optional[bool] = False,
        authors: Optional[List[str]] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> SearchResponse:
        """
        Get time-series counts for a filter

        https://docs.asknews.app/en/reference#get-/v1/index_counts
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/news/search",
            query={
                "query": query,
                "n_articles": n_articles,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "time_filter": time_filter,
                "return_type": return_type,
                "method": method,
                "historical": historical,
                "offset": offset,
                "categories": categories if categories is not None else ["All"],
                "similarity_score_threshold": similarity_score_threshold,
                "doc_start_delimiter": doc_start_delimiter,
                "doc_end_delimiter": doc_end_delimiter,
                "provocative": provocative,
                "reporting_voice": reporting_voice,
                "domain_url": domain_url,
                "bad_domain_url": bad_domain_url,
                "page_rank": page_rank,
                "diversify_sources": diversify_sources,
                "strategy": strategy,
                "hours_back": hours_back,
                "string_guarantee": string_guarantee,
                "string_guarantee_op": string_guarantee_op,
                "reverse_string_guarantee": reverse_string_guarantee,
                "entity_guarantee": entity_guarantee,
                "entity_guarantee_op": entity_guarantee_op,
                "return_graphs": return_graphs,
                "return_geo": return_geo,
                "countries": countries,
                "countries_blacklist": countries_blacklist,
                "languages": languages,
                "continents": continents,
                "sentiment": sentiment,
                "premium": premium,
                "authors": authors,
            },
            headers=http_headers,
            accept=[(SearchResponse.__content_type__, 1.0)],
        )
        return SearchResponse.model_validate(response.content)

    async def get_index_counts(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        time_filter: Literal["crawl_date", "pub_date"] = "pub_date",
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
        sampling: Literal["5m", "1h", "12h", "1d", "1w", "1m"] = "1d",
        provocative: Optional[str] = "all",
        reporting_voice: Optional[Union[List[str], str]] = None,
        domains: Optional[Union[List[str], str]] = None,
        bad_domain_url: Optional[Union[List[str], str]] = None,
        page_rank: Optional[int] = None,
        string_guarantee: Optional[List[str]] = None,
        string_guarantee_op: Optional[str] = "OR",
        reverse_string_guarantee: Optional[List[str]] = None,
        entity_guarantee: Optional[List[str]] = None,
        entity_guarantee_op: Optional[str] = "OR",
        countries: Optional[List[str]] = None,
        countries_blacklist: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        continents: Optional[List[str]] = None,
        sentiment: Optional[Literal["negative", "neutral", "positive"]] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> IndexCountsResponse:
        """
        Get index counts over time.

        https://docs.asknews.app/en/reference#get-/v1/index_counts

        :param start_datetime: The start datetime.
        :type start_datetime: datetime
        :param end_datetime: The end datetime.
        :type end_datetime: datetime
        :param time_filter: The time filter.
        :type time_filter: Literal["crawl_date", "pub_date"]
        :param categories: The categories.
        :type categories: Optional[List[
            Literal[
                "All", "Business", "Crime", "Politics", "Science", "Sports",
                "Technology", "Military", "Health", "Entertainment", "Finance",
                "Culture", "Climate", "Environment", "World"
            ]
        ]]
        :param sampling: The sampling.
        :type sampling: Literal["5m", "1h", "12h", "1d", "1w", "1m"]
        :param provocative: The provocative filter.
        :type provocative: Optional[str]
        :param reporting_voice: The reporting voice filter.
        :type reporting_voice: Optional[Union[List[str], str]]
        :param domains: The domains filter.
        :type domains: Optional[Union[List[str], str]]
        :param bad_domain_url: The bad domain URL filter.
        :type bad_domain_url: Optional[Union[List[str], str]]
        :param page_rank: The page rank filter.
        :type page_rank: Optional[int]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The index counts response.
        :rtype: IndexCountsResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/index_counts",
            query={
                "start_datetime": start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_datetime": end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                "sampling": sampling,
                "time_filter": time_filter,
                "categories": categories,
                "provocative": provocative,
                "reporting_voice": reporting_voice,
                "domains": domains,
                "bad_domain_url": bad_domain_url,
                "page_rank": page_rank,
                "string_guarantee": string_guarantee,
                "string_guarantee_op": string_guarantee_op,
                "reverse_string_guarantee": reverse_string_guarantee,
                "entity_guarantee": entity_guarantee,
                "entity_guarantee_op": entity_guarantee_op,
                "countries": countries,
                "countries_blacklist": countries_blacklist,
                "languages": languages,
                "continents": continents,
                "sentiment": sentiment,
                "premium": True,
            },
            headers=http_headers,
            accept=[(IndexCountsResponse.__content_type__, 1.0)],
        )
        return IndexCountsResponse.model_validate(response.content)

    async def get_sources_report(
        self,
        n_points: int = 100,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        metric: str = "countries_diversity",
        sampling: str = "1h",
        *,
        http_headers: Optional[Dict] = None,
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
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The source report response.
        :rtype: SourceReportResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/sources",
            query={
                "n_points": n_points,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "metric": metric,
                "sampling": sampling,
            },
            headers=http_headers,
            accept=[(SourceReportResponse.__content_type__, 1.0)],
        )
        return SourceReportResponse.model_validate(response.content)

    async def search_reddit(
        self,
        keywords: List[str],
        n_threads: int = 5,
        method: Literal["nl", "kw"] = "kw",
        deep: bool = True,
        return_type: Literal["dicts", "string", "both"] = "string",
        time_filter: Literal["all", "day", "hour", "month", "week", "year"] = "all",
        sort: Literal["relevance", "hot", "top", "new", "comments"] = "relevance",
        *,
        http_headers: Optional[Dict] = None,
    ) -> RedditResponse:
        """
        Search Reddit, summarize and analyze the threads,
        Return the list of threads and analyses.
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/reddit/search",
            query={
                "keywords": keywords,
                "n_threads": n_threads,
                "method": method,
                "deep": deep,
                "return_type": return_type,
                "time_filter": time_filter,
                "sort": sort,
            },
            headers=http_headers,
            accept=[(RedditResponse.__content_type__, 1.0)],
        )
        return RedditResponse.model_validate(response.content)

    async def build_graph(
        self,
        query: str = "",
        return_articles: bool = False,
        min_cluster_probability: float = 0.9,
        geo_disambiguation: bool = False,
        filter_params: Optional[Dict] = None,
        constrained_disambiguations: Optional[List[Dict]] = None,
        docs_upload: Optional[List[Dict]] = None,
        visualize_with: Optional[str] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> GraphResponse:
        response = await self.client.request(
            method="POST",
            endpoint="/v1/news/graph",
            body={
                "query": query,
                "return_articles": return_articles,
                "min_cluster_probability": min_cluster_probability,
                "geo_disambiguation": geo_disambiguation,
                "filter_params": filter_params,
                "constrained_disambiguations": constrained_disambiguations,
                "docs_upload": docs_upload,
                "visualize_with": visualize_with,
            },
            headers=http_headers,
            accept=[(GraphResponse.__content_type__, 1.0)],
        )
        return GraphResponse.model_validate(response.content)
