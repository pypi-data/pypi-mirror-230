from typing import Any, Dict, List, Optional
from .mapping import ChainMap
from pydantic import BaseModel, Field
from uuid import uuid4
import pandas as pd
import json
import networkx as nx


class ChainTree(BaseModel):
    """

    Represents a conversation as a tree of messages.
    """

    title: str = Field(None, description="The title of the conversation.")

    id: str = Field(default_factory=lambda: str(uuid4()))

    create_time: float = Field(
        None, description="The timestamp for when the conversation was created."
    )
    update_time: float = Field(
        None, description="The timestamp for when the conversation was last updated."
    )
    mapping: Dict[str, ChainMap] = Field(
        None,
        description="A dictionary mapping node IDs to their corresponding message nodes.",
    )

    moderation_results: Optional[List[Dict[str, Any]]] = Field(
        None, description="Moderation results associated with the conversation."
    )
    current_node: Optional[str] = Field(None, description="The ID of the current node.")


class ChainTreeIndex(BaseModel):
    conversation: ChainTree

    def to_dict(self) -> Dict[str, Any]:
        return {"conversation": self.conversation.dict()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChainTreeIndex":
        return cls(conversation=ChainTree.from_dict(data["conversation"]))
