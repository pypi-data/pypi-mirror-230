from typing import List, Optional, Union, Tuple, Dict
from dlm_matrix.transformation.operation import Operations
from collections import defaultdict
import numpy as np
from pydantic import Field
from uuid import uuid4


def first_element_or_value(value: Union[int, List[int]]) -> int:
    """Return the first element if the input is a list; otherwise, return the value itself."""
    if isinstance(value, list) and len(value) > 0:
        return value[0]
    return value


class Coordinate(Operations):
    id: str = Field(default_factory=lambda: str(uuid4()))
    # create a super

    @classmethod
    def create(
        cls,
        depth_args: Union[int, List[int]] = 0,
        sibling_args: Union[int, List[int]] = 0,
        sibling_count_args: Union[int, List[int]] = 0,
        time_args: Union[int, List[int]] = 0,
        n_parts_args: Union[int, List[int]] = 0,
    ):
        return cls(
            x=first_element_or_value(depth_args),
            y=first_element_or_value(sibling_args),
            z=first_element_or_value(sibling_count_args),
            t=first_element_or_value(time_args),
            n_parts=first_element_or_value(n_parts_args),
        )

    parent: "Operations" = None
    children: List["Operations"] = []
    history: List["Operations"] = []
    length: float = 0.0

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def merge_coordinates(coords: List["Coordinate"]) -> "Coordinate":
        """Merge a list of coordinates, calculating average values for each dimension."""
        avg_x = sum([coord.x for coord in coords]) / len(coords)
        avg_y = sum([coord.y for coord in coords]) / len(coords)
        avg_z = sum([coord.z for coord in coords]) / len(coords)
        avg_t = sum([coord.t for coord in coords]) / len(coords)

        return Coordinate(x=avg_x, y=avg_y, z=avg_z, t=avg_t)

    def path_length(self):
        """Calculate the length of the path traversed using NumPy."""
        # Convert history to a numpy array
        history_array = np.array(self.history)

        # Compute pairwise differences
        pairwise_diffs = np.diff(history_array, axis=0)

        # Compute distances
        pairwise_distances = np.linalg.norm(pairwise_diffs, axis=1)

        # Sum up the distances to get the total path length
        length = np.sum(pairwise_distances)

        self.length = length

        return length

    def path_curvature(self):
        """Compute the curvature of the path traversed using NumPy."""

        # Compute straight distance between the first and last points
        straight_distance = np.linalg.norm(
            np.array(self.history[-1]) - np.array(self.history[0])
        )

        # Compute the total traversed distance using the path_length method
        traversed_distance = self.path_length()

        # Compute the curvature
        curvature = (traversed_distance - straight_distance) / traversed_distance

        return curvature

    def tree_distance(self, other: Optional["Operations"] = None) -> int:
        """
        Calculate the tree distance between two nodes.

        Args:
            other (Optional[Operations]): Another coordinate object. Defaults to None.

        Returns:
            int: Distance in the tree structure.
        """
        if other is None:
            raise ValueError("The 'other' parameter cannot be None")

        if not isinstance(other, Operations):
            raise TypeError(
                f"Expected 'Operations' type for 'other', got {type(other)}"
            )

        if self == other:
            return 0

        if not hasattr(self, "parent") or not hasattr(other, "parent"):
            raise AttributeError("Both nodes must have a 'parent' attribute")

        if self.is_same_depth_as(other):
            return abs(self.y - other.y)

        distance_to_root = self.x
        other_distance_to_root = other.x

        # Align depths
        while self.x > other.x:
            self = self.parent
            if self is None:
                raise ValueError("Node has no parent, cannot align depths")
            distance_to_root -= 1

        while other.x > self.x:
            other = other.parent
            if other is None:
                raise ValueError("Node has no parent, cannot align depths")
            other_distance_to_root -= 1

        # Traverse to the common ancestor
        while self != other:
            self = self.parent
            other = other.parent
            if self is None or other is None:
                raise ValueError("Node has no parent, cannot find common ancestor")
            distance_to_root += 1
            other_distance_to_root += 1

        return distance_to_root + other_distance_to_root

    def depth_summary(self) -> dict:
        """
        Get a summary of nodes at each depth of the tree.

        Returns:
            dict: A summary of the tree depths.
        """
        summary = defaultdict(int)
        summary[self.x] = 1
        for child in self.children:
            child_summary = child.depth_summary()
            for depth, count in child_summary.items():
                summary[depth] += count
        return dict(summary)

    @staticmethod
    def tree_to_tetra_dict(
        tree: "Coordinate",
    ) -> Dict[str, Tuple[float, float, float, float, int]]:
        """
        Converts a CoordinateTree into a dictionary where each key is a node id,
        and the value is a tuple containing (x, y, z, t, n_parts) for that node.

        Parameters:
            tree (CoordinateTree): The root of the CoordinateTree.

        Returns:
            Dict[str, Tuple[float, float, float, float, int]]: A dictionary mapping node IDs to tuples of coordinates.
        """

        tetra_dict = {}
        stack = [tree]

        while stack:
            node = stack.pop()

            if not node.id:
                continue

            # Validate the coordinates
            if any(
                val is None for val in [node.x, node.y, node.z, node.t, node.n_parts]
            ):
                continue

            # Add to tetra_dict
            tetra_dict[node.id] = (node.x, node.y, node.z, node.t, node.n_parts)

            # Add children to stack
            stack.extend(node.children)

        return tetra_dict
