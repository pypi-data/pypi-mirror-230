from typing import Dict, Tuple, Any, List, Union, Optional
from dlm_matrix.representation.compute import CoordinateRepresentation
from dlm_matrix.transformation import Coordinate
import itertools
import collections
import networkx as nx
import pandas as pd


class ChainRepresentation(CoordinateRepresentation):
    def extract_coordinates(
        self, coordinate: Coordinate
    ) -> Optional[List[Union[int, float]]]:
        """
        Extract x, y, z, t, and n_parts from the coordinate object and return them as a list.

        Parameters:
        - coordinate (Optional[object]): The coordinate object containing spatial information.

        Returns:
        - Optional[List[Union[int, float]]]: A list containing the extracted coordinates, or None if coordinate is None.
        """
        if coordinate is None:
            return None

        try:
            return [
                coordinate.x,
                coordinate.y,
                coordinate.z,
                coordinate.t,
                coordinate.n_parts,
            ]
        except AttributeError as e:
            print(f"AttributeError encountered: {e}")
            return None

    def collect_messages(
        self,
    ) -> Tuple[
        List[str],
        List[str],
        List[str],
        List[str],
        List[str],
        List[List[Union[int, float]]],
        List[List[Union[int, float]]],
        List[List[float]],
        List[List[float]],
    ]:
        """
        Collects messages and their corresponding details.

        Returns:
        - Tuple: A tuple containing lists for prompts, responses, prompt_ids, response_ids, created_times, prompt_coordinates, response_coordinates, prompt_encodings, and response_encodings.
        """
        prompts, responses, prompt_ids, response_ids = [], [], [], []
        created_times, prompt_coordinates, response_coordinates = [], [], []
        prompt_encodings, response_encodings = [], []

        for message_id, _ in self.message_dict.items():
            if self.is_message_valid(message_id):
                author = self.get_message_author_role(message_id)
                children = self.conversation_dict.get(message_id, [None, []])[1]

                for child_id in children:
                    if self.is_message_pair_valid(message_id, child_id, author):
                        self.append_message_details(
                            message_id,
                            child_id,
                            prompts,
                            responses,
                            prompt_ids,
                            response_ids,
                            created_times,
                            prompt_coordinates,
                            response_coordinates,
                            prompt_encodings,
                            response_encodings,
                        )

        return (
            prompts,
            responses,
            prompt_ids,
            response_ids,
            created_times,
            prompt_coordinates,
            response_coordinates,
            prompt_encodings,
            response_encodings,
        )

    def is_message_valid(self, message_id: str) -> bool:
        """
        Checks if a message is valid based on various attributes.

        Parameters:
        - message_id (str): The ID of the message to check.

        Returns:
        - bool: True if the message is valid, otherwise False.
        """
        return all(
            [
                self.get_message_content(message_id) is not None,
                self.get_message_create_time(message_id) is not None,
                self.get_message_coordinate(message_id) is not None,
                self.get_message_author_role(message_id) is not None,
            ]
        )

    def is_message_pair_valid(
        self, parent_id: str, child_id: str, parent_author: str
    ) -> bool:
        """
        Checks if a parent-child message pair is valid.

        Parameters:
        - parent_id (str): The ID of the parent message.
        - child_id (str): The ID of the child message.
        - parent_author (str): The author role of the parent message.

        Returns:
        - bool: True if the message pair is valid, otherwise False.
        """
        child_author = self.get_message_author_role(child_id)
        return (
            child_author is not None
            and parent_author == "user"
            and child_author == "assistant"
        )

    def append_message_details(
        self,
        parent_id: str,
        child_id: str,
        prompts: List[str],
        responses: List[str],
        prompt_ids: List[str],
        response_ids: List[str],
        created_times: List[str],
        prompt_coordinates: List[Optional[List[Union[int, float]]]],
        response_coordinates: List[Optional[List[Union[int, float]]]],
        prompt_encodings: List[List[float]],
        response_encodings: List[List[float]],
    ) -> None:
        """
        Appends the details of a valid message pair to various lists.

        Parameters:
        - parent_id (str): The ID of the parent message.
        - child_id (str): The ID of the child message.
        - prompts (List[str]): List of prompts.
        - responses (List[str]): List of responses.
        - ... (Other lists for storing message details)

        Returns:
        - None
        """

        # Append message contents, ids, and created_times
        prompts.append(self.get_message_content(parent_id))
        responses.append(self.get_message_content(child_id))
        prompt_ids.append(parent_id)
        response_ids.append(child_id)
        created_times.append(self.get_message_create_time(parent_id))

        # Append coordinates if they exist, otherwise skip
        prompt_coord = self.extract_coordinates(self.get_message_coordinate(parent_id))
        if prompt_coord is not None:
            prompt_coordinates.append(prompt_coord)

        response_coord = self.extract_coordinates(self.get_message_coordinate(child_id))
        if response_coord is not None:
            response_coordinates.append(response_coord)

        # Append encodings
        prompt_encodings.append(
            list(map(float, self.message_dict[parent_id].message.embedding))
        )
        response_encodings.append(
            list(map(float, self.message_dict[child_id].message.embedding))
        )

    def encode_texts(
        self,
        prompts: List[str],
        responses: List[str],
    ) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Encodes the texts using either the SentenceTransformer model or the OpenAI API.

        Parameters:
        - prompts (List[str]): List of prompts.
        - responses (List[str]): List of responses.

        Returns:
        - Tuple: A tuple containing lists of encoded prompts and responses.
        """

        # First, find all the unique texts across both prompts and responses
        unique_texts = list(
            collections.OrderedDict.fromkeys(prompts + responses).keys()
        )

        # Encode these unique texts
        all_encoded_texts = self.spatial_similarity._embed_text_batch(unique_texts)

        # Create a mapping from text to encoding
        encoding_lookup = dict(zip(unique_texts, all_encoded_texts))

        # Now populate the return lists, re-using the unique encodings where possible
        encoded_prompts = [list(map(float, encoding_lookup[p])) for p in prompts]
        encoded_responses = [list(map(float, encoding_lookup[r])) for r in responses]

        return encoded_prompts, encoded_responses

    def create_prompt_response_df(
        self, pre_computed_embeddings: bool = True
    ) -> pd.DataFrame:
        """
        Creates a DataFrame capturing the relationship between prompts and responses.

        Parameters:
        - pre_computed_embeddings (bool, optional): Whether to use pre-computed embeddings. Default is False.

        Returns:
        - pd.DataFrame: A DataFrame containing the relationship data.
        """
        (
            prompts,
            responses,
            prompt_ids,
            response_ids,
            created_times,
            prompt_coordinates,
            response_coordinates,
            prompt_encodings,
            response_encodings,
        ) = self.collect_messages()

        if not pre_computed_embeddings:
            prompt_encodings, response_encodings = self.encode_texts(prompts, responses)

        relationship_df = pd.DataFrame(
            {
                "prompt_id": prompt_ids,
                "response_id": response_ids,
                "prompt": prompts,
                "response": responses,
                "prompt_embedding": prompt_encodings,
                "response_embedding": response_encodings,
                "created_time": created_times,
                "prompt_coordinate": prompt_coordinates,
                "response_coordinate": response_coordinates,
            }
        )

        return relationship_df

    def create_chain_representation(
        self,
        message_id_1: str,
        operation: str = None,
        message_id_2: str = None,
        n: int = None,
        return_message_info: bool = False,
        return_df: bool = False,
        return_dict: bool = False,
    ) -> Any:
        # Define the operation dictionary mapping operation strings to functions
        operation_dict = {
            "bifurcation_points": self.get_bifurcation_points,
            "merge_points": self.get_merge_points,
            "cross_references": self.get_commonly_co_referenced_messages,
            "commonly_co_referenced": self.get_co_reference_chain_between_messages,
            "relationships_between": self.get_all_relationships_between_messages,
        }

        # Validate the operation
        if operation not in operation_dict:
            raise ValueError(
                f"Invalid operation. Valid operations are: {list(operation_dict.keys())}"
            )

        # Validate the message IDs
        if message_id_1 not in self.message_dict:
            raise ValueError("Invalid message_id_1")

        if message_id_2 is not None and message_id_2 not in self.message_dict:
            raise ValueError("Invalid message_id_2")

        # Validate the number of hops
        if n is not None and not isinstance(n, int):
            raise ValueError("n must be an int")

        # Validate the return type
        if not isinstance(return_message_info, bool):
            raise ValueError("return_message_info must be a boolean")

        if not isinstance(return_df, bool):
            raise ValueError("return_df must be a boolean")

        if not isinstance(return_dict, bool):
            raise ValueError("return_dict must be a boolean")

        # Perform the operation
        if operation == "relationships_between":
            result = operation_dict[operation](
                message_id_1, message_id_2, return_message_info=return_message_info
            )

        elif operation == "commonly_co_referenced":
            result = operation_dict[operation](
                message_id_1, message_id_2, n, return_message_info=return_message_info
            )

        else:
            result = operation_dict[operation](
                message_id_1, n, return_message_info=return_message_info
            )

        # Format the result
        if return_message_info:
            result = [self.message_dict[message_id] for message_id in result]

        if return_df:
            result = pd.DataFrame(result)

        if return_dict:
            result = {
                message_id: self.message_dict[message_id] for message_id in result
            }

        return result

    def _fallback_method(self, message_id: str) -> List[str]:
        """A simple fallback method that returns all neighboring messages in case the main operation fails"""
        return self.conversation_dict[message_id][1]

    def _find_path_or_chain(
        self, message_id_1: str, message_id_2: str
    ) -> Optional[List[str]]:
        """Finds a path within a certain hop range or a connecting chain between two messages."""
        paths_within_hop_range = self._get_paths_within_hop_range(
            message_id_1, message_id_2, 2
        )
        if paths_within_hop_range:
            return paths_within_hop_range[0]  # Use the first path within the hop range
        else:
            return self._find_connecting_chain(message_id_1, message_id_2)

    def _find_connecting_chain(self, message_id_1: str, message_id_2: str) -> List[str]:
        """
        Returns a chain of messages that connect the two given messages.

        Args:
            message_id_1: The ID of the first message.
            message_id_2: The ID of the second message.

        Returns:
            A list of message IDs forming the connecting chain.
        """
        if (
            message_id_1 not in self.message_dict
            or message_id_2 not in self.message_dict
        ):
            raise ValueError("Both message IDs must exist in the conversation")

        # Get the set of messages reachable from message_id_1 and the set of messages that can reach message_id_2
        reachable_from_1 = set(nx.descendants(self._get_message_tree(), message_id_1))
        can_reach_2 = set(nx.ancestors(self._get_message_tree(), message_id_2))

        # Find the intersection of the two sets
        common_messages = reachable_from_1 & can_reach_2

        # If no common message is found, there is no connecting chain
        if not common_messages:
            return []

        # Select a message from the common messages that minimizes the total distance of the chain
        connecting_message = min(
            common_messages,
            key=lambda node: nx.shortest_path_length(
                self._get_message_tree(), message_id_1, node
            )
            + nx.shortest_path_length(self._get_message_tree(), node, message_id_2),
        )

        # Get the paths from message_id_1 to the connecting message and from the connecting message to message_id_2
        path_to_connecting = nx.shortest_path(
            self._get_message_tree(), message_id_1, connecting_message
        )
        path_from_connecting = nx.shortest_path(
            self._get_message_tree(), connecting_message, message_id_2
        )

        # Return the concatenation of the two paths, excluding the connecting message in one of them to avoid duplication
        return path_to_connecting + path_from_connecting[1:]

    def _get_paths_within_hop_range(
        self,
        message_id_1: str,
        message_id_2: str,
        hop_range: Union[int, Tuple[int, int]],
        return_message_info: bool = False,
    ) -> Union[List[List[Union[str, Dict[str, Any]]]], None]:
        """
        Returns a list of all paths between two messages within a range of
        number of steps, or None if no path exists within the given range.

        If return_message_info is True, returns information about the messages
        in the path instead of just the IDs.
        """

        # Validation
        if not isinstance(hop_range, (int, tuple)) or (
            isinstance(hop_range, tuple)
            and not len(hop_range) == 2
            and isinstance(hop_range[0], int)
            and isinstance(hop_range[1], int)
        ):
            raise ValueError("hop_range must be an int or a tuple of two ints.")

        if (
            message_id_1 not in self.message_dict
            or message_id_2 not in self.message_dict
        ):
            raise ValueError(
                "Both message_id_1 and message_id_2 must be valid message IDs."
            )

        if isinstance(hop_range, int):
            hop_range = (hop_range, hop_range)

        # Optimization: use a dictionary to store n-hop neighbors
        neighbor_cache_1 = {}
        neighbor_cache_2 = {}

        paths = []
        for hops in range(hop_range[0], hop_range[1] + 1):
            # Compute and cache n-hop neighbors if they haven't been computed yet
            if hops not in neighbor_cache_1:
                neighbor_cache_1[hops] = self._get_n_hop_neighbors(message_id_1, hops)
            if hops not in neighbor_cache_2:
                neighbor_cache_2[hops] = self._get_n_hop_neighbors(message_id_2, hops)

            # Find the intersection of the two sets of neighbors
            common_neighbors = list(
                set(neighbor_cache_1[hops]) & set(neighbor_cache_2[hops])
            )

            # For each common neighbor, get all paths from message_id_1 to the neighbor
            # and all paths from the neighbor to message_id_2, then combine them to
            # create a path from message_id_1 to message_id_2
            for neighbor in common_neighbors:
                paths_1 = nx.all_simple_paths(
                    self._get_message_tree(), message_id_1, neighbor, cutoff=hops
                )
                paths_2 = nx.all_simple_paths(
                    self._get_message_tree(), neighbor, message_id_2, cutoff=hops
                )
                for path_1 in paths_1:
                    for path_2 in paths_2:
                        path = path_1 + path_2[1:]  # Combine the two paths
                        if return_message_info:
                            path = [self.message_dict[msg_id] for msg_id in path]
                        paths.append(path)

        return paths if paths else None

    def _get_n_hop_neighbors(
        self, message_id: str, n: int
    ) -> Union[List[Dict[str, Any]], None]:
        """Returns a list of all n-hop neighbors of the message with the given ID, or None if the message doesn't exist"""
        if message_id not in self.message_dict:
            return None
        return nx.single_source_shortest_path_length(
            self._get_message_tree(), message_id, cutoff=n
        )

    def _get_n_hop_neighbors_ids(
        self, message_id: str, n: int
    ) -> Union[List[str], None]:
        """Returns a list of all n-hop neighbors of the message with the given ID, or None if the message doesn't exist"""
        neighbors = self._get_n_hop_neighbors(message_id, n)
        if neighbors is None:
            return None
        return [neighbor for neighbor in neighbors]

    def _get_paths_between_messages(
        self, message_id_1: str, message_id_2: str, all_paths: bool = False
    ) -> Union[List[str], List[List[str]], None]:
        """
        Returns the shortest path or all shortest paths between the two given messages.

        Args:
            message_id_1: The ID of the first message.
            message_id_2: The ID of the second message.
            all_paths: If True, returns all shortest paths. Otherwise, returns a single shortest path.

        Returns:
            A path or list of paths between the two messages.
        """
        try:
            if all_paths:
                return list(
                    nx.all_shortest_paths(
                        self._get_message_tree(),
                        message_id_1,
                        message_id_2,
                        weight="weight",
                    )
                )
            else:
                return nx.shortest_path(
                    self._get_message_tree(),
                    message_id_1,
                    message_id_2,
                    weight="weight",
                )
        except nx.NetworkXNoPath:
            return []

    def get_bifurcation_points(
        self, message_id_1: str, message_id_2: str
    ) -> Optional[List[str]]:
        """Return a path or chain of bifurcation points between two messages, or None if no such chain exists."""
        path_or_chain = self._find_path_or_chain(message_id_1, message_id_2)
        if path_or_chain is None:
            return None
        return [
            node for node in path_or_chain if len(self.conversation_dict[node][1]) > 1
        ]

    def get_co_reference_chain_between_messages(
        self, message_id_1: str, message_id_2: str, n: int
    ) -> Optional[List[str]]:
        """Return a path or chain of commonly co-referenced messages between two messages, or None if no such chain exists."""
        path_or_chain = self._find_path_or_chain(message_id_1, message_id_2)
        if path_or_chain is None:
            return None
        commonly_co_referenced = self.get_commonly_co_referenced_messages(
            message_id_1, n
        )
        return [node for node in path_or_chain if node in commonly_co_referenced]

    def get_cross_references(
        self, message_id_1: str, message_id_2: str
    ) -> Optional[List[str]]:
        """Return a path or chain, including cross-references, between two messages, or None if no such path or chain exists."""
        return self._find_path_or_chain(message_id_1, message_id_2)

    def get_merge_points(self, message_id: str, n: int) -> List[str]:
        """Return list of message ids within n hops of message_id that have more than one parent."""
        neighbors = self._get_n_hop_neighbors(message_id, n)
        child_parent_dict = {}
        for parent, (_, children) in self.conversation_dict.items():
            for child in children:
                if child in child_parent_dict:
                    child_parent_dict[child].append(parent)
                else:
                    child_parent_dict[child] = [parent]
        return [node for node in neighbors if len(child_parent_dict.get(node, [])) > 1]

    def get_all_relationships_between_messages(
        self, message_id_1: str, message_id_2: str, return_message_info: bool = True
    ) -> List[List[Union[str, Dict[str, Any]]]]:
        """Return all paths, including cross-references, between two messages."""

        # Check if the message_id's are valid
        if (
            message_id_1 not in self.message_dict
            or message_id_2 not in self.message_dict
        ):
            raise ValueError("Invalid message_id(s)")

        paths = self._get_paths_between_messages(
            message_id_1, message_id_2, all_paths=True
        )
        if paths is None:
            return None

        if return_message_info:
            return [[self.message_dict[msg_id] for msg_id in path] for path in paths]
        else:
            return paths

    def get_commonly_co_referenced_messages(
        self, message_id: str, n: int
    ) -> Dict[Tuple[str, str], int]:
        """Return pairs of messages within n hops of message_id that are commonly referenced together and how often they co-occur."""

        # Check if the message_id is valid
        if message_id not in self.message_dict:
            raise ValueError("Invalid message_id")

        neighbors = self._get_n_hop_neighbors_ids(message_id, n)
        if neighbors is None:
            return None

        # Get all pairs of messages within n hops of message_id
        pairs = list(itertools.combinations(neighbors, 2))

        # Get all pairs of messages that are commonly referenced together
        commonly_co_referenced = collections.Counter(
            [
                tuple(sorted(pair))
                for pair in pairs
                if self._are_commonly_co_referenced(pair[0], pair[1])
            ]
        )

        return commonly_co_referenced

    def _are_commonly_co_referenced(self, message_id_1: str, message_id_2: str) -> bool:
        # Check if the message_id's are valid
        if (
            message_id_1 not in self.message_dict
            or message_id_2 not in self.message_dict
        ):
            raise ValueError("Invalid message_id(s)")

        # Get the set of messages that reference message_id_1 and the set of messages that reference message_id_2
        references_1 = set(self._get_referencing_messages(message_id_1))
        references_2 = set(self._get_referencing_messages(message_id_2))

        # Find the intersection of the two sets
        common_references = references_1 & references_2

        # If no common message is found, the messages are not commonly co-referenced
        if not common_references:
            return False

        # Select a message from the common messages that minimizes the total distance of the chain
        common_reference = min(
            common_references,
            key=lambda node: nx.shortest_path_length(
                self._get_message_tree(), node, message_id_1
            )
            + nx.shortest_path_length(self._get_message_tree(), node, message_id_2),
        )

        # Get the paths from message_id_1 to the common reference and from the common reference to message_id_2
        path_to_common_reference = nx.shortest_path(
            self._get_message_tree(), message_id_1, common_reference
        )
        path_from_common_reference = nx.shortest_path(
            self._get_message_tree(), common_reference, message_id_2
        )

        # Return True if the paths are disjoint, False otherwise
        return not set(path_to_common_reference) & set(path_from_common_reference)

    def _get_referencing_messages(self, message_id: str) -> List[str]:
        """Returns a list of all messages that reference the message with the given ID, or None if the message doesn't exist"""
        if message_id not in self.message_dict:
            return None
        return [node for node in self._get_message_tree().predecessors(message_id)]
