from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Callable, Union
from enum import Enum


class Source(str, Enum):
    email = "email"
    file = "file"
    chat = "chat"


class DocumentMetadata(BaseModel):
    source: Optional[Source] = None
    source_id: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[str] = None
    author: Optional[str] = None


class DocumentChunkMetadata(DocumentMetadata):
    document_id: Optional[str] = None


class DocumentChunk(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: DocumentChunkMetadata
    embedding: Optional[List[float]] = None


class DocumentChunkWithScore(DocumentChunk):
    score: float


class Document(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: Optional[DocumentMetadata] = None


class DocumentWithChunks(Document):
    chunks: List[DocumentChunk]


class DocumentMetadataFilter(BaseModel):
    document_id: Optional[str] = None
    source: Optional[Source] = None
    source_id: Optional[str] = None
    author: Optional[str] = None
    start_date: Optional[str] = None  # any date string format
    end_date: Optional[str] = None  # any date string format


class QueryElement(BaseModel):
    query: str = Field(None, description="The query string.")
    value: Any = Field(None, description="The query value.")
    top_k: Optional[int] = Field(3, description="The number of results to return.")
    filter: Optional[Dict[str, Any]] = Field(None, description="Filter options.")


class QueryWithEmbedding(QueryElement):
    embedding: Optional[List[float]]


class QueryResult(BaseModel):
    query: str = Field(None, description="The query string.")
    results: List[Dict[str, Any]] = Field(
        None, description="List of results for the query."
    )


class CompositeQuery(BaseModel):
    operator: str = Field(
        "AND", description="Logical operator to combine queries, e.g., 'AND', 'OR'"
    )
    queries: List[Union["CompositeQuery", QueryElement]]


class QueryMetadata(BaseModel):
    sort_by: Optional[str] = Field(None, description="Sort by this field.")
    sort_order: Optional[str] = Field(None, description="Sort order: 'asc' or 'desc'")
    limit: Optional[int] = Field(None, description="Limit the number of results.")
    offset: Optional[int] = Field(None, description="Skip this many results.")
    created_at: Optional[str]
    updated_at: Optional[str]


class QueryFragment(BaseModel):
    element: QueryElement
    composite: Optional[CompositeQuery]
    metadata: QueryMetadata
    chain_filter: Optional[object] = Field(
        None, description="Chain-specific filter options."
    )


class Plugin(BaseModel):
    name: str
    function: Callable[..., Any]  # Placeholder, adapt as needed


class CacheOptions(BaseModel):
    enabled: bool = Field(True, description="Whether to enable caching.")
    ttl: int = Field(60, description="Time-to-live for the cache in seconds.")


class RealTimeOptions(BaseModel):
    enabled: bool = Field(False, description="Whether to enable real-time updates.")
    channel: Optional[str] = Field(
        None, description="The channel to use for real-time updates."
    )


class PaginationOptions(BaseModel):
    page: int = Field(1, description="Page number.")
    per_page: int = Field(20, description="Items per page.")


class SortingOptions(BaseModel):
    field: str
    direction: str = Field("asc", description="Sort direction: asc or desc.")


class RateLimitOptions(BaseModel):
    max_calls: int = Field(60, description="Max API calls per minute.")
    period: int = Field(60, description="Rate limit period in seconds.")


class ErrorOptions(BaseModel):
    timeout: int = Field(30, description="Time in seconds before timing out.")
    retries: int = Field(3, description="Number of times to retry the query.")


class QueryOptions(BaseModel):
    pagination: Optional[PaginationOptions] = Field(
        None, description="Pagination settings."
    )
    sorting: Optional[SortingOptions] = Field(None, description="Sorting settings.")
    rate_limit: Optional[RateLimitOptions] = Field(
        None, description="Rate limit settings."
    )
    error: Optional[ErrorOptions] = Field(None, description="Error settings.")

    real_time: Optional[RealTimeOptions] = Field(
        None, description="Real-time update settings."
    )
    cache: Optional[CacheOptions] = Field(None, description="Cache settings.")


class ChainQuery(BaseModel):
    conversation_tree_type: str = Field(
        None, description="The type of conversation tree."
    )
    node_ids: Optional[List[str]] = Field(
        None, description="A list of node IDs to include in the conversation tree."
    )
    attribute_filter: Optional[Dict[str, Any]] = Field(
        None,
        description="A dictionary where the key is the node attribute and the value is the desired attribute value.",
    )


class ChainTreeQuery(ChainQuery):
    query_fragments: Optional[List[QueryFragment]] = Field(
        None, description="List of query fragments."
    )
    cache: Optional[CacheOptions] = Field(None, description="Cache settings.")

    real_time: Optional[RealTimeOptions] = Field(
        None, description="Real-time update settings."
    )
    plugins: Optional[List[Plugin]] = Field(
        None, description="List of plugins to extend query capabilities."
    )

    query_options: Optional[QueryOptions] = Field(None, description="Query options.")

    root_query: Optional[Union[CompositeQuery, QueryElement]] = Field(
        None, description="Root query to filter nodes."
    )
    metadata: Optional[QueryMetadata] = Field(
        None, description="Query metadata like sorting and pagination."
    )

    class Config:
        schema_extra = {
            "example": {
                "conversation_tree_type": "full",
                "node_ids": ["node_1", "node_2"],
                "attribute_filter": {"content": "hello"},
                "query_fragments": [
                    {
                        "element": {"type": "text", "value": "hello"},
                        "metadata": {
                            "created_at": "2023-09-03T12:34:56",
                            "updated_at": "2023-09-03T12:34:56",
                        },
                    }
                ],
                "plugins": [{"name": "Plugin1", "function": lambda x: x}],
                "query_options": {
                    "pagination": {"page": 1, "per_page": 20},
                    "sorting": {"field": "content", "direction": "asc"},
                    "rate_limit": {"max_calls": 60, "period": 60},
                    "error": {"timeout": 30, "retries": 3},
                    "real_time": {"enabled": True, "channel": "updates_channel"},
                    "cache": {"enabled": True, "ttl": 120},
                },
            }
        }
