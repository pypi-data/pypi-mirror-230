from typing import List, Tuple, Optional, Dict, Any, Type
from dlm_matrix.chaintrees.interface import IChainFactory, IChainTree
from dlm_matrix.models import Content
from dlm_matrix.transformation import Coordinate
import weakref
from abc import ABC, abstractmethod
import hashlib


class SHA256SignatureScheme:
    def generate_signature(self, content_node: Any) -> str:
        return hashlib.sha256(str(content_node).encode()).hexdigest()


class ChainNode:
    """
    Represents a node in the ChainTree data structure.
    Each node is characterized by a key-value pair and linked to its parent and children nodes.
    """

    def __init__(self, key: str, value: int) -> None:
        self.key = key
        self.value = value
        self.parent: ChainNode = None
        self.children: List[ChainNode] = []

    def add_child(self, child_node: "ChainNode") -> None:
        child_node.parent = self
        self.children.append(child_node)

    def remove_child(self, child_node: "ChainNode") -> None:
        child_node.parent = None
        self.children.remove(child_node)

    def __str__(self):
        return f"Node(id={self.key}, value={self.value})"


class ChainComposite(ChainNode):
    lookup_table = (
        weakref.WeakValueDictionary()
    )  # Use a weak value dictionary to store nodes by their hashes

    def __init__(self, key: Optional[Type] = None, value: Optional[Type] = None):
        super().__init__()
        self.key = key
        self.value = value
        self.id = self._hash_node(self)
        self.left = None
        self.right = None

    def add_child(self, child: ChainNode):
        if child == self:
            raise ValueError("Cannot add the node as its own child.")
        if child in self.children:
            raise ValueError(f"Child with id '{child.id}' is already added.")
        child.id = self._hash_node(child)
        self.children.append(child)
        self.lookup_table[child.id] = child
        print(f"Added child with id '{child}' to node with id '{self}'.")

    def remove_child(self, child: ChainNode):
        if child not in self.children:
            raise ValueError(f"Child with id '{child.id}' not found.")
        del self.lookup_table[child.id]
        self.children.remove(child)

    def _hash_node(self, node: ChainNode) -> str:
        signature_scheme = SHA256SignatureScheme()
        return signature_scheme.generate_signature(node)

    def get_child_by_hash(self, node_hash: str) -> Optional[ChainNode]:
        return self.lookup_table.get(node_hash)

    def get_parent_by_hash(self, node_hash: str) -> Optional[ChainNode]:
        for node in self.lookup_table.values():
            if isinstance(node, ChainComposite) and any(
                child.id == node_hash for child in node.children
            ):
                return node
        return None

    def get_node_by_hash(self, content_hash: str) -> Optional[ChainNode]:
        return self.lookup_table.get(content_hash)

    def get_child_by_key(self, key: str) -> ChainNode:
        for child in self.children:
            if child.key == key:
                return child
        raise ValueError(f"Child with key '{key}' not found.")

    def get_child_by_value(self, value: Any) -> ChainNode:
        for child in self.children:
            if child.value == value:
                return child
        raise ValueError(f"Child with value '{value}' not found.")

    def clear_children(self):
        self.children.clear()
        self.lookup_table.clear()

    def accept(self, visitor):
        visitor.visit_composite(self)

    def max_children(self) -> int:
        return 2

    def get_ancestors(self) -> List[ChainNode]:
        ancestors = []
        if not self.parent:
            return ancestors
        ancestors.append(self.parent)
        if isinstance(self.parent, ChainComposite):
            ancestors.extend(self.parent.get_ancestors())
        return ancestors

    def get_descendants(self) -> List[ChainNode]:
        descendants = []
        for child in self.children:
            descendants.append(child)
            if isinstance(child, ChainComposite):
                descendants.extend(child.get_descendants())
        return descendants


class ChainLink:
    """
    Represents a chain in the ChainTree data structure.
    Each chain is rooted at a node with a specific key and contains all nodes whose key is a prefix of that key.
    """

    def __init__(self, root_node: ChainNode) -> None:
        self.root = root_node


class ChainTreeLink(IChainTree):
    """
    Represents a ChainTree data structure.
    """

    def __init__(
        self,
        chain_factory: IChainFactory,
        allow_duplicates: bool = False,
    ):
        self.chain_factory = chain_factory
        self.allow_duplicates = allow_duplicates
        self.chains_links = {}
        self.chains = []
        self.nodes = []

    def add_chain(
        self,
        chain_type: str,
        id: str,
        content: Content,
        coordinate: Coordinate,
        parent: Optional[str] = None,
    ) -> None:
        """
        Adds a chain to the ChainTree.
        """
        if not self.allow_duplicates and id in self.chains:
            raise ValueError(f"Duplicate id {id} found in sequence.")

        chain = self.chain_factory.create_chain(
            chain_type, id, content, coordinate, parent
        )
        self.chains.append(chain)

        # Add the chain to the chain with the same id
        if id not in self.chains_links:
            self.chains_links[id] = ChainLink(chain)
        else:
            self.chains_links[id].root.add_child(chain)

        # Add the chain to the chains with ids that are prefixes of the chain's id
        for i in range(1, len(id)):
            prefix = id[:i]
            if prefix not in self.chains_links:
                self.chains_links[prefix] = ChainLink(chain)
            else:
                self.chains_links[prefix].root.add_child(chain)

    def update_chain(
        self,
        id: str,
        new_content: Optional[Content] = None,
        new_coordinate: Optional[Coordinate] = None,
        new_metadata: Optional[Dict[str, Any]] = None,
    ):
        for chain in self.chains:
            if chain.id == id:
                if new_content is not None:
                    chain.content = new_content
                if new_coordinate is not None:
                    chain.coordinate = new_coordinate
                if new_metadata is not None:
                    chain.metadata = new_metadata
                break

    def add_node(self, key: str, value: int) -> None:
        """
        Adds a node to the ChainTree.
        """
        if not self.allow_duplicates and key in self.chains:
            raise ValueError(f"Duplicate key {key} found in sequence.")

        node = ChainNode(key, value)
        self.nodes.append(node)

        # Add the node to the chain with the same key
        if key not in self.chains_links:
            self.chains_links[key] = ChainLink(node)
        else:
            self.chains_links[key].root.add_child(node)

        # Add the node to the chains with keys that are prefixes of the node's key
        for i in range(1, len(key)):
            prefix = key[:i]
            if prefix not in self.chains_links:
                self.chains_links[prefix] = ChainLink(node)
            else:
                self.chains_links[prefix].root.add_child(node)

    def remove_node(self, key: str) -> None:
        """
        Removes a node from the ChainTree.
        """
        node_to_remove = None
        for node in self.nodes:
            if node.key == key:
                node_to_remove = node
                break

        if node_to_remove is None:
            raise ValueError(f"Node with key {key} not found.")

        # Remove the node from the chains with keys that are prefixes of the node's key
        for i in range(len(key)):
            prefix = key[:i]
            if prefix in self.chains_links:
                self.chains_links[prefix].root.remove_child(node_to_remove)

        self.nodes.remove(node_to_remove)

    def get_chains_by_coordinate(self, coordinate: Coordinate):
        return [chain for chain in self.chains if chain.coordinate == coordinate]

    def get_chains(self):
        return self.chains

    def get_chain(self, id: str):
        for chain in self.chains:
            if chain.id == id:
                return chain
        return None

    def get_last_chain(self):
        return self.chains[-1]

    def get_chains_by_type(self, chain_type: str):
        return [
            chain for chain in self.chains if isinstance or chain.entity == chain_type
        ]

    def remove_chain(self, id: str):
        self.chains = [chain for chain in self.chains if chain.id != id]

    def add_nodes(self, nodes: List[Tuple[str, int]]) -> None:
        """
        Adds multiple nodes to the ChainTree.
        """
        for node in nodes:
            self.add_node(node[0], node[1])

    def remove_nodes(self, keys: List[str]) -> None:
        """
        Removes multiple nodes from the ChainTree.
        """
        for key in keys:
            self.remove_node(key)

    def get_nodes(self) -> List[ChainNode]:
        """
        Gets all nodes from the ChainTree.
        """
        return self.nodes

    def get_node(self, key: str) -> ChainNode:
        """
        Gets a node from the ChainTree.
        """
        if key not in self.chains_links:
            raise ValueError(f"Key {key} not found in sequence.")

        return self.chains_links[key].root

    def _traverse(self, node: ChainNode, indent: str = "") -> List[str]:
        """
        Helper method for __str__ that recursively traverses the ChainTree and generates a list of strings
        representing the nodes and their relationships in the tree.
        """
        lines = [f"{indent}{node.key}: {node.value}"]
        for child in node.children:
            lines.extend(self._traverse(child, indent + "  "))
        return lines

    def _traverse_chain(self, node: ChainNode, visited: set) -> List[Tuple[str, str]]:
        """
        Helper method for create_partial_sequence_as_simplicial_complex that recursively traverses the ChainTree
        and generates a list of tuples representing the simplicial complex.
        """
        simplicial_complex = []
        for child in node.children:
            simplicial_complex.append((node.key, child.key))
            simplicial_complex.extend(self._traverse_chain(child, visited))
        return simplicial_complex
