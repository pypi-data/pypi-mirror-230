from typing import Callable, List, Optional, Tuple
from dlm_matrix.transformation.tree import CoordinateTree
from dlm_matrix.transformation.coordinate import Coordinate
from dlm_matrix.embedding.spatial import SpatialSimilarity
from heapq import heappush, heappop
import numpy as np


class CoordinateTreeTraverser:
    def __init__(self, tree: CoordinateTree):
        self.tree = tree

    def traverse_depth_first(
        self, predicate: Callable[[Coordinate], bool]
    ) -> Coordinate:
        return CoordinateTree.depth_first_search(self.tree, predicate)

    def traverse_breadth_first(
        self, predicate: Callable[[Coordinate], bool]
    ) -> Coordinate:
        return CoordinateTree.breadth_first_search(self.tree, predicate)

    def traverse_depth_first_all(
        self, predicate: Callable[[Coordinate], bool]
    ) -> List[Coordinate]:
        return CoordinateTree.depth_first_search_all(self.tree, predicate)

    def traverse_similarity(
        self,
        target_sentence: str,
        fast_predicate: Optional[Callable[[Coordinate], bool]] = None,
        top_k: int = 1,
        keyword: Optional[str] = None,
    ) -> List[Tuple[Coordinate, float]]:
        most_similar_nodes = (
            []
        )  # This will hold (negative_cosine_similarity, node) pairs

        target_embedding = SpatialSimilarity().encode_texts([target_sentence])[0]

        # If a fast_predicate is provided, use it to narrow down the search space.
        candidate_nodes = (
            self.traverse_depth_first(fast_predicate)
            if fast_predicate
            else self.traverse_depth_first_all(lambda x: True)
        )

        # Convert target_embedding to a unit vector if it isn't already
        target_norm = np.linalg.norm(target_embedding)
        if target_norm > 0:
            target_unit_vector = target_embedding / target_norm
        else:
            target_unit_vector = target_embedding

        for node in candidate_nodes:
            # If keyword filtering is enabled, skip nodes that don't contain the keyword
            if (
                keyword
                and keyword.lower() not in node.message_info.message.content.text.lower()
            ):
                continue

            node_embedding = (
                node.message_info.message.embedding
            )  # Assuming embeddings are stored here

            # Convert node_embedding to a unit vector if it isn't already
            node_norm = np.linalg.norm(node_embedding)
            if node_norm > 0:
                node_unit_vector = node_embedding / node_norm
            else:
                node_unit_vector = node_embedding

            # Compute cosine similarity
            cosine_sim = np.dot(target_unit_vector, node_unit_vector)

            # Negate cosine similarity because heapq is a min-heap and we want max similarity
            heappush(most_similar_nodes, (-cosine_sim, node))

            # If heap is too big, remove smallest
            if len(most_similar_nodes) > top_k:
                heappop(most_similar_nodes)

        # Extract nodes and actual similarity scores, and sort by similarity
        return [
            (node, -neg_cosine_sim)
            for neg_cosine_sim, node in sorted(most_similar_nodes, reverse=True)
        ]
    