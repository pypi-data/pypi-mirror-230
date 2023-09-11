from typing import List, Callable, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
import string


class BaseTreeGeneratorConfig(BaseModel):
    min_depth: int = Field(
        default=2,
        description="Minimum depth of the tree",
    )
    max_depth: int = Field(
        default=100,
    )

    min_children: int = Field(
        default=1,
        description="Minimum number of children per node",
    )

    max_children: int = Field(
        default=3,
        description="Maximum number of children per node",
    )

    min_content_length: int = Field(
        default=10,
        description="Minimum length of content per node",
    )

    max_content_length: int = Field(
        default=50,
        description="Maximum length of content per node",
    )

    content_characters: str = Field(
        default=string.ascii_letters + string.digits,
        description="Characters to use when generating content",
    )

    content_length_distribution: str = Field(
        default="uniform",
        description="Distribution of content length",
    )

    content_generation_algorithm: Optional[str] = Field(
        default="random",
        description="Algorithm to use when generating content",
    )

    tree_structure_distribution: str = Field(
        default="balanced",
        description="Distribution of tree structure",
    )

    use_random: bool = Field(
        default=True,
        description="Use random",
    )

    tree_generation_algorithm = Field(
        default="random",
        description="Algorithm to use when generating tree",
    )

    random_distribution: str = Field(
        default="uniform",
        description="Distribution of random",
    )

    number_of_nodes: int = Field(
        default=100,
        description="Number of nodes to generate",
    )

    class Config:
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "min_depth": 2,
                "max_depth": 100,
                "min_children": 1,
                "max_children": 3,
                "min_content_length": 10,
                "max_content_length": 50,
                "content_characters": string.ascii_letters + string.digits,
                "content_length_distribution": "uniform",
                "content_generation_algorithm": "random",
                "tree_structure_distribution": "balanced",
                "use_random": True,
            }
        }
