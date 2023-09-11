from typing import Dict, Tuple, Any, Optional, List, Union
from dlm_matrix.models import ChainTreeIndex, ChainMap, Chain
from dlm_matrix.transformation import Coordinate, CoordinateTree
from dlm_matrix.type import NodeRelationship
from dlm_matrix.representation.base import Representation
from dlm_matrix.representation.estimator import Estimator
from dlm_matrix.embedding.spatial import SpatialSimilarity
from dlm_matrix.visualization.animate import animate_conversation_tree
from collections import defaultdict
import logging

RelationshipDict = Dict[str, Dict[str, Union[str, List[str]]]]
TetraCoordinate = Tuple[float, float, float, float, int]
TetraDict = Dict[str, TetraCoordinate]
StackItem = Tuple[str, TetraCoordinate, int]
Stack = List[StackItem]


class CoordinateRepresentation(Representation):
    RELATIONSHIP_WEIGHTS = {
        "siblings": 1,
        "cousins": 2,
        "uncles_aunts": 3,
        "nephews_nieces": 3,
        "grandparents": 4,
        "ancestors": 5,
        "descendants": 5,
        NodeRelationship.PARENT: 1,
        NodeRelationship.CHILD: 1,
        NodeRelationship.PREVIOUS: 1,
        NodeRelationship.NEXT: 1,
        NodeRelationship.SOURCE: 1,
    }

    def __init__(
        self,
        conversation_tree: ChainTreeIndex,
        spatial_similarity: Optional[SpatialSimilarity] = None,
        message_dict: Optional[Dict[str, Coordinate if Coordinate else Any]] = None,
        conversation_dict: Optional[
            Dict[str, Coordinate if Coordinate else Any]
        ] = None,
    ):
        super().__init__(conversation_tree)
        self.message_dict = (
            self._message_representation() if message_dict is None else message_dict
        )
        self.conversation_dict = (
            self._conversation_representation()
            if conversation_dict is None
            else conversation_dict
        )
        self.estimator = Estimator(self.message_dict, self.conversation_dict)
        self.spatial_similarity = (
            spatial_similarity if spatial_similarity else SpatialSimilarity()
        )

    def prepare_base_document(
        self,
        message_id: str,
        embedding_data: Any,
        coordinate: Coordinate,
        relationship: Dict[str, str],
    ):
        """
        Prepare the base attributes for the ChainDocument.

        Args:
            message_id: The id of the message.
            embedding_data: The embedding data of the message.
            coordinate: The tetrahedron coordinate of the message.
            relationship: The relationships of the message.

        Returns:
            A dictionary containing the base attributes for a ChainDocument.
        """

        return {
            "id": message_id,
            "text": self.get_message_content(message_id),
            "author": self.get_message_author_role(message_id),
            "coordinate": list(coordinate),
            "umap_embeddings": embedding_data[0].tolist(),
            "cluster_label": int(embedding_data[1]),
            "embedding": embedding_data[2][0],
            "n_neighbors": embedding_data[3],
            "relationships": relationship,
            "create_time": self.get_message_create_time(message_id),
        }

    def prepare_children(self, message_id: str, relationship: Dict[str, str]):
        """
        Prepare the children data for the ChainDocument.

        Args:
            message_id: The id of the message.
            relationship: The relationships of the message.

        Returns:
            A list of children in dictionary form.
        """
        children_message = self.get_child_message(message_id)
        children = relationship.get(NodeRelationship.CHILD, [])

        if children_message is None:
            return None

        return [child.dict() for child in children_message] if children else None

    def get_chain_document_parameters(
        self,
        message_id: str,
        embedding_data: Any,
        coordinate: Coordinate,
        relationship: Dict[str, str],
    ):
        """
        Extract the parameters for a ChainDocument from the given inputs.

        Args:
            message_id: The id of the message.
            embedding_data: The embedding data of the message.
            coordinate: The tetrahedron coordinate of the message.
            relationship: The relationships of the message.

        Returns:
            A dictionary containing the parameters for a ChainDocument.
        """
        base_document = self.prepare_base_document(
            message_id, embedding_data, coordinate, relationship
        )

        children_dicts = self.prepare_children(message_id, relationship)

        return {
            **base_document,
            "children": children_dicts if children_dicts is not None else [],
        }

    def create_chain_document(
        self,
        message_id: str,
        embedding_data: Any,
        tetra_dict: TetraDict,
        relationship: Dict[str, str],
    ) -> Chain:
        """
        Create a ChainDocument for a given message id.

        Args:
            message_id: The id of the message.
            embedding_data: The embedding data of the message.
            tetra_dict: The dictionary containing the tetrahedron coordinates.
            relationship: The relationships of the message.
            subgraph: The subgraph of the graph.

        Returns:
            A ChainDocument object for the given message id.
        """
        if message_id not in tetra_dict:
            # skip if message_id is not in tetra_dict
            return None
        chain_document_parameters = self.get_chain_document_parameters(
            message_id, embedding_data, tetra_dict[message_id], relationship
        )
        return chain_document_parameters

    @staticmethod
    def tree_to_tetra_dict(
        tree: CoordinateTree,
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
                logging.warning("Node ID is not set. Skipping this node.")
                continue

            # Validate the coordinates
            if any(
                val is None for val in [node.x, node.y, node.z, node.t, node.n_parts]
            ):
                logging.warning(
                    f"Node {node.id} has None value(s). Ensure all values are valid."
                )
                continue

            # Add to tetra_dict
            tetra_dict[node.id] = (node.x, node.y, node.z, node.t, node.n_parts)

            # Add children to stack
            stack.extend(node.children)

        return tetra_dict

    def tetra_dict_to_tree(
        self,
        root_id: str,
        tetra_dict: TetraDict,
        relationships: RelationshipDict,
        message_dict: Dict[str, Any],
        max_depth: int = 1000,
        **kwargs: Dict[str, Any],
    ) -> "CoordinateTree":
        """
        Builds a CoordinateTree object based on the root node ID, tetrahedral coordinates,
        relationships, and message dictionary.

        Args:
            root_id (str): The ID of the root node.
            tetra_dict (TetraDict): A dictionary that maps node IDs to tetrahedral coordinates.
            relationships (RelationshipDict): A dictionary that describes the relationships between nodes.
            message_dict (Dict[str, Any]): A dictionary that maps node IDs to message information.
            **kwargs (Dict[str, Any]): Additional keyword arguments.

        Returns:
            CoordinateTree: The root of the built CoordinateTree.
        """

        # Get the coordinates and other details from the tetra_dict
        # Initialize the root node
        x, y, z, t, n_parts = tetra_dict[root_id]
        root = CoordinateTree(
            id=root_id,
            x=x,
            y=y,
            z=z,
            t=t,
            n_parts=n_parts,
            message_info=message_dict.get(root_id, None),
            create_time=self.get_message_create_time(root_id),
        )

        def build_tree(node_id: str, node: CoordinateTree, depth: int):
            # Base case: if maximum depth reached, stop the recursion
            if depth > max_depth:
                return

            # Process children and update data structures
            self._process_children(
                node_id, depth, relationships, tetra_dict, [], **kwargs
            )

            # Add processed children to the node
            child_ids = relationships.get(node_id, {}).get(NodeRelationship.CHILD, [])
            for child_id in child_ids:
                x, y, z, t, n_parts = tetra_dict[child_id]
                child = CoordinateTree(
                    id=child_id,
                    x=x,
                    y=y,
                    z=z,
                    t=t,
                    n_parts=n_parts,
                    message_info=message_dict.get(child_id, None),
                    create_time=self.get_message_create_time(child_id),
                )
                node.children.append(child)

                # Recursively build subtree rooted at the child
                build_tree(child_id, child, depth + 1)

        # Start building the tree from the root
        build_tree(root_id, root, depth=0)

        return root

    def _process_children(
        self,
        message_id: str,
        depth: int,
        relationships: RelationshipDict,
        tetra_dict: TetraDict,
        stack: Stack,
        **kwargs: Dict[str, Union[str, float]],
    ) -> None:
        """
        Processes the children of a given message node and updates relevant data structures.

        Args:
            message_id (str): The ID of the message node to process.
            depth (int): The depth of the message node in the tree.
            relationships (Dict): Dictionary mapping message IDs to relationships.
            tetra_dict (Dict): Dictionary mapping message IDs to coordinates.
            stack (List): Stack for depth-first traversal.
            kwargs (Dict): Additional keyword arguments.
        """
        children_ids = list(self.get_children_ids(message_id))
        relationships[message_id][NodeRelationship.CHILD] = children_ids
        sorted_children_ids = self._sort_children_by_time(children_ids)

        for i, child_id in enumerate(sorted_children_ids):
            if child_id not in self.message_dict:
                logging.warning(
                    f"Child ID {child_id} is not in the message dictionary. Removing it from children_ids."
                )
                continue

            try:
                flattened_child_coordinate = self._assign_coordinates(
                    child_id, i, children_ids, depth, **kwargs
                )
            except KeyError as e:
                logging.error(f"KeyError assigning coordinates for {child_id}: {e}")
                continue

            relationships = self._assign_relationships(
                message_id, child_id, children_ids, i, relationships
            )
            tetra_dict[child_id] = flattened_child_coordinate
            stack.append((child_id, flattened_child_coordinate, depth + 1))

    def _create_coordinates_graph(
        self, use_graph: bool = False, **kwargs: Dict[str, Union[str, float]]
    ) -> Dict[str, TetraCoordinate]:
        try:
            (
                relationships,
                get_children_ids,
                tetra_dict,
                root_id,
                root_coordinate,
            ) = self.initialize_representation(use_graph)
            stack = [(root_id, root_coordinate, 1)]

            while stack:
                message_id, parent_coords, depth = stack.pop()
                self._process_children(
                    message_id, depth, relationships, tetra_dict, stack, **kwargs
                )

            coordinate_tree = self.tetra_dict_to_tree(
                root_id, tetra_dict, relationships, self.message_dict, **kwargs
            )

            return tetra_dict, relationships, coordinate_tree

        except Exception as e:
            logging.error(f"Error creating coordinates: {e}")
            return {}, {}

    def _procces_coordnates(
        self,
        use_graph: bool = False,
        local_embedding: bool = True,
        animate: bool = True,
        **kwargs: Dict[str, Union[str, float]],
    ) -> Optional[Union[TetraDict, List[ChainMap]]]:
        (
            embeddings,
            message_ids,
            message_embeddings,
        ) = self.spatial_similarity.generate_embeddings(self.message_dict)

        # Create coordinates and relationships
        tetra_dict, relationships, coordinate_tree = self._create_coordinates_graph(
            use_graph, **kwargs
        )
        if not tetra_dict:
            # skip if no coordinates were created
            return None

        # Animate the conversation tree, if specified
        if animate:
            animate_conversation_tree(
                coordinates=list(tetra_dict.values()),
            )

        # Update the coordinates with local embeddings, if specified
        if local_embedding:
            # Generate local embeddings for messages
            message_embeddings = self.spatial_similarity.generate_message_embeddings(
                self.estimator,
                self.message_dict,
                embeddings,
                message_ids,
                message_embeddings,
            )

            # Update representation with local embeddings
            updated_tree_doc = self._construct_representation(
                message_embeddings,
                tetra_dict,
                relationships,
            )
            return updated_tree_doc, embeddings, coordinate_tree.dict()
        else:
            return coordinate_tree

    def _construct_representation(
        self,
        message_embeddings: Dict[str, Any],
        tetra_dict: TetraDict,
        relationships: RelationshipDict,
    ) -> List[Chain]:
        # Create a defaultdict to avoid KeyError exceptions
        safe_relationships = defaultdict(lambda: {}, relationships)

        # Create a list to store the ChainDocuments
        chain_documents = []

        # Iterate over each message in the conversation
        for message_id, embedding_data in message_embeddings.items():
            # Add a node for each message

            # Extract and merge relationships
            relationship = safe_relationships[message_id]

            #  Add the node to the graph
            chain_document = self.create_chain_document(
                message_id,
                embedding_data,
                tetra_dict,
                relationship,
            )

            chain_documents.append(chain_document)

        return chain_documents
