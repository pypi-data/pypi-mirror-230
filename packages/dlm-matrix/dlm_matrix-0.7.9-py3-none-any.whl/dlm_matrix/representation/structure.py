from typing import Any, Dict, List, Tuple
from dlm_matrix.models import ChainTreeIndex
from dlm_matrix.relationship import ChainRelationships
import pandas as pd
import networkx as nx


class HierarchyRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, Any]:
        """
        Creates a dictionary representation of the conversation tree.
        The dictionary has the following structure:

        [
         <parent id>: {
            <children>: {
                "child_id": {
                    "message": <message content>,
                    "children": [<child id>, ...]
                    },
                ...
            },
            ...
        }]
        """
        rep_hierarchy = {}
        for node in self.mapping.values():
            if node.parent is None:
                rep_hierarchy[node.id] = self._create_node_representation(node)
        return rep_hierarchy

    def _create_node_representation(self, node) -> Dict[str, Any]:
        """
        Creates a dictionary representation of a node in the conversation tree.
        The dictionary has the following structure:

        {
            "message": <message content>,
            "children": [<child id>, ...]
        }
        """
        children = {}
        for child in node.children:
            children[child.id] = self._create_node_representation(child)
        return {"message": node.message.content, "children": children}


class ListRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, Any]:
        """
        Creates a dictionary representation of the conversation tree.
        The dictionary has the following structure:

        [
            {
                "id": <message id>,
                "message": <message content>,
                "children": [<child id>, ...]
            },
            ...
        ]
        """
        rep_list = []
        for node in self.mapping.values():
            children_ids = [child for child in node]
            message = self.message_dict.get(node.id)
            content = message.content.parts if message is not None else ""
            rep_list.append(
                {"id": node.id, "message": content, "children": children_ids}
            )
        return rep_list


class GraphRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, Any]:
        """
        Creates a dictionary representation of the conversation tree.
        The dictionary has the following structure:

        {
            <parent id>: [<child id>, ...],
            ...
        }
        """
        rep_graph = {}
        for node in self.mapping.values():
            rep_graph[node.id] = [child for child in node.children]
        return rep_graph


class SimpleAdjacencyListRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, List[str]]:
        adjacency_list = {}
        for mapping in self.mapping.values():
            adjacency_list[mapping.id] = [child for child in mapping.children]
        return adjacency_list


class DetailedAdjacencyListRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, Dict[str, Any]]:
        """
        Creates a representation of the conversation tree as an adjacency list.
        """
        adjacency_list = {}
        for message in self.mapping.values():
            adjacency_list[message.id] = {
                "parent": message.parent,
                "children": message.children,
            }
        return adjacency_list


class DetailedEdgeRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, Dict[str, Any]]:
        """
        Creates a dictionary representation of the conversation tree.
        The dictionary has the following structure:
        {
            "edges": [
                {
                    "source": <source vertex id>,
                    "target": <target vertex id>
                },
                ...
            ]
        }
        """
        edges = []
        for message in self.mapping.values():
            if message.parent is not None:
                edge = {"source": message.parent, "target": message.id}
                edges.append(edge)
        return {"edges": edges}


class VertexRepresentation(ChainRelationships):
    def create_representation(self) -> List[str]:
        return list(self.mapping.keys())


class AdjacencyMatrixRepresentation(ChainRelationships):
    def create_representation(self) -> pd.DataFrame:
        message_ids = [message_id for message_id in self.mapping.keys()]
        adjacency_matrix = pd.DataFrame(0, index=message_ids, columns=message_ids)

        for message_id, mapping in self.mapping.items():
            for child in mapping.children:
                adjacency_matrix.at[message_id, child] = 1

        return adjacency_matrix


class ChildParentRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, str]:
        """
        Creates a dictionary representation where each child id is mapped to its parent id.
        This representation will be helpful to quickly lookup the parent of any message.

        Returns:
            children (Dict[str, str]): The dictionary mapping each child id to its parent id.
        """
        children = {}
        for message in self.mapping.values():
            for child in message.children:
                children[child] = message.id
        return children


class RootChildRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, List[str]]:
        """
        Creates a dictionary representation where the root id maps to all the leaf nodes.
        This representation can be useful to get all leaf nodes from the root.

        Returns:
            root_child (Dict[str, List[str]]): The dictionary mapping the root id to all the leaf nodes.
        """
        root_child = {}
        for message in self.mapping.values():
            if message.parent is None:  # this is the root node
                root_child[message.id] = self._find_leaf_nodes(message)
        return root_child

    def _find_leaf_nodes(self, node) -> List[str]:
        leaf_nodes = []
        for child_id in node.children:
            child_node = self.mapping[child_id]
            if child_node.children:
                leaf_nodes.extend(self._find_leaf_nodes(child_node))
            else:
                leaf_nodes.append(child_id)
        return leaf_nodes


class ThreadRepresentation(ChainRelationships):
    def create_representation(self) -> List[List[Dict[str, Any]]]:
        """
        Creates a list representation of the conversation tree, where each entry is a list representing a thread.

        [
            [  # Thread 1
                {  # Document 1
                    "text": <text content>,
                    "extra_info": <extra_info>,
                    "relationships": {
                        "parent": <parent id>,
                        "children": [<child id>, ...],
                        "previous": <previous id>,
                        "next": <next id>,
                    },
                },
                ...  # More documents in thread 1
            ],
            ...  # More threads
        ]
        """

        threads = []

        # A helper function to construct a document dictionary
        def _create_document(node):
            text = node.message.content
            extra_info = (
                node.message.extra_info
            )  # Assuming 'extra_info' field in the Message object
            parent_id = node.parent.id if node.parent else None
            children_ids = [child.id for child in node.children]
            previous_id = node.previous.id if node.previous else None
            next_id = node.next.id if node.next else None
            document = {
                "text": text,
                "extra_info": extra_info,
                "relationships": {
                    "parent": parent_id,
                    "children": children_ids,
                    "previous": previous_id,
                    "next": next_id,
                },
            }

            return document

        # A helper function to traverse the conversation tree and construct threads
        def _traverse_tree(node, current_thread):
            current_thread.append(_create_document(node))
            for child in node.children:
                _traverse_tree(child, current_thread)

        # Start the traversal
        for node in self.mapping.values():
            if node.parent is None:  # It's a root node, start a new thread
                current_thread = []
                _traverse_tree(node, current_thread)
                threads.append(current_thread)

        return threads


class SequentialMessagesWithAuthors(ChainRelationships):
    def create_representation(self) -> List[Dict[str, Any]]:
        sequential_messages = []

        for node in self.mapping.values():
            if node.parent is None:
                self._traverse_tree(node.id, sequential_messages)

        return sequential_messages

    def _traverse_tree(self, node_id: str, sequential_messages: List[Dict[str, Any]]):
        node = self.mapping[node_id]
        sequential_messages.append(
            {"message": node.message.content, "author": node.message.author}
        )

        for child in node.children:
            self._traverse_tree(child, sequential_messages)


class RepresentationFactory(ChainRelationships):
    def create_representation(
        self, representation_type: str, message_dict: dict, mapping: dict
    ) -> ChainRelationships:
        """
        Create a Representation object based on the representation_type parameter.

        Parameters
        ----------
        representation_type : str
            The type of representation to create. Must be one of: "hierarchy", "list", "sequential".

        message_dict : dict
            Dictionary that maps message id to the corresponding Message object.

        mapping : dict
            Dictionary that maps node id to the corresponding Node object.

        Returns
        -------
        Representation
            The created Representation object.
        """

        if representation_type == "hierarchy":
            return HierarchyRepresentation(message_dict, mapping)
        elif representation_type == "list":
            return ListRepresentation(message_dict, mapping)
        elif representation_type == "sequential":
            return SequentialMessagesRepresentation(message_dict, mapping)
        elif representation_type == "thread":
            return ThreadRepresentation(message_dict, mapping)
        else:
            raise ValueError(
                f"Representation type {representation_type} not supported."
            )


class SequentialMessagesRepresentation(ChainRelationships):
    def create_representation(self) -> List[Tuple[str, str]]:
        """
        Creates a sequential representation of the conversation tree.
        The  representation has the following structure:
        [
            {
                "message": <message content>,
                "author": <message author>
            },
            ...
        ]

        """

        message_list = []

        def _traverse_sequentially(node_id: str):
            node = self.mapping[node_id]
            message_list.append((node.message.content, node.message.author))
            for child in node.children:
                _traverse_sequentially(child.id)

        for node in self.mapping.values():
            if node.parent is None:
                _traverse_sequentially(node.id)

        return message_list


class NestedDictRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, Any]:
        nested_dict = {}
        for node in self.mapping.values():
            if node.parent is None:
                nested_dict[node.id] = self._build_nested_dict(node.id)
        return nested_dict

    def _build_nested_dict(self, node_id: str) -> Dict[str, Any]:
        node = self.mapping[node_id]
        children = [self._build_nested_dict(child.id) for child in node.children]
        return {node.id: {"message": node.message, "children": children}}


class ConversationAsDataFrame(ChainRelationships):
    def create_representation(self) -> pd.DataFrame:
        data = []
        for message in self.mapping.values():
            data.append(message.message.dict())

        return pd.DataFrame(data)


class MessageAttributesRepresentation(ChainRelationships):
    def __init__(self, conversation_tree: ChainTreeIndex, attributes: List[str]):
        super().__init__(conversation_tree)
        self.attributes = attributes

    def create_representation(self) -> Dict[str, Dict[str, Any]]:
        message_attributes = {}
        for message in self.mapping.values():
            message_attributes[message.id] = {
                attr: getattr(message.message, attr) for attr in self.attributes
            }
        return message_attributes


class ConversationGraphRepresentation(GraphRepresentation):
    def create_representation(self) -> nx.DiGraph:
        graph = super().create_representation()

        # Additional process to link assistant and user messages
        # Assume we have "system", "user", and "assistant" roles
        user_assistant_nodes = [
            node
            for node, data in graph.nodes(data=True)
            if data.get("role") in {"user", "assistant"}
        ]

        for i in range(len(user_assistant_nodes) - 1):
            graph.add_edge(user_assistant_nodes[i], user_assistant_nodes[i + 1])

        return graph


class DepthRepresentation(ChainRelationships):
    def create_representation(self) -> Dict[str, int]:
        """
        Creates a dictionary representation where each node id is mapped to its depth in the conversation tree.
        This representation will be helpful to understand the depth of any message in the conversation.

        Returns:
            depth_dict (Dict[str, int]): The dictionary mapping each node id to its depth in the conversation.
        """
        depth_dict = {}
        for message in self.mapping.values():
            if message.parent is None:  # this is the root node
                depth_dict[message.id] = 0
                self._compute_depth(message, 0, depth_dict)
        return depth_dict

    def _compute_depth(self, node, current_depth, depth_dict) -> None:
        for child_id in node.children:
            child_node = self.mapping[child_id]
            depth_dict[child_id] = current_depth + 1
            self._compute_depth(child_node, current_depth + 1, depth_dict)
