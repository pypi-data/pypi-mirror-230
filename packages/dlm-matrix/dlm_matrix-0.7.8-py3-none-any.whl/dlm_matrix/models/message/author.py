from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from dlm_matrix.type import RoleType


class Author(BaseModel):
    """
    Represents an author in the conversation.
    """

    role: RoleType = Field(..., description="The role of the author.")
    id: Optional[str] = Field(None, description="The id of the role.")
    type: Optional[str] = Field(None, description="The type of the role.")
    description: Optional[str] = Field(None, description="The description of the role.")
    metadata: Optional[Dict[str, Any]] or object = Field(
        None, description="Additional metadata about the author."
    )
    name: Optional[str] = Field(None, description="The name of the author.")


class AuthorList(BaseModel):
    """
    Represents a list of authors.
    """

    authors: List[Author] = Field(..., description="The list of authors.", min_items=1)
    roles: List[RoleType] = Field(
        default=[],
        description="The list of roles associated with the authors in the list.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roles = [author.role for author in self.authors]
