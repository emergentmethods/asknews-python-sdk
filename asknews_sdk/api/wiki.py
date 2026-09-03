from typing import Dict, List, Optional
from urllib.parse import quote

from asknews_sdk.api.base import BaseAPI
from asknews_sdk.dto.wiki import (
    WikiBatchEntityRequest,
    WikiBatchEntityResponse,
    WikiBatchLinkEntityRequest,
    WikiBatchLinkEntityResponse,
    WikiBatchSearchResponse,
    WikiEntityResponse,
    WikiLinkEntityResponse,
    WikiSearchResponse,
)


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
        string_guarantee: Optional[List[str]] = None,
        include_main_section: bool = False,
        has_wikidata: Optional[bool] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiSearchResponse:
        """
        Search for wiki articles given a query.

        https://docs.asknews.app/en/reference#get-/v1/wiki/search

        :param query: Query string that can be any phrase, keyword, question, or
            paragraph.
        :type query: str
        :param n_documents: Number of documents to return.
        :type n_documents: int
        :param neighbor_chunks: Number of neighbor chunks to attach and return.
        :type neighbor_chunks: int
        :param full_articles: If true, full articles will be returned.
        :type full_articles: bool
        :param hybrid_search: If true, hybrid search will be used.
        :type hybrid_search: bool
        :param diversify: Diversity factor for MMR re-ranking (0.0-1.0).
        :type diversify: float
        :param string_guarantee: List of strings that must be present in the results.
        :type string_guarantee: Optional[List[str]]
        :param include_main_section: If true, the main section of the article is
            prepended to each chunk.
        :type include_main_section: bool
        :param has_wikidata: Filter results by whether the article has Wikidata.
            If None, no filtering is applied.
        :type has_wikidata: Optional[bool]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The search response.
        :rtype: WikiSearchResponse
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
                "has_wikidata": has_wikidata,
            },
            headers=http_headers,
            accept=[(WikiSearchResponse.__content_type__, 1.0)],
        )
        return WikiSearchResponse.model_validate(response.content)

    def search_wiki_batch(
        self,
        queries: List[str],
        n_documents: int = 5,
        neighbor_chunks: int = 1,
        full_articles: bool = False,
        hybrid_search: bool = False,
        diversify: float = 0.0,
        string_guarantee: Optional[List[str]] = None,
        include_main_section: bool = False,
        has_wikidata: Optional[bool] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiBatchSearchResponse:
        """
        Search for wiki articles for multiple queries in a single batch.

        https://docs.asknews.app/en/reference#post-/v1/wiki/search/batch

        :param queries: List of query strings to search for in parallel.
        :type queries: List[str]
        :param n_documents: Number of documents to return per query.
        :type n_documents: int
        :param neighbor_chunks: Number of neighbor chunks to attach and return.
        :type neighbor_chunks: int
        :param full_articles: If true, full articles will be returned.
        :type full_articles: bool
        :param hybrid_search: If true, hybrid search will be used.
        :type hybrid_search: bool
        :param diversify: Diversity factor for MMR re-ranking (0.0-1.0).
        :type diversify: float
        :param string_guarantee: List of strings that must be present in the results.
        :type string_guarantee: Optional[List[str]]
        :param include_main_section: If true, the main section of the article is
            prepended to each chunk.
        :type include_main_section: bool
        :param has_wikidata: Filter results by whether the article has Wikidata.
            If None, no filtering is applied.
        :type has_wikidata: Optional[bool]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The batch search response.
        :rtype: WikiBatchSearchResponse
        """
        response = self.client.request(
            method="POST",
            endpoint="/v1/wiki/search/batch",
            query={
                "queries": queries,
                "n_documents": n_documents,
                "neighbor_chunks": neighbor_chunks,
                "full_articles": full_articles,
                "hybrid_search": hybrid_search,
                "string_guarantee": string_guarantee,
                "diversify": diversify,
                "include_main_section": include_main_section,
                "has_wikidata": has_wikidata,
            },
            headers=http_headers,
            accept=[(WikiBatchSearchResponse.__content_type__, 1.0)],
        )
        return WikiBatchSearchResponse.model_validate(response.content)

    def link_entity(
        self,
        entity: str,
        entity_type: Optional[str] = None,
        entity_description: Optional[str] = None,
        n_candidates: int = 5,
        relevance_threshold: float = 0.40,
        ambiguity_margin: float = 0.05,
        allow_ambiguous: bool = True,
        include_candidates: bool = True,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiLinkEntityResponse:
        """
        Link an entity name to its Wikidata entity.

        https://docs.asknews.app/en/reference#get-/v1/wiki/link-entity

        :param entity: Name of the entity to link.
        :type entity: str
        :param entity_type: Optional type of the entity (e.g. 'person', 'location',
            'organization').
        :type entity_type: Optional[str]
        :param entity_description: Optional description providing additional context
            to improve entity matching.
        :type entity_description: Optional[str]
        :param n_candidates: Number of candidate entities to return alongside the
            linked entity. Does not affect which entity is linked.
        :type n_candidates: int
        :param relevance_threshold: Accept/abstain gate: minimum relevance (0-1) the
            linked entity must have.
        :type relevance_threshold: float
        :param ambiguity_margin: A different entity with the same name scoring within
            this relative margin (0-1) of the winner marks the result 'ambiguous'.
        :type ambiguity_margin: float
        :param allow_ambiguous: If true, 'ambiguous' links still return their
            entity; if false, only confident 'linked' matches are accepted.
        :type allow_ambiguous: bool
        :param include_candidates: If true, include the candidate list alongside the
            linked entity.
        :type include_candidates: bool
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The entity link response.
        :rtype: WikiLinkEntityResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/wiki/link-entity",
            query={
                "entity": entity,
                "entity_type": entity_type,
                "entity_description": entity_description,
                "n_candidates": n_candidates,
                "relevance_threshold": relevance_threshold,
                "ambiguity_margin": ambiguity_margin,
                "allow_ambiguous": allow_ambiguous,
                "include_candidates": include_candidates,
            },
            headers=http_headers,
            accept=[(WikiLinkEntityResponse.__content_type__, 1.0)],
        )
        return WikiLinkEntityResponse.model_validate(response.content)

    def link_entity_batch(
        self,
        entities: List[str],
        entity_types: Optional[List[Optional[str]]] = None,
        entity_descriptions: Optional[List[Optional[str]]] = None,
        relevance_threshold: Optional[float] = None,
        ambiguity_margin: Optional[float] = None,
        allow_ambiguous: bool = True,
        include_candidates: bool = True,
        n_candidates: int = 5,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiBatchLinkEntityResponse:
        """
        Link multiple entity names to their Wikidata entities in parallel.

        https://docs.asknews.app/en/reference#post-/v1/wiki/link-entity/batch

        :param entities: List of entity names to link.
        :type entities: List[str]
        :param entity_types: Optional types of the entities. Must be the same length
            as entities if provided; individual elements may be None.
        :type entity_types: Optional[List[Optional[str]]]
        :param entity_descriptions: Optional descriptions for the entities. Must be the
            same length as entities if provided; individual elements may be None.
        :type entity_descriptions: Optional[List[Optional[str]]]
        :param relevance_threshold: Accept/abstain gate: minimum relevance (0-1) the
            linked entity must have.
        :type relevance_threshold: Optional[float]
        :param ambiguity_margin: A different entity with the same name scoring within
            this relative margin (0-1) of the winner marks the result 'ambiguous'.
        :type ambiguity_margin: Optional[float]
        :param allow_ambiguous: If true, 'ambiguous' links still return their
            entity; if false, only confident 'linked' matches are accepted.
        :type allow_ambiguous: bool
        :param include_candidates: If true, include the candidate list alongside the
            linked entity.
        :type include_candidates: bool
        :param n_candidates: Number of candidate entities to return per entity alongside
            the linked entity. Does not affect which entity is linked.
        :type n_candidates: int
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The batch entity link response.
        :rtype: WikiBatchLinkEntityResponse
        """
        body = WikiBatchLinkEntityRequest(
            entities=entities,
            entity_types=entity_types,
            entity_descriptions=entity_descriptions,
            relevance_threshold=relevance_threshold,
            ambiguity_margin=ambiguity_margin,
            allow_ambiguous=allow_ambiguous,
            include_candidates=include_candidates,
        )
        response = self.client.request(
            method="POST",
            endpoint="/v1/wiki/link-entity/batch",
            body=body.model_dump(mode="json"),
            query={"n_candidates": n_candidates},
            headers=http_headers,
            accept=[(WikiBatchLinkEntityResponse.__content_type__, 1.0)],
        )
        return WikiBatchLinkEntityResponse.model_validate(response.content)

    def get_entity(
        self,
        qid: str,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiEntityResponse:
        """
        Retrieve a Wikidata entity by its QID.

        https://docs.asknews.app/en/reference#get-/v1/wiki/entity/-qid-

        :param qid: Wikidata QID of the entity to retrieve, e.g. 'Q312'.
        :type qid: str
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The entity response. A QID that is not in the collection comes back
            with found=False rather than raising.
        :rtype: WikiEntityResponse
        """
        response = self.client.request(
            method="GET",
            endpoint="/v1/wiki/entity/{qid}",
            # Escaped: QIDs are free-form input and a raw "/" would otherwise be
            # normalized away into a different endpoint.
            params={"qid": quote(qid, safe="")},
            headers=http_headers,
            accept=[(WikiEntityResponse.__content_type__, 1.0)],
        )
        return WikiEntityResponse.model_validate(response.content)

    def get_entity_batch(
        self,
        qids: List[str],
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiBatchEntityResponse:
        """
        Retrieve multiple Wikidata entities by QID in a single request.

        https://docs.asknews.app/en/reference#post-/v1/wiki/entity/batch

        :param qids: Wikidata QIDs to retrieve.
        :type qids: List[str]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The batch entity response. Results are in the order the QIDs were
            supplied; a QID that is not in the collection comes back with found=False
            rather than being omitted.
        :rtype: WikiBatchEntityResponse
        """
        body = WikiBatchEntityRequest(qids=qids)
        response = self.client.request(
            method="POST",
            endpoint="/v1/wiki/entity/batch",
            body=body.model_dump(mode="json"),
            headers=http_headers,
            accept=[(WikiBatchEntityResponse.__content_type__, 1.0)],
        )
        return WikiBatchEntityResponse.model_validate(response.content)


class AsyncWikiAPI(BaseAPI):
    """
    Wiki API

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
        string_guarantee: Optional[List[str]] = None,
        include_main_section: bool = False,
        has_wikidata: Optional[bool] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiSearchResponse:
        """
        Search for wiki articles given a query.

        https://docs.asknews.app/en/reference#get-/v1/wiki/search

        :param query: Query string that can be any phrase, keyword, question, or
            paragraph.
        :type query: str
        :param n_documents: Number of documents to return.
        :type n_documents: int
        :param neighbor_chunks: Number of neighbor chunks to attach and return.
        :type neighbor_chunks: int
        :param full_articles: If true, full articles will be returned.
        :type full_articles: bool
        :param hybrid_search: If true, hybrid search will be used.
        :type hybrid_search: bool
        :param diversify: Diversity factor for MMR re-ranking (0.0-1.0).
        :type diversify: float
        :param string_guarantee: List of strings that must be present in the results.
        :type string_guarantee: Optional[List[str]]
        :param include_main_section: If true, the main section of the article is
            prepended to each chunk.
        :type include_main_section: bool
        :param has_wikidata: Filter results by whether the article has Wikidata.
            If None, no filtering is applied.
        :type has_wikidata: Optional[bool]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The search response.
        :rtype: WikiSearchResponse
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
                "has_wikidata": has_wikidata,
            },
            headers=http_headers,
            accept=[(WikiSearchResponse.__content_type__, 1.0)],
        )
        return WikiSearchResponse.model_validate(response.content)

    async def search_wiki_batch(
        self,
        queries: List[str],
        n_documents: int = 5,
        neighbor_chunks: int = 1,
        full_articles: bool = False,
        hybrid_search: bool = False,
        diversify: float = 0.0,
        string_guarantee: Optional[List[str]] = None,
        include_main_section: bool = False,
        has_wikidata: Optional[bool] = None,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiBatchSearchResponse:
        """
        Search for wiki articles for multiple queries in a single batch.

        https://docs.asknews.app/en/reference#post-/v1/wiki/search/batch

        :param queries: List of query strings to search for in parallel.
        :type queries: List[str]
        :param n_documents: Number of documents to return per query.
        :type n_documents: int
        :param neighbor_chunks: Number of neighbor chunks to attach and return.
        :type neighbor_chunks: int
        :param full_articles: If true, full articles will be returned.
        :type full_articles: bool
        :param hybrid_search: If true, hybrid search will be used.
        :type hybrid_search: bool
        :param diversify: Diversity factor for MMR re-ranking (0.0-1.0).
        :type diversify: float
        :param string_guarantee: List of strings that must be present in the results.
        :type string_guarantee: Optional[List[str]]
        :param include_main_section: If true, the main section of the article is
            prepended to each chunk.
        :type include_main_section: bool
        :param has_wikidata: Filter results by whether the article has Wikidata.
            If None, no filtering is applied.
        :type has_wikidata: Optional[bool]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The batch search response.
        :rtype: WikiBatchSearchResponse
        """
        response = await self.client.request(
            method="POST",
            endpoint="/v1/wiki/search/batch",
            query={
                "queries": queries,
                "n_documents": n_documents,
                "neighbor_chunks": neighbor_chunks,
                "full_articles": full_articles,
                "hybrid_search": hybrid_search,
                "string_guarantee": string_guarantee,
                "diversify": diversify,
                "include_main_section": include_main_section,
                "has_wikidata": has_wikidata,
            },
            headers=http_headers,
            accept=[(WikiBatchSearchResponse.__content_type__, 1.0)],
        )
        return WikiBatchSearchResponse.model_validate(response.content)

    async def link_entity(
        self,
        entity: str,
        entity_type: Optional[str] = None,
        entity_description: Optional[str] = None,
        n_candidates: int = 5,
        relevance_threshold: float = 0.40,
        ambiguity_margin: float = 0.05,
        allow_ambiguous: bool = True,
        include_candidates: bool = True,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiLinkEntityResponse:
        """
        Link an entity name to its Wikidata entity.

        https://docs.asknews.app/en/reference#get-/v1/wiki/link-entity

        :param entity: Name of the entity to link.
        :type entity: str
        :param entity_type: Optional type of the entity (e.g. 'person', 'location',
            'organization').
        :type entity_type: Optional[str]
        :param entity_description: Optional description providing additional context
            to improve entity matching.
        :type entity_description: Optional[str]
        :param n_candidates: Number of candidate entities to return alongside the
            linked entity. Does not affect which entity is linked.
        :type n_candidates: int
        :param relevance_threshold: Accept/abstain gate: minimum relevance (0-1) the
            linked entity must have.
        :type relevance_threshold: float
        :param ambiguity_margin: A different entity with the same name scoring within
            this relative margin (0-1) of the winner marks the result 'ambiguous'.
        :type ambiguity_margin: float
        :param allow_ambiguous: If true, 'ambiguous' links still return their
            entity; if false, only confident 'linked' matches are accepted.
        :type allow_ambiguous: bool
        :param include_candidates: If true, include the candidate list alongside the
            linked entity.
        :type include_candidates: bool
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The entity link response.
        :rtype: WikiLinkEntityResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/wiki/link-entity",
            query={
                "entity": entity,
                "entity_type": entity_type,
                "entity_description": entity_description,
                "n_candidates": n_candidates,
                "relevance_threshold": relevance_threshold,
                "ambiguity_margin": ambiguity_margin,
                "allow_ambiguous": allow_ambiguous,
                "include_candidates": include_candidates,
            },
            headers=http_headers,
            accept=[(WikiLinkEntityResponse.__content_type__, 1.0)],
        )
        return WikiLinkEntityResponse.model_validate(response.content)

    async def link_entity_batch(
        self,
        entities: List[str],
        entity_types: Optional[List[Optional[str]]] = None,
        entity_descriptions: Optional[List[Optional[str]]] = None,
        relevance_threshold: Optional[float] = None,
        ambiguity_margin: Optional[float] = None,
        allow_ambiguous: bool = True,
        include_candidates: bool = True,
        n_candidates: int = 5,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiBatchLinkEntityResponse:
        """
        Link multiple entity names to their Wikidata entities in parallel.

        https://docs.asknews.app/en/reference#post-/v1/wiki/link-entity/batch

        :param entities: List of entity names to link.
        :type entities: List[str]
        :param entity_types: Optional types of the entities. Must be the same length
            as entities if provided; individual elements may be None.
        :type entity_types: Optional[List[Optional[str]]]
        :param entity_descriptions: Optional descriptions for the entities. Must be the
            same length as entities if provided; individual elements may be None.
        :type entity_descriptions: Optional[List[Optional[str]]]
        :param relevance_threshold: Accept/abstain gate: minimum relevance (0-1) the
            linked entity must have.
        :type relevance_threshold: Optional[float]
        :param ambiguity_margin: A different entity with the same name scoring within
            this relative margin (0-1) of the winner marks the result 'ambiguous'.
        :type ambiguity_margin: Optional[float]
        :param allow_ambiguous: If true, 'ambiguous' links still return their
            entity; if false, only confident 'linked' matches are accepted.
        :type allow_ambiguous: bool
        :param include_candidates: If true, include the candidate list alongside the
            linked entity.
        :type include_candidates: bool
        :param n_candidates: Number of candidate entities to return per entity alongside
            the linked entity. Does not affect which entity is linked.
        :type n_candidates: int
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The batch entity link response.
        :rtype: WikiBatchLinkEntityResponse
        """
        body = WikiBatchLinkEntityRequest(
            entities=entities,
            entity_types=entity_types,
            entity_descriptions=entity_descriptions,
            relevance_threshold=relevance_threshold,
            ambiguity_margin=ambiguity_margin,
            allow_ambiguous=allow_ambiguous,
            include_candidates=include_candidates,
        )
        response = await self.client.request(
            method="POST",
            endpoint="/v1/wiki/link-entity/batch",
            body=body.model_dump(mode="json"),
            query={"n_candidates": n_candidates},
            headers=http_headers,
            accept=[(WikiBatchLinkEntityResponse.__content_type__, 1.0)],
        )
        return WikiBatchLinkEntityResponse.model_validate(response.content)

    async def get_entity(
        self,
        qid: str,
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiEntityResponse:
        """
        Retrieve a Wikidata entity by its QID.

        https://docs.asknews.app/en/reference#get-/v1/wiki/entity/-qid-

        :param qid: Wikidata QID of the entity to retrieve, e.g. 'Q312'.
        :type qid: str
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The entity response. A QID that is not in the collection comes back
            with found=False rather than raising.
        :rtype: WikiEntityResponse
        """
        response = await self.client.request(
            method="GET",
            endpoint="/v1/wiki/entity/{qid}",
            # Escaped: QIDs are free-form input and a raw "/" would otherwise be
            # normalized away into a different endpoint.
            params={"qid": quote(qid, safe="")},
            headers=http_headers,
            accept=[(WikiEntityResponse.__content_type__, 1.0)],
        )
        return WikiEntityResponse.model_validate(response.content)

    async def get_entity_batch(
        self,
        qids: List[str],
        *,
        http_headers: Optional[Dict] = None,
    ) -> WikiBatchEntityResponse:
        """
        Retrieve multiple Wikidata entities by QID in a single request.

        https://docs.asknews.app/en/reference#post-/v1/wiki/entity/batch

        :param qids: Wikidata QIDs to retrieve.
        :type qids: List[str]
        :param http_headers: Additional HTTP headers.
        :type http_headers: Optional[Dict]
        :return: The batch entity response. Results are in the order the QIDs were
            supplied; a QID that is not in the collection comes back with found=False
            rather than being omitted.
        :rtype: WikiBatchEntityResponse
        """
        body = WikiBatchEntityRequest(qids=qids)
        response = await self.client.request(
            method="POST",
            endpoint="/v1/wiki/entity/batch",
            body=body.model_dump(mode="json"),
            headers=http_headers,
            accept=[(WikiBatchEntityResponse.__content_type__, 1.0)],
        )
        return WikiBatchEntityResponse.model_validate(response.content)
