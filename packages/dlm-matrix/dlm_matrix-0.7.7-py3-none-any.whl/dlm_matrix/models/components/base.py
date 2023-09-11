from typing import Any, Optional
from pydantic import BaseModel, Field


class BaseCoordinate(BaseModel):
    """
    Represents a coordinate in a space.
    """

    n_parts: int = Field(0, description="The number of parts of the coordinate.")


class Coordinate2D(BaseCoordinate):
    """
    Represents a 2D coordinate in a space.
    """

    x: Any = Field(0.0, description="The x-coordinate of the coordinate.")
    y: Any = Field(0.0, description="The y-coordinate of the coordinate.")


class Coordinate3D(Coordinate2D):
    """
    Represents a 3D coordinate in a space.
    """

    z: Any = Field(0.0, description="The z-coordinate of the coordinate.")


class Coordinate4D(Coordinate3D):
    """
    Represents a 4D coordinate in a space.
    """

    t: Any = Field(0.0, description="The t-coordinate of the coordinate.")
    create_time: Optional[str] = Field(
        None, description="The creation date of the message."
    )
