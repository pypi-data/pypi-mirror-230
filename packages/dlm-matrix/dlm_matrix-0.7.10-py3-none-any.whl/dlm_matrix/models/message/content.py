from typing import List, Optional, Any
from pydantic import BaseModel, Field
from dlm_matrix.type import ContentType


class Content(BaseModel):
    """
    The base class for all content types.
    """

    text: Optional[str] = Field(
        None, description="The text content of the message (if any)."
    )

    content_type: ContentType = Field(
        ContentType.TEXT, description="The type of content (text, image, audio, etc.)"
    )
    parts: Optional[List[str]] = Field(
        None, description="The parts of the content (text, image, audio, etc.)"
    )

    part_lengths: Optional[Any] = Field(
        None, description="The lengths of the parts of the content."
    )

    embedding: Optional[List[float]] = None

    doc_hash: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"
        json_schema_extra = {
            "example": {
                "content_type": "text",
                "parts": ["Hello, how are you?"],
            }
        }

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.parts:
            self.text = self.parts[0]
            self.part_lengths = len(self.text.split("\n\n")) if self.text else []
        else:
            self.part_lengths = 0  # If parts are not provided, set part_lengths to 0.

    @classmethod
    def from_text(cls, text: str):
        """Creates a Content object from text."""
        return cls(content_type=ContentType.TEXT, parts=[text])

    @classmethod
    def from_content_type(cls, content_type: ContentType, parts: List[str]):
        """Creates a Content object from content type and parts."""
        return cls(content_type=content_type, parts=parts)

    def get_text(self) -> str:
        """Get text."""
        if self.text is None:
            raise ValueError("text field not set.")
        return self.text

    def get_doc_id(self) -> str:
        """Get doc_id."""
        if self.id is None:
            raise ValueError("id not set.")
        return self.id

    def get_doc_hash(self) -> str:
        """Get doc_hash."""
        if self.doc_hash is None:
            raise ValueError("doc_hash is not set.")
        return self.doc_hash

    @property
    def is_id_none(self) -> bool:
        """Check if id is None."""
        return self.id is None

    @property
    def is_text_none(self) -> bool:
        """Check if text is None."""
        return self.text is None

    def get_embedding(self) -> List[float]:
        """Get embedding.

        Errors if embedding is None.

        """
        if self.embedding is None:
            raise ValueError("embedding not set.")
        return self.embedding
