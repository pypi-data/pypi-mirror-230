from typing import List, Dict, Any, Optional, Union, Callable
from dlm_matrix.transformation.coordinate import Coordinate
from pydantic import Field
from collections import defaultdict
import numpy as np
import threading
import logging
import functools


def memoize(f):
    cache = {}

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            result = f(*args, **kwargs)
            cache[key] = result
        return cache[key]

    return wrapped


class CoordinateTree(Coordinate):  # Inherits from Coordinate
    children: List["CoordinateTree"] = Field(
        default_factory=list, description="The children of the node."
    )

    message_info: Any = Field(None)  # or a more specific type if you have one

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child

    def find_node_by_id(self, node_id: str) -> Optional["CoordinateTree"]:
        for node in self:
            if node.id == node_id:
                return node
        return None


    def classify_by_depth(
        self,
    ) -> Dict[float, Dict[str, Union[List["CoordinateTree"], float]]]:
        """
        Classify the nodes by their depth and compute the density of nodes at each depth.

        :return: Dictionary where keys are depths, and values are another dictionary containing nodes at that depth and the density.
        """

        # Group nodes by their depth
        nodes_by_depth = defaultdict(list)
        total_nodes = 0

        for node in self:
            depth = self.x
            nodes_by_depth[depth].append(node)
            total_nodes += 1

        # Compute the density for each depth and restructure the result
        depth_density_data = {}

        for depth, nodes in nodes_by_depth.items():
            depth_density_data[depth] = {
                "nodes": nodes,
                "density": len(nodes) / total_nodes,
            }

        return depth_density_data

    def compute_sibling_sequences(
        self, nodes: List["CoordinateTree"]
    ) -> List[List["CoordinateTree"]]:
        # First, sort nodes by their y-coordinate. In case of a tie (same y-coordinate), sort by t-coordinate
        nodes.sort(key=lambda node: (node.y, node.create_time))

        sequences = [[nodes[0]]]

        for i in range(1, len(nodes)):
            # Check if the y-coordinate of the current node is consecutive to the previous node
            is_consecutive_y = nodes[i].y == nodes[i - 1].y + 1

            if (
                nodes[i].create_time is not None
                and nodes[i - 1].create_time is not None
            ):
                # If nodes have the same y-coordinate, they should be sequenced based on their create_time
                is_same_y = nodes[i].y == nodes[i - 1].y
                is_earlier_t = nodes[i].create_time < nodes[i - 1].create_time

                if is_consecutive_y or (is_same_y and not is_earlier_t):
                    sequences[-1].append(nodes[i])
                else:
                    sequences.append([nodes[i]])
            else:
                # Handle the case where create_time is None for one or both nodes
                if is_consecutive_y:
                    sequences[-1].append(nodes[i])
                else:
                    sequences.append([nodes[i]])

        return sequences

    def check_homogeneity(
        self, sequence: List["CoordinateTree"]
    ) -> List[Dict[str, Any]]:
        """
        Check homogeneity within a sequence with depth-based importance score.

        :param sequence: List of CoordinateTree objects to check for homogeneity.
        :return: List of dictionaries containing homogeneous groups and their importance scores.
        """

        # Lists to keep track of homogeneous groups and their corresponding importance scores
        homogeneous_groups = []
        importance_scores = []

        # Calculate the initial importance score for the first coordinate in the sequence
        importance_scores.append(sequence[0].x * len(sequence[0].children))

        current_group = [sequence[0]]
        for i in range(1, len(sequence)):
            if sequence[i].z == sequence[i - 1].z:
                current_group.append(sequence[i])
                importance_scores[-1] += sequence[i].x * len(sequence[i].children)
            else:
                homogeneous_groups.append(
                    {
                        "group": current_group,
                        "importance_score": importance_scores[-1] / len(current_group),
                    }
                )
                current_group = [sequence[i]]
                importance_scores.append(sequence[i].x * len(sequence[i].children))

        # Add the last group to the result
        if current_group:
            homogeneous_groups.append(
                {
                    "group": current_group,
                    "importance_score": importance_scores[-1] / len(current_group),
                }
            )

        return homogeneous_groups

    def compute_group_sizes(self) -> Dict[float, float]:
        """Compute the depth-adjusted size of each homogeneous group in the tree."""
        group_sizes = defaultdict(float)

        for node in self:
            z_value = node.z
            adjustment_factor = 1 / (1 + node.x)
            group_sizes[z_value] += adjustment_factor

        return group_sizes

    def get_group_characteristics(
        self, groups: List[List["CoordinateTree"]]
    ) -> List[Dict[str, Union[float, List["CoordinateTree"]]]]:
        group_characteristics = []

        for group in groups:
            filtered_group = []

            # Filter out elements that are not of type CoordinateTree
            for elem in group:
                if not isinstance(elem, CoordinateTree):
                    continue
                filtered_group.append(elem)

            if (
                not filtered_group
            ):  # If all elements are of unexpected type, skip this group
                continue

            depths = [node.x for node in filtered_group]
            times = [node.t for node in filtered_group]

            size = len(filtered_group)
            if size == 0:
                print("Unexpected: filtered_group has size 0")
                continue

            mean_depth = sum(depths) / size if size != 0 else 0
            temporal_range = max(times) - min(times) if times else 0

            divisor = size * mean_depth
            spatial_density = (
                sum(node.y for node in filtered_group) / divisor if divisor != 0 else 0
            )
            time_consistency = 1 / (1 + temporal_range)

            characteristics = {
                "size": size,
                "mean_depth": mean_depth,
                "temporal_range": temporal_range,
                "spatial_density": spatial_density,
                "time_consistency": time_consistency,
                "group": filtered_group,
            }
            group_characteristics.append(characteristics)

        return group_characteristics

    @memoize
    def get_group_characteristics_memoized(self, groups):
        return self.get_group_characteristics(groups)

    def find_maximus_triangle(
        self, weight_function: Optional[Callable[[float], Dict[str, float]]] = None
    ) -> List["CoordinateTree"]:
        def worker(sequence, depth, WEIGHTS, output):
            if not sequence:
                return
            homogeneous_groups = self.check_homogeneity(sequence)
            actual_groups = [group_dict["group"] for group_dict in homogeneous_groups]
            if not actual_groups:
                return
            group_characteristics = self.get_group_characteristics_memoized(
                actual_groups
            )

            local_max_score = 0
            local_maximus = None
            for characteristics in group_characteristics:
                score = sum(
                    WEIGHTS.get(key, 0) * characteristics.get(key, 0) for key in WEIGHTS
                )

                if score > local_max_score:
                    local_max_score = score
                    local_maximus = characteristics["group"]

            output.append((local_max_score, local_maximus))

        nodes_by_depth = self.classify_by_depth()
        maximus_triangle = []
        max_score = 0

        def default_weight_function(depth: float) -> Dict[str, float]:
            return {
                "size": 1.0,
                "mean_depth": depth * 0.1,
                "spatial_density": 1.5,
                "time_consistency": 1.2,
            }

        if weight_function is None:
            weight_function = default_weight_function

        threads = []
        output = []
        for depth, depth_data in nodes_by_depth.items():
            WEIGHTS = weight_function(depth)
            nodes = depth_data.get("nodes", [])
            if not isinstance(nodes, list) or not nodes:
                continue

            sequences = self.compute_sibling_sequences(nodes)
            for sequence in sequences:
                t = threading.Thread(
                    target=worker, args=(sequence, depth, WEIGHTS, output)
                )
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        for local_max_score, local_maximus in output:
            if local_max_score > max_score:
                max_score = local_max_score
                maximus_triangle = local_maximus

        logging.info(f"Maximus triangle identified with score: {max_score}")

        return maximus_triangle

    def rotate_subtree(self, subtree_id: str, angle_degree: float):
        """
        Rotates a given subtree by the specified angle (in degrees)
        around its root node. This can be a simulation of shifting a conversation topic.
        """
        subtree = self.subtree_by_node_id(subtree_id)
        if not subtree:
            return

        for node in subtree:
            # Just a simple rotation around the 'y' axis (can be extended to other axes)
            x, y = node.x, node.y
            angle_rad = np.radians(angle_degree)
            new_x = x * np.cos(angle_rad) - y * np.sin(angle_rad)
            new_y = x * np.sin(angle_rad) + y * np.cos(angle_rad)
            if isinstance(node, Coordinate):
                node.x = new_x
                node.y = new_y
            else:
                node[0], node[1] = new_x, new_y

    def subtree_by_node_id(self, node_id: str) -> Optional["CoordinateTree"]:
        """Fetches a subtree starting from the provided node id."""
        for subtree in self:
            if subtree.root_id == node_id:
                return subtree
        return None

    def get_subtree_coordinates(self, subtree_id: str) -> List[Coordinate]:
        """Fetches the coordinates of a subtree."""
        subtree = self.subtree_by_node_id(subtree_id)
        if not subtree:
            return []

        return [node for node in subtree]

    def get_subtree_coordinates_by_depth(
        self, subtree_id: str
    ) -> Dict[float, List[Coordinate]]:
        """Fetches the coordinates of a subtree by depth."""
        subtree = self.subtree_by_node_id(subtree_id)
        if not subtree:
            return {}

        coordinates_by_depth = defaultdict(list)
        for node in subtree:
            depth = node.x
            coordinates_by_depth[depth].append(node)
        return coordinates_by_depth

    def visualize_tree(self, level=0, prefix="--> ") -> str:
        """
        Enhanced tree visualization using ASCII characters.
        """
        tree_str = "|   " * (level - 1) + prefix + str(self) + "\n"
        for child in self.children:
            tree_str += child.visualize_tree(level + 1)
        return tree_str

    @staticmethod
    # Create an example conversion function
    def convert_coordinate_to_tuple(coord):
        # Assuming you somehow calculate Depth, Sibling, Sibling Count from the Coordinate object
        depth = coord.x
        sibling = coord.y
        sibling_count = coord.z
        return (depth, sibling, sibling_count)

    @staticmethod
    def depth_first_search(
        tree: "CoordinateTree", predicate: Callable[["CoordinateTree"], bool]
    ) -> Optional["CoordinateTree"]:
        if predicate(tree):
            return tree
        else:
            for child in tree.children:
                result = CoordinateTree.depth_first_search(child, predicate)
                if result is not None:
                    return result
            return None

    @staticmethod
    def breadth_first_search(
        tree: "CoordinateTree", predicate: Callable[["CoordinateTree"], bool]
    ) -> Optional["CoordinateTree"]:
        queue = [tree]
        while queue:
            node = queue.pop(0)
            if predicate(node):
                return node
            else:
                queue.extend(node.children)
        return None

    @staticmethod
    def depth_first_search_all(
        tree: "CoordinateTree", predicate: Callable[["CoordinateTree"], bool]
    ) -> List["CoordinateTree"]:
        results = []
        if predicate(tree):
            results.append(tree)
        for child in tree.children:
            results.extend(CoordinateTree.depth_first_search_all(child, predicate))
        return results

    @classmethod
    def build_from_dict(cls, d: Dict[str, Any]) -> "CoordinateTree":
        return cls(
            id=d["id"],
            x=d["x"],
            y=d["y"],
            z=d["z"],
            t=d["t"],
            n_parts=d["n_parts"],
            children=[cls.build_from_dict(child) for child in d["children"]],
        )

    @classmethod
    def from_tree_structure(
        cls, message_id: str, tree_structure: Dict[str, Dict[str, Any]]
    ) -> "CoordinateTree":
        node_info = tree_structure.get(message_id, {})
        children = [
            cls.from_tree_structure(child_id, tree_structure)
            for child_id in node_info.get("children", [])
        ]
        message_info = node_info.get("message", {})
        return cls(id=message_id, children=children, message_info=message_info)

    def to_tree_structure(self) -> Dict[str, Dict[str, Any]]:
        tree_structure = {}
        for node in self:
            tree_structure[node.id] = {
                "children": [child.id for child in node.children],
                "message": node.message_info,
            }
        return tree_structure
