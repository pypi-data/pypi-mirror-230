from pydantic import BaseModel
from typing import Any, Dict, Optional, List, Union, Type
from .author import Author, AuthorList
from .metadata import Metadata
from .content import Content
from .embedding import DocumentEmbeddings
from .connection import Connection
from .note import Annotations
from pydantic import BaseModel, Field
from uuid import uuid4
from dlm_matrix.type import NodeRelationship, RoleType
import torch


class ChainLinks(BaseModel):
    relationships: Dict[NodeRelationship, str] = Field(
        default=None, description="Node relationships associated with the message."
    )
    connections: Dict[str, Connection] = Field(
        default=None, description="Connections associated with the message."
    )


class ChainMessage(BaseModel):
    content: Optional[Content] = Field(
        default=None, description="The content of the message."
    )

    author: Optional[Union[Author, AuthorList]] = Field(
        default=None, description="The author of the message."
    )
    create_time: float = Field(
        default=None, description="Timestamp when the message was created."
    )
    end_turn: Optional[bool] = Field(
        default=None, description="Whether the message ends the current turn."
    )
    weight: int = Field(
        default=1,
        description="Weight indicating the message's importance or relevance.",
    )
    metadata: Optional[Union[Metadata, Dict[str, Any]]] = Field(
        default=None, description="Metadata associated with the message."
    )
    recipient: Optional[str] = Field(
        default=None, description="Recipient of the message, if applicable."
    )

    coordinate: Optional[Any] = Field(
        default=None,
        description="Coordinate in the embedding space for spatial querying.",
    )


class Chain(ChainMessage):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the message.",
    )
    embedding: DocumentEmbeddings = Field(
        default=None, description="Embedding and cluster information for the document."
    )
    links: ChainLinks = Field(
        default=None, description="Information about connections and sequencing."
    )
    annotations: Annotations = Field(
        default=None, description="Any notes or annotations related to the message."
    )

    children: Optional["Chain"] = Field(
        default=None, description="ID of the child message."
    )

    prev: Optional[str] = Field(default=None, description="ID of the previous message.")
    next: Optional[str] = Field(default=None, description="ID of the next message.")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
