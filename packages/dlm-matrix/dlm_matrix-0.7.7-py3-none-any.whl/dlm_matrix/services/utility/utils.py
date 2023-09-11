from typing import Any, Callable, List, Optional, Tuple, Union, Dict
import networkx as nx
import numpy as np


def validate_parameters(
    nodes: List[Tuple[Any, ...]],
    calculate_weight: Optional[Callable],
    should_connect: Optional[Callable],
    directed: bool,
    # Add other parameters if needed
):
    if not all(isinstance(node, tuple) and len(node) >= 2 for node in nodes):
        raise ValueError(
            "Each node should be a tuple with at least two elements: an identifier and one or more values."
        )
    if calculate_weight is not None and not callable(calculate_weight):
        raise ValueError(
            "If provided, calculate_weight must be a callable function that takes two nodes and returns an integer."
        )
    if should_connect is not None and not callable(should_connect):
        raise ValueError(
            "If provided, should_connect must be a callable function that takes two nodes and returns a boolean."
        )
    if not isinstance(directed, bool):
        raise ValueError("The directed argument must be a boolean value.")


def calculate_weight_euclidean(node1: Tuple[Any, ...], node2: Tuple[Any, ...]) -> float:
    """
    Calculates the weight of an edge as the Euclidean distance between the node values.

    Args:
        node1 (Tuple[Any, ...]): The first node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.
        node2 (Tuple[Any, ...]): The second node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.

    Returns:
        float: The Euclidean distance between the nodes.
    """

    # Extract coordinates; assume first element in the tuple is an identifier, not a coordinate
    coords1 = node1[1:]
    coords2 = node2[1:]

    # Check if both nodes have the same number of coordinates
    if len(coords1) != len(coords2):
        raise ValueError("Both nodes must have the same number of coordinates.")

    return np.linalg.norm(np.array(coords1) - np.array(coords2))


def calculate_weight_haversine(node1: Tuple[Any, ...], node2: Tuple[Any, ...]) -> float:
    """
    Calculates the weight of an edge as the Haversine distance between the node values.

    Args:
        node1 (Tuple[Any, ...]): The first node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.
        node2 (Tuple[Any, ...]): The second node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.

    Returns:
        float: The Haversine distance between the nodes.
    """

    # Extract coordinates; assume first element in the tuple is an identifier, not a coordinate
    coords1 = node1[1:]
    coords2 = node2[1:]

    # Check if both nodes have the same number of coordinates
    if len(coords1) != len(coords2):
        raise ValueError("Both nodes must have the same number of coordinates.")

    # Convert to radians
    coords1 = np.radians(coords1)
    coords2 = np.radians(coords2)

    # Compute Haversine distance
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    return c


def calculate_weight_contraction(
    node1: Tuple[Any, ...], node2: Tuple[Any, ...]
) -> float:
    """
    Calculates the weight of an edge as the contraction between the node values.

    Args:
        node1 (Tuple[Any, ...]): The first node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.
        node2 (Tuple[Any, ...]): The second node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.

    Returns:
        float: The contraction between the nodes.
    """

    # Extract coordinates; assume first element in the tuple is an identifier, not a coordinate
    coords1 = node1[1:]
    coords2 = node2[1:]

    # Check if both nodes have the same number of coordinates
    if len(coords1) != len(coords2):
        raise ValueError("Both nodes must have the same number of coordinates.")

    return np.sum(np.abs(np.array(coords1) - np.array(coords2))) / np.sum(
        np.abs(np.array(coords1) + np.array(coords2))
    )


def calculate_weight_cosine(node1: Tuple[Any, ...], node2: Tuple[Any, ...]) -> float:
    """
    Calculates the weight of an edge as the cosine distance between the node values.

    Args:
        node1 (Tuple[Any, ...]): The first node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.
        node2 (Tuple[Any, ...]): The second node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.

    Returns:
        float: The cosine distance between the nodes.
    """

    # Extract coordinates; assume first element in the tuple is an identifier, not a coordinate
    coords1 = node1[1:]
    coords2 = node2[1:]

    # Check if both nodes have the same number of coordinates
    if len(coords1) != len(coords2):
        raise ValueError("Both nodes must have the same number of coordinates.")

    return 1 - np.dot(coords1, coords2) / (
        np.linalg.norm(coords1) * np.linalg.norm(coords2)
    )


def calculate_weight_manhattan(node1: Tuple[Any, ...], node2: Tuple[Any, ...]) -> float:
    """
    Calculates the weight of an edge as the Manhattan distance between the node values.

    Args:
        node1 (Tuple[Any, ...]): The first node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.
        node2 (Tuple[Any, ...]): The second node, represented as a tuple where the first element is the node ID and the subsequent elements are coordinates.

    Returns:
        float: The Manhattan distance between the nodes.
    """

    # Extract coordinates; assume first element in the tuple is an identifier, not a coordinate
    coords1 = node1[1:]
    coords2 = node2[1:]

    # Check if both nodes have the same number of coordinates
    if len(coords1) != len(coords2):
        raise ValueError("Both nodes must have the same number of coordinates.")

    return np.sum(np.abs(np.array(coords1) - np.array(coords2)))


def sequence_to_graph(
    sequence: List[Dict[str, Union[int, float, None, Dict]]],
    directed: bool = True,
    multigraph: bool = False,
) -> Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]:
    """
    Converts a sequence (list of dictionaries) back to a NetworkX graph.
    """
    # Initialize an empty graph based on the given parameters
    if multigraph:
        graph = nx.MultiDiGraph() if directed else nx.MultiGraph()
    else:
        graph = nx.DiGraph() if directed else nx.Graph()

    # Iterate through the sequence to add edges to the graph
    for edge in sequence:
        start_node = edge["start_node"]
        end_node = edge["end_node"]
        weight = edge.get("weight", None)
        edge_attr = edge.get("edge_attr", {})
        node_attr_1 = edge.get("node_attr_1", {})
        node_attr_2 = edge.get("node_attr_2", {})

        # Add nodes and their attributes if not already added
        if start_node not in graph:
            graph.add_node(start_node, **node_attr_1)
        if end_node not in graph:
            graph.add_node(end_node, **node_attr_2)

        # Add edge with attributes
        if weight is not None:
            edge_attr["weight"] = weight
        graph.add_edge(start_node, end_node, **edge_attr)

    return graph


def graph_to_sequence(
    graph: Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
) -> List[Dict[str, Union[int, float, None, Dict]]]:
    """
    Converts a NetworkX graph to a sequence (list of dictionaries).
    """
    sequence = []
    for u, v, data in graph.edges(data=True):
        edge_dict = {
            "start_node": u,
            "end_node": v,
            "weight": data.get("weight", None),
            "node_attr_1": graph.nodes[u],
            "node_attr_2": graph.nodes[v],
            "edge_attr": data,
        }
        sequence.append(edge_dict)

    return sequence


def create_fully_connected_graph(
    nodes: List[Tuple[Any, ...]],
    calculate_weight: Optional[Callable] = calculate_weight_euclidean,
    should_connect: Optional[Callable] = calculate_weight_cosine,
    directed: bool = False,
    multigraph: bool = False,
    self_loops: bool = True,
    node_attributes: Optional[Dict[Any, Dict[str, Any]]] = None,
    edge_attributes: Optional[Dict[Tuple[Any, Any], Dict[str, Any]]] = None,
    return_sequence: bool = True,  # New parameter to specify the output format
) -> Union[nx.Graph, List[Dict[str, Union[int, float, None]]]]:
    """
    Takes a list of nodes and returns a graph or a sequence representing a fully connected graph.
    """

    if multigraph:
        graph = nx.MultiGraph() if not directed else nx.MultiDiGraph()
    else:
        graph = nx.Graph() if not directed else nx.DiGraph()

    graph.add_nodes_from(
        [
            (node[0], node_attributes.get(node[0], {}))
            for node in nodes
            if node_attributes
        ]
    )

    sequence = []  # Initialize empty sequence

    for i in range(len(nodes)):
        for j in range(i + 1 if not self_loops else i, len(nodes)):
            if should_connect and should_connect(nodes[i], nodes[j]):
                edge_data = {
                    "weight": calculate_weight(nodes[i], nodes[j])
                    if calculate_weight
                    else None,
                    "edge_attr": edge_attributes.get((nodes[i][0], nodes[j][0]), {})
                    if edge_attributes
                    else {},
                }
                graph.add_edge(nodes[i][0], nodes[j][0], **edge_data)

                if return_sequence:
                    sequence.append(
                        {
                            "start_node": nodes[i][0],
                            "end_node": nodes[j][0],
                            "weight": edge_data["weight"],
                            "node_attr_1": node_attributes.get(nodes[i][0], {})
                            if node_attributes
                            else {},
                            "node_attr_2": node_attributes.get(nodes[j][0], {})
                            if node_attributes
                            else {},
                            "edge_attr": edge_data["edge_attr"],
                        }
                    )

    return sequence if return_sequence else graph
