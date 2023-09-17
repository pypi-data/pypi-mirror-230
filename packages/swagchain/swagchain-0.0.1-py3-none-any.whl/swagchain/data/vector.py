from __future__ import annotations

from typing import Any, Dict, List, Literal, TypeAlias, Union
from uuid import uuid4

from aiofauna import LazyProxy  # type: ignore
from aiohttp import ClientSession
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

Vector: TypeAlias = List[Union[int, float]]
Value: TypeAlias = Union[int, float, str, bool, List[str]]
QueryJoin: TypeAlias = Literal["$and", "$or"]
QueryWhere: TypeAlias = Literal[
    "$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin"
]
QueryKey: TypeAlias = Union[str, QueryWhere, QueryJoin]
QueryValue: TypeAlias = Union[Value, List[Value], "Query", List["Query"]]
Query: TypeAlias = Dict[QueryKey, QueryValue]
MetaData: TypeAlias = Dict[str, Value]


class QueryBuilder:
    """Query builder for Pinecone Query API with MongoDB-like syntax."""

    def __init__(self, field: str = None, query: Query = None):  # type: ignore
        self.field = field
        self.query = query if query else {}

    def __repr__(self) -> str:
        return f"{self.query}"

    def __call__(self, field_name: str) -> QueryBuilder:
        return QueryBuilder(field_name)

    def __and__(self, other: QueryBuilder) -> QueryBuilder:
        return QueryBuilder(query={"$and": [self.query, other.query]})

    def __or__(self, other: QueryBuilder) -> QueryBuilder:
        return QueryBuilder(query={"$or": [self.query, other.query]})

    def __eq__(self, value: Value) -> QueryBuilder:  # type: ignore
        return QueryBuilder(query={self.field: {"$eq": value}})

    def __ne__(self, value: Value) -> QueryBuilder:  # type: ignore
        return QueryBuilder(query={self.field: {"$ne": value}})

    def __lt__(self, value: Value) -> QueryBuilder:
        return QueryBuilder(query={self.field: {"$lt": value}})

    def __le__(self, value: Value) -> QueryBuilder:
        return QueryBuilder(query={self.field: {"$lte": value}})

    def __gt__(self, value: Value) -> QueryBuilder:
        return QueryBuilder(query={self.field: {"$gt": value}})

    def __ge__(self, value: Value) -> QueryBuilder:
        return QueryBuilder(query={self.field: {"$gte": value}})

    def in_(self, values: List[Value]) -> QueryBuilder:
        """MongoDB-like syntax for $in operator."""
        return QueryBuilder(query={self.field: {"$in": values}})

    def nin_(self, values: List[Value]) -> QueryBuilder:
        """MongoDB-like syntax for $nin operator."""
        return QueryBuilder(query={self.field: {"$nin": values}})


class UpsertRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    values: Vector = Field(...)
    metadata: MetaData = Field(...)


class Embedding(BaseModel):
    values: Vector = Field(...)
    metadata: MetaData = Field(...)


class QueryRequest(BaseModel):
    topK: int = Field(default=10)
    filter: Dict[str, Any] = Field(...)
    includeMetadata: bool = Field(default=True)
    vector: Vector = Field(...)


class QueryMatch(BaseModel):
    id: str = Field(...)
    score: float = Field(...)
    metadata: MetaData = Field(...)


class QueryResponse(BaseModel):
    matches: List[QueryMatch] = Field(...)


class UpsertResponse(BaseModel):
    upsertedCount: int = Field(...)


class VectorClient(LazyProxy[ClientSession]):
    def __init__(self, api_key: str, api_endpoint: str) -> None:  # type: ignore
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        super().__init__()

    def __load__(self) -> ClientSession:
        return ClientSession(
            headers={"api-key": self.api_key},
            base_url=self.api_endpoint,
        )

    async def upsert(self, embeddings: List[Embedding]) -> UpsertResponse:
        """
        upsert
        Upsert embeddings into the vector index.

        Args:
                                        embeddings (List[Embedding]): Embeddings to upsert.

        Returns:
                                        UpsertResponse: Upsert response.
        """
        async with self.__load__() as session:
            values: List[Vector] = []
            metadata: List[MetaData] = []
            for embedding in embeddings:
                values.append(embedding.values)
                metadata.append(embedding.metadata)

            async with session.post(
                "/vectors/upsert",
                json={
                    "vectors": [
                        UpsertRequest(values=values, metadata=metadata).dict()
                        for values, metadata in zip(values, metadata)
                    ]
                },
            ) as response:
                return UpsertResponse(**await response.json())

    async def query(
        self, expr: Query, vector: Vector, topK: int, includeMetadata: bool = True
    ) -> QueryResponse:
        """query
        Query the vector index.

        Args:
                                        expr (Query): Query expression.
                                        vector (Vector): Query vector.
                                        includeMetadata (bool, optional): Whether to include metadata in the response. Defaults to True.
                                        topK (int, optional): Number of results to return.

        Returns:
                                        QueryResponse: Query response.
        """
        async with self.__load__() as session:
            payload = QueryRequest(
                topK=topK,
                filter=expr,  # type: ignore
                vector=vector,
                includeMetadata=includeMetadata,
            ).dict()
            async with session.post(
                "/query",
                json=payload,
            ) as response:
                return QueryResponse(**await response.json())
