from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel
from pydantic.fields import Field
import json

DEFAULT_TEXT_NODE_TMPL = "{metadata_str}\n\n{content}"
DEFAULT_METADATA_TMPL = "{key}: {value}"
DEFAULT_METADATA_SEPERATOR = "\n\n"
DEFAULT_CUSTOM_METADATA_KEY = "custom_metadata"


class FinishDetails(BaseModel):
    """
    Represents finish details for a message.
    Attributes:
        type (str): The type of finish details (text generation, classification, etc.).
        stop (str): Information on when the finish detail process stopped.
    """

    type: str = Field(
        ...,
        description="The type of finish details (text generation, classification, etc.).",
    )
    stop: str = Field(
        ..., description="Information on when the finish detail process stopped."
    )

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "type": "text_generation",
                "stop": "max_length",
            }
        }


class MetadataFinishDetails(BaseModel):
    """
    Represents finish details metadata for a message.
    Attributes:
        model_slug (str): The slug or identifier for the model used.
        finish_details (FinishDetails): Details on how the model finished processing the content.
        timestamp_ (str): The timestamp for when the finish details were generated.
        links (List[str]): List of links associated with the message.
    """

    model: Optional[str] = Field(
        None,
        description="The slug or identifier for the model used.",
        alias="model_slug",
    )
    finish_details: Optional[FinishDetails] = Field(
        None, description="Details on how the model finished processing the content."
    )

    timestamp_: Optional[str] = Field(
        None, description="The timestamp for when the finish details were generated."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model_slug": "gpt2",
                "finish_details": {
                    "type": "text_generation",
                    "stop": "max_length",
                },
                "timestamp_": "2021-06-01T12:00:00.000Z",
                "links": ["https://example.com", "https://example2.com"],
            }
        }


class Metadata(BaseModel):
    """
    Represents metadata associated with a message.
    Attributes:
        timestamp (Optional[str]): The timestamp for when the metadata was created.
        finish_details (Optional[MetadataFinishDetails]): Details about the model's finish process.
        metadata_details  (Optional[Dict[str, MetadataDetails]]): Any additional custom metadata.

    """

    timestamp: Optional[str] = Field(
        None, description="The timestamp for when the metadata was created."
    )
    metadata_finish_details: Optional[MetadataFinishDetails] = Field(
        None, description="Details about the model's finish process."
    )

    metadata_details: Optional[Dict[str, Any]]

    links: Optional[List[str]] = Field(
        None, description="List of links extracted from the message content."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2021-06-01T12:00:00.000Z",
                "finish_details": {
                    "model_slug": "gpt2",
                    "finish_details": {
                        "type": "text_generation",
                        "stop": "max_length",
                    },
                    "timestamp_": "2021-06-01T12:00:00.000Z",
                },
                "metadata_details": {
                    "custom_metadata": {
                        "key": "custom_metadata",
                        "value": "custom_metadata_value",
                    }
                },
                "links": ["https://example.com", "https://example.org"],
            }
        }

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.metadata_details = self.metadata_details or {}

    def to_dict(self) -> Dict[str, Any]:
        return self.dict(exclude_none=True)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
