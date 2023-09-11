from typing import Dict, Any, List, Union
from dlm_matrix.models.components import Coordinate4D
from pydantic import ValidationError
import torch
import numpy as np


class BaseOperations(Coordinate4D):
    def __iter__(self):
        return iter(self.dict().values())

    def fetch_value(self, field: str) -> float:
        """Fetch a value from the coordinate fields."""
        return getattr(self, field, 0.0)

    @classmethod
    def build_from_dict(cls, data: Dict[str, Any]) -> "BaseOperations":
        """Build a Coordinate from a dictionary."""
        return cls(**data)

    @staticmethod
    def get_coordinate_names() -> List[str]:
        """Return names of the coordinate dimensions."""
        return [
            "depth_x",
            "sibling_y",
            "sibling_count_z",
            "time_t",
            "n_parts",
        ]

    @staticmethod
    def from_tuple(values: tuple) -> "BaseOperations":
        """Initialize Coordinate from a tuple."""
        return BaseOperations(
            x=values[0],
            y=values[1],
            z=values[2],
            t=values[3],
            n_parts=values[4],
        )

    @staticmethod
    def unflatten(values: np.ndarray) -> "BaseOperations":
        """Convert a flattened array back into a Coordinate."""
        assert values.shape[0] == 5, "Invalid shape for unflattening"
        return BaseOperations(
            x=values[0],
            y=values[1],
            z=values[2],
            t=values[3],
            n_parts=values[4],
        )

    @classmethod
    def from_tensor(cls, tensor: torch.Tensor) -> "BaseOperations":
        """Initialize Coordinate from a PyTorch tensor."""
        return cls.unflatten(tensor.cpu().numpy())

    def to_reduced_array(self, exclude_t: bool = False) -> np.ndarray:
        """
        Convert the Coordinate object into a reduced numpy array representation, excluding n_parts.

        Args:
            exclude_t (bool, optional): If set to True, the 't' value will not be included in the array.
                                       Defaults to False.

        Returns:
            A numpy array representation of the Coordinate object.
        """
        if exclude_t:
            return np.array([self.x, self.y, self.z])
        else:
            return np.array([self.x, self.y, self.z, self.t])

    @staticmethod
    def to_tensor(
        coordinates_dict: Dict[str, Union["BaseOperations", np.array]]
    ) -> torch.Tensor:
        """
        Converts a dictionary of Coordinate objects or flattened Coordinate arrays into a PyTorch tensor.

        Args:
            coordinates_dict: The dictionary of Coordinate objects or flattened Coordinate arrays.

        Returns:
            A PyTorch tensor representation of the Coordinate objects or their flattened representations in the dictionary.
        """
        # Check if the values in the dictionary are Coordinate objects. If they are, use the reduced representation.
        coordinates_list = [
            value.to_reduced_array() if isinstance(value, BaseOperations) else value
            for value in coordinates_dict.values()
        ]

        # Ensure the array values are of the expected shape (i.e., length 4). This will handle cases where np.arrays are provided directly.
        coordinates_list = [coords[:4] for coords in coordinates_list]

        # Stack them into a 2D numpy array
        coordinates_array = np.stack(coordinates_list, axis=0)

        # Convert the 2D array to a PyTorch tensor.
        coordinates_tensor = torch.tensor(coordinates_array, dtype=torch.float32)

        return coordinates_tensor

    @staticmethod
    def flatten(coordinate: "BaseOperations") -> np.ndarray:
        """Flatten the Coordinate instance into a numpy array."""
        return np.array(
            [
                coordinate.x,
                coordinate.y,
                coordinate.z,
                coordinate.t,
                coordinate.n_parts,
            ]
        )

    def to_list(self) -> List[float]:
        """Convert Coordinate to list."""

        return [self.x, self.y, self.z, self.t, self.n_parts]

    def tuple(self) -> tuple:
        """Convert Coordinate to tuple."""
        return tuple(self.dict().values())

    @staticmethod
    def flatten_list(coordinates: List["BaseOperations"]) -> np.ndarray:
        """Flatten a list of Coordinates."""
        return np.array([BaseOperations.flatten(c) for c in coordinates])

    @staticmethod
    def flatten_list_of_lists(coordinates: List[List["BaseOperations"]]) -> np.ndarray:
        """Flatten a list of list of Coordinates."""
        return np.array([[BaseOperations.flatten(c) for c in cs] for cs in coordinates])

    @staticmethod
    def string_to_coordinate(coordinate_str: str) -> "BaseOperations":
        """Convert a string representation to Coordinate."""
        coordinate_arr = np.fromstring(coordinate_str, sep=",")
        if coordinate_arr.shape[0] != 5:
            raise ValidationError("Invalid string representation for Coordinate.")
        return BaseOperations.unflatten(coordinate_arr)

    @staticmethod
    def coordinate_to_string(coordinate: "BaseOperations", separator: str = ",") -> str:
        """Convert Coordinate to string representation."""
        return np.array2string(coordinate, separator=separator)[1:-1]

    @staticmethod
    def create_sequence_from_coordinates(
        coordinates: list, convert_to_string: bool = False
    ):
        sequence = []

        # Flatten the list of coordinates
        flattened_coordinates = BaseOperations.flatten_list(coordinates)

        # Convert each flattened coordinate to string format, if required
        if convert_to_string:
            str_coordinates = [
                BaseOperations.coordinate_to_string(fc, separator=",")
                for fc in flattened_coordinates
            ]
        else:
            str_coordinates = flattened_coordinates  # Keep original coordinates

        # Create the sequence of key-value pairs
        sequence = [(c.id, sc) for c, sc in zip(coordinates, str_coordinates)]

        return sequence

    @staticmethod
    def stack_coordinates(
        coordinates_dict: Dict[str, Union["BaseOperations", np.array]]
    ) -> np.array:
        """Stack coordinates from a dictionary."""
        return np.stack(list(coordinates_dict.values()), axis=0)

    @staticmethod
    def to_tensor_from_dict(
        coordinates_dict: Dict[str, Union["BaseOperations", np.array]]
    ) -> torch.Tensor:
        """Convert dictionary of Coordinates to tensor."""
        coordinates_array = BaseOperations.stack_coordinates(coordinates_dict)
        return torch.tensor(coordinates_array, dtype=torch.float32)

    @classmethod
    def batch_to_tensor(cls, batch: List["BaseOperations"]) -> torch.Tensor:
        """Convert a batch of Coordinates to a single tensor."""
        return torch.stack([coordinate.to_tensor() for coordinate in batch])

    def serialize(self) -> str:
        """Serialize the Coordinate object to a string."""
        return ",".join([str(x) for x in self])

    @classmethod
    def deserialize(cls, data: str) -> "BaseOperations":
        """Deserialize a string to a Coordinate object."""
        values = list(map(float, data.split(",")))
        return cls(
            x=values[0], y=values[1], z=values[2], t=values[3], n_parts=values[4]
        )

    def save(self, filename: str) -> None:
        """Save the serialized Coordinate object to a file."""
        with open(filename, "w") as f:
            f.write(self.serialize())

    @classmethod
    def load(cls, filename: str) -> "BaseOperations":
        """Load a Coordinate object from a file."""
        with open(filename, "r") as f:
            data = f.read().strip()
        return cls.deserialize(data)
