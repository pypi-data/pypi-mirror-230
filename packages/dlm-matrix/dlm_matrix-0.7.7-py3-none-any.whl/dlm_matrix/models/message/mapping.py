from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from dlm_matrix.models.message.chain import Chain
from dlm_matrix.type import NodeRelationship


class ChainMap(BaseModel):
    """
    Represents a mapping between a message and its relationships.
    id (str): Unique identifier for the mapping.
    message (Optional[Message]): The message associated with the mapping.
    parent (Optional[str]): The ID of the parent message.
    children (List[str]): The IDs of the child messages.
    """

    id: str = Field(..., description="Unique identifier for the mapping.")

    message: Optional[Chain] = Field(
        None, description="The message associated with the mapping."
    )

    parent: Optional[str] = Field(None, description="The ID of the parent message.")

    children: Optional[List[str]] = Field(
        [], description="The IDs of the child messages."
    )

    references: Optional[List[str]] = Field(
        [], description="The IDs of the referenced messages."
    )

    relationships: Dict[NodeRelationship, str] = Field(
        None,
        description="Relationships associated with the message.",
    )

    prev: Optional[str] = Field(None, description="The ID of the previous message.")

    next: Optional[str] = Field(None, description="The ID of the next message.")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
