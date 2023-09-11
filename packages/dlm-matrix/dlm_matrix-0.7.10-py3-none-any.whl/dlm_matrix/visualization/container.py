from typing import Any, Dict, List, Optional, Callable, Tuple
import numpy as np
from dlm_matrix.transformation.tree import CoordinateTree
from dlm_matrix.transformation.coordinate import Coordinate
import concurrent.futures
import pandas as pd


class CoordinateContainer:
    """
    Custom container for CoordinateTree objects.
    Attributes:
        coordinate_trees (List[CoordinateTree]): A list of CoordinateTree objects.
    """

    def __init__(self, coordinate_trees: Optional[List[CoordinateTree]] = None):
        self.coordinate_trees = coordinate_trees

    def __repr__(self):
        return f"CoordinateContainer(coordinate_trees={self.coordinate_trees})"

    def to_list(self) -> List[CoordinateTree]:
        return self.coordinate_trees

    @classmethod
    def from_dict(cls, d: Dict[str, "CoordinateTree"]) -> "CoordinateContainer":
        return cls([coord_tree for coord_tree in d.values()])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "coordinate_trees": [
                coord_tree.dict() for coord_tree in self.coordinate_trees
            ]
        }

    def apply_func(
        self, func: Callable[[CoordinateTree], CoordinateTree]
    ) -> "CoordinateContainer":
        return CoordinateContainer(
            [func(coord_tree) for coord_tree in self.coordinate_trees]
        )

    def map(self, func: Callable[[CoordinateTree], Any]) -> List[Any]:
        return [func(coord_tree) for coord_tree in self.coordinate_trees]

    def filter(self, func: Callable[[CoordinateTree], bool]) -> "CoordinateContainer":
        return CoordinateContainer(
            [coord_tree for coord_tree in self.coordinate_trees if func(coord_tree)]
        )

    def to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame([coord_tree.dict() for coord_tree in self.coordinate_trees])

    def to_csv(self, path: str) -> None:
        self.to_pandas().to_csv(path)

    def sort(
        self,
        key: Optional[Callable[[CoordinateTree], Any]] = None,
        reverse: bool = False,
    ) -> "CoordinateContainer":
        return CoordinateContainer(
            sorted(self.coordinate_trees, key=key, reverse=reverse)
        )

    def shuffle(self, random_state: Optional[int] = None) -> "CoordinateContainer":
        if random_state is not None:
            np.random.seed(random_state)
        np.random.shuffle(self.coordinate_trees)
        return self

    def sample(
        self, n: int, random_state: Optional[int] = None
    ) -> "CoordinateContainer":
        if random_state is not None:
            np.random.seed(random_state)
        return CoordinateContainer(np.random.choice(self.coordinate_trees, n))

    def split(
        self, n: int, random_state: Optional[int] = None
    ) -> Tuple["CoordinateContainer", "CoordinateContainer"]:
        if random_state is not None:
            np.random.seed(random_state)
        np.random.shuffle(self.coordinate_trees)
        return (
            CoordinateContainer(self.coordinate_trees[:n]),
            CoordinateContainer(self.coordinate_trees[n:]),
        )

    def pipe(self, *funcs: Tuple[Callable[[Any], Any]]) -> Any:
        result = self
        for func in funcs:
            if isinstance(result, CoordinateContainer):
                if callable(func):
                    result = func(result)
                else:
                    raise TypeError("All elements of funcs must be callable")
            else:
                return result
        return result

    def _compute_distance_map(
        tetra_dict_1: Dict[str, CoordinateTree],
        tetra_dict_2: Dict[str, CoordinateTree],
    ) -> Dict[str, Tuple[str, float]]:
        distance_map = {}
        for message_id_1, coord_1 in tetra_dict_1.items():
            distances = {
                id: coord_1.calculate_distance(coord_2)
                for id, coord_2 in tetra_dict_2.items()
            }
            closest_coord_id, min_distance = min(distances.items(), key=lambda x: x[1])
            distance_map[message_id_1] = (closest_coord_id, min_distance)
        return distance_map

    def _compute_distance_map_parallel(
        self,
        conversation_dict_1: Dict[str, CoordinateTree],
        conversation_dict_2: Dict[str, CoordinateTree],
    ) -> Dict[str, Tuple[str, float]]:
        distance_map = {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {}
            for message_id_1, convo_1 in conversation_dict_1.items():
                futures[message_id_1] = executor.submit(
                    self._compute_distance_map, convo_1, conversation_dict_2
                )
            for message_id_1, future in futures.items():
                distance_map[message_id_1] = future.result()

        return distance_map

    @staticmethod
    def normalize_coordinates(
        tetra_dict: Dict[str, Coordinate]
    ) -> Dict[str, Coordinate]:
        """
        Normalizes the coordinates of the tetrahedron to the nearest 100.

        Args:
            tetra_dict: A dictionary mapping message IDs to their coordinates.

        Returns:
            Dict[str, Any]: The normalized tetra_dict with updated coordinates.
        """
        attributes = [
            attr for attr in Coordinate.__annotations__ if attr not in ["n_parts"]
        ]
        min_values = Coordinate(
            **{
                axis: np.min(
                    np.array([getattr(coord, axis) for coord in tetra_dict.values()])
                )
                for axis in attributes
            }
        )
        max_values = Coordinate(
            **{
                axis: np.max(
                    np.array([getattr(coord, axis) for coord in tetra_dict.values()])
                )
                for axis in attributes
            }
        )

        decimal_places = 3  # Specify the number of decimal places you want to round to

        def normalize_coord(coord):
            for axis in attributes:
                value = (getattr(coord, axis) - getattr(min_values, axis)) / (
                    getattr(max_values, axis) - getattr(min_values, axis)
                )
                setattr(coord, axis, np.round(value, decimal_places))
            return coord

        normalized_tetra_dict = {
            message_id: normalize_coord(coord)
            for message_id, coord in tetra_dict.items()
        }

        return normalized_tetra_dict

    @staticmethod
    def custom_scale_x_coordinates(
        tetra_dict: Dict[str, Coordinate],
        scaling_technique: str,
        scaled_t: Dict[str, float],
        desired_range: Tuple[float, float] = (0, 1),
    ) -> Dict[str, float]:
        """
        Apply custom scaling techniques to the x coordinates in the Coordinate Dataclasss.
        taking into account the scaled t coordinates.

        Args:
            scaling_technique (str): The scaling technique to apply. Choose from 'linear', 'logarithmic', 'sigmoid', 'discrete'.
            scaled_t (Dict[str, float]): Th
            e scaled t coordinates.
            desired_range (Tuple[float, float]): The desired range for the scaled x coordinates.

        Returns:
            Dict[str, float]: The scaled x coordinates.
        """

        # Extract the x coordinates from Coordinate Class
        x_coords = np.array([coord.x for coord in tetra_dict.values()])

        if scaling_technique == "linear":
            # Linear scaling
            x_min = np.min(x_coords)
            x_max = np.max(x_coords)
            scaled_x = (x_coords - x_min) / (x_max - x_min) * (
                desired_range[1] - desired_range[0]
            ) + desired_range[0]

        elif scaling_technique == "logarithmic":
            # Logarithmic scaling
            scaled_x = np.log(x_coords + 1)

        elif scaling_technique == "sigmoid":
            # Sigmoid scaling
            scaled_x = 1 / (1 + np.exp(-x_coords))

        elif scaling_technique == "discrete":
            # Discrete scaling
            n_intervals = len(np.unique(x_coords))
            scaled_x = np.floor(x_coords) % n_intervals

        else:
            raise ValueError(
                "Invalid scaling technique. Choose from 'linear', 'logarithmic', 'sigmoid', or 'discrete'."
            )

        # Convert scaled_x to a dictionary with regular Python integers
        scaled_x_dict = {
            message_id: int(scaled_x[i])
            for i, message_id in enumerate(tetra_dict.keys())
        }

        # Adjust scaled x coordinates based on the scaled t coordinates
        for message_id, t_coord in scaled_t.items():
            scaled_x_dict[message_id] = int(scaled_x_dict[message_id] + t_coord)

        return scaled_x_dict

    @staticmethod
    def custom_scale_t_coordinates(
        tetra_dict: Dict[str, Coordinate],
        scaling_technique: str,
        desired_range: Tuple[float, float] = (0, 1),
    ) -> Dict[str, float]:
        """
        Apply custom scaling techniques to the t coordinates in the Coordinate Dataclass.

        Args:
            scaling_technique (str): The scaling technique to apply. Choose from 'temporal_resolution',
                                        'time_weighting', 'time_clustering', 'time_based_relationships'.
            desired_range (Tuple[float, float]): The desired range for the scaled t coordinates.

        Returns:
            Dict[str, float]: The scaled t coordinates.
        """

        # Extract the t coordinates from Coordinate Class

        t_coords = np.array([coord.t for coord in tetra_dict.values()])

        if scaling_technique == "temporal_resolution":
            # Apply temporal resolution adjustment
            min_t = np.min(t_coords)
            scaled_t = t_coords - min_t

        elif scaling_technique == "time_weighting":
            # Apply time weighting scaling
            min_t = np.min(t_coords)
            max_t = np.max(t_coords)
            scaled_t = (t_coords - min_t) / (max_t - min_t) * (
                desired_range[1] - desired_range[0]
            ) + desired_range[0]

        elif scaling_technique == "time_based_relationships":
            # Apply time-based relationship scaling
            scaled_t = np.diff(t_coords)
            scaled_t = np.insert(scaled_t, 0, 0)  # Pad with zero for consistent length

        else:
            raise ValueError(
                "Invalid scaling technique. Choose from 'temporal_resolution', 'time_weighting', or 'time_based_relationships'."
            )

        # Create a dictionary mapping message IDs to scaled t coordinates
        scaled_t_dict = {
            message_id: float(scaled_t[i])
            for i, message_id in enumerate(tetra_dict.keys())
        }

        return scaled_t_dict

    @staticmethod
    def adaptive_temporal_topological_scaling(
        tetra_dict: Dict[str, "Coordinate"],
        x_scaling_technique: str = "discrete",
        t_scaling_technique: str = "time_based_relationships",
        t_scaling_range: Tuple[float, float] = (0, 1),
    ) -> Dict[str, "Coordinate"]:
        """
        Apply Adaptive Temporal-Topological Scaling (ATS) to the x and t coordinates within the Tetrahedron Representation.
        This method enhances the representation by incorporating adaptive scaling, topological considerations,
        non-linear transformations, temporal resolution adjustment, temporal dynamics modeling,
        and multimodal representations.

        Args:
            tetra_dict (Dict[str, Coordinate]): The original Tetrahedron Representation mapping message IDs to Coordinate objects.
            x_scaling_technique (str): The desired scaling technique for x coordinates. Options: 'linear', 'logarithmic', 'sigmoid', 'discrete'.
            t_scaling_technique (str): The desired scaling technique for t coordinates. Options: 'temporal_resolution', 'time_weighting', 'time_based_relationships'.
            t_scaling_range (Tuple[float, float]): The desired range for t scaling. Only applicable for certain t scaling techniques.
            topological_method (str): The topological method to use. Options: 'persistent_homology', 'graph_based'.
            temporal_modeling_method (str): The temporal modeling method to use. Options: 'autoregressive', 'state_space', 'recurrent_neural_network', etc.
            temporal_modeling_params (Dict[str, Any]): Additional parameters for the temporal modeling method.

        Returns:
            Dict[str, Coordinate]: The transformed Tetrahedron Representation with scaled x and t coordinates.
        """
        # Normalize the coordinates
        tetra_dict = CoordinateContainer.normalize_coordinates(tetra_dict)

        # Apply custom scaling for t coordinates
        scaled_t_coords = CoordinateContainer.custom_scale_t_coordinates(
            tetra_dict, t_scaling_technique, t_scaling_range
        )

        # Apply custom scaling for x coordinates
        scaled_x_coords = CoordinateContainer.custom_scale_x_coordinates(
            tetra_dict, x_scaling_technique, scaled_t_coords
        )

        # Update the coordinates in the Coordinate Dataclass
        transformed_representation = {
            message_id: Coordinate(
                x=scaled_x_coords[message_id],
                y=coord.y,
                z=coord.z,
                t=scaled_t_coords[message_id],
            )
            for message_id, coord in tetra_dict.items()
        }

        return transformed_representation
