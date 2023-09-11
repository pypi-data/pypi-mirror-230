from dlm_matrix.relationship import ChainRelationships
from typing import List, Tuple, Union, Dict, Optional, Callable
from dlm_matrix.models import ChainMap
from dlm_matrix.type import ScalingType, MethodType
from dlm_matrix.embedding.utils import normalize_scores
import datetime
import numpy as np
import logging



class Layout(ChainRelationships):
    def __init__(self) -> None:
        """Initializer for the MessageLayout class."""
        self.temporal_scale = 1.0  # Adjust this scale factor as needed

    def _temporal_weight(self, delta_time: datetime.timedelta) -> float:
        """Compute a temporal weight based on the time difference."""
        decay_rate = 1.0  # tune this as per requirements
        return np.exp(-decay_rate * delta_time)

    def time_diff_decay_function(
        self, time_diff: float, decay_type: str = "exponential", half_life: float = 60
    ) -> float:
        if half_life <= 0:
            logging.error("Half-life must be greater than zero.")
            return 1.0  # Default value

        try:
            if decay_type == "exponential":
                decay_factor = 0.5 ** (time_diff / half_life)
            elif decay_type == "logarithmic":
                decay_factor = 1 / (1 + np.log(time_diff + 1))
            elif decay_type == "linear":
                decay_factor = max(1 - time_diff / (time_diff + half_life), 0)
            else:
                raise ValueError(f"Unsupported decay type: {decay_type}")

            return decay_factor

        except Exception as e:
            logging.error(
                f"Error occurred while calculating time decay factor: {str(e)}"
            )
            return 1.0  # Default value

    def time_decay_factor(
        self,
        message: Union[ChainMap, None],
        sibling_time_differences: List[float],
        sub_thread_root: ChainMap,
    ) -> float:
        if sibling_time_differences and not all(
            isinstance(x, (int, float)) for x in sibling_time_differences
        ):
            logging.error("Sibling time differences should be a list of numbers.")
            return 1.0  # Default value

        try:
            if (
                not message
                or not hasattr(message, "message")
                or not message.message
                or not hasattr(message.message, "create_time")
            ):
                logging.error("Message or its attributes are invalid.")
                return 1.0  # Default value

            if (
                not sub_thread_root
                or not hasattr(sub_thread_root, "message")
                or not sub_thread_root.message
                or not hasattr(sub_thread_root.message, "create_time")
            ):
                logging.error("Sub_thread_root or its attributes are invalid.")
                return 1.0  # Default value

            time_diff = (
                datetime.datetime.fromtimestamp(message.message.create_time)
                - datetime.datetime.fromtimestamp(sub_thread_root.message.create_time)
            ).total_seconds() / 60

            decay_factor = self.time_diff_decay_function(time_diff)

            if sibling_time_differences:
                decay_factor *= np.mean(sibling_time_differences)

            return decay_factor

        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return 1.0  # Default value

    def _gather_similarity_scores(self, children_ids: List[str]) -> List[float]:
        """
        Gather similarity scores for a list of children messages.

        Args:
            children_ids (List[str]): A list of IDs for children messages.

        Returns:
            List[float]: A list of similarity scores.
        """

        # Pre-calculate previous and next sibling IDs for all children
        prev_sibling_ids = [
            self._get_previous_sibling_id(child_id) for child_id in children_ids
        ]
        next_sibling_ids = [
            self._get_next_sibling_id(child_id) for child_id in children_ids
        ]

        # Gather similarity scores where both prev and next siblings exist
        similarity_scores = [
            self.calculate_similarity_score(prev_id, next_id)
            for prev_id, next_id in zip(prev_sibling_ids[:-1], next_sibling_ids[1:])
            if prev_id and next_id
        ]

        return similarity_scores

    def calculate_time_coordinate(
        self, mapping: ChainMap, children_ids: List[str], sub_thread_root: ChainMap
    ) -> float:
        if not mapping or not children_ids or not sub_thread_root:
            logging.error("Invalid mapping, children_ids, or sub_thread_root.")
            return 1.0  # Default value

        sibling_time_differences = [
            self.message_dict[child_id].message.create_time
            - mapping.message.create_time
            for child_id in children_ids
        ]

        time_decay_factor = self.time_decay_factor(
            mapping, sibling_time_differences, sub_thread_root
        )
        return time_decay_factor

    def calculate_temporal_weight(
        self,
        message_dict: Dict[str, object],
        sub_thread_root: Optional[ChainMap] = None,
    ) -> Union[float, np.ndarray]:
        """Calculate the temporal weight for either a set of messages or a specific sub_thread_root."""

        if not message_dict:
            logging.error("message_dict must be provided.")
            return 1.0  # Default value

        # If a sub_thread_root is specified, calculate the weight for that specific root
        if sub_thread_root:
            mapping = self.get_mapping_for_sub_thread_root(
                sub_thread_root, message_dict
            )

            # Check if the mapping is found to prevent infinite recursion
            if not mapping:
                logging.error("Mapping not found for sub_thread_root.")
                return 1.0  # Default value

            children_ids = self.get_children_ids(mapping.parent)

            # Compute the temporal weight based on the sub-thread root
            time_coordinate = self.calculate_time_coordinate(
                mapping, children_ids, sub_thread_root
            )

            return (
                time_coordinate  # Modify this if you need to factor in other variables
            )

        # Otherwise, calculate weights for all messages
        else:
            valid_messages = [
                message.message.create_time
                for message in message_dict.values()
                if message.message and message.message.create_time is not None
            ]

            create_times = np.array(valid_messages)
            delta_times = np.abs(create_times[:, np.newaxis] - create_times)
            temporal_weights = np.vectorize(self.time_diff_decay_function)(
                delta_times, "exponential"
            )

            # Filter out the diagonal elements
            return temporal_weights[
                np.where(~np.eye(temporal_weights.shape[0], dtype=bool))
            ]

    def calculate_spacing(
        self, children_ids: List[str], normalized_scores, method: str
    ) -> float:
        """
        Calculate the spacing between siblings based on similarity.

        Args:
            children_ids: The IDs of the message's children.
            normalized_scores: Normalized similarity scores.
            method: The method used for calculating spacing ("both" or "spacing").

        Returns:
            The calculated spacing as a float.
        """

        if len(children_ids) <= 1:
            return 0

        if method == MethodType.BOTH:
            # Calculate the average normalized similarity score among siblings
            avg_similarity = np.mean(normalized_scores) if normalized_scores else 0

            # Calculate the spacing factor based on similarity
            spacing_factor = -0.5 + avg_similarity * 0.5
            spacing = spacing_factor * (len(children_ids) - 1)
        else:
            # Use the original formula without considering similarity
            spacing = 0 if len(children_ids) == 1 else -0.5 * (len(children_ids) - 1)

        return spacing

    def calculate_weighted_z_coord(
        self, normalized_scores: List[float], temporal_weights: np.ndarray
    ) -> float:
        """Calculate a weighted z-coordinate based on normalized scores and temporal weights."""
        return sum(
            score * weight for score, weight in zip(normalized_scores, temporal_weights)
        )

    def calculate_final_z_coord(
        self,
        normalized_scores: List[float],
        temporal_weights: np.array,
        children_ids: List[str],
        alpha_final_z: float = 0.7,
        method: str = MethodType.BOTH,
    ) -> float:
        """
        Calculate the final z-coordinate incorporating both weights and sibling spacing.

        Args:
            normalized_scores: List of normalized similarity scores.
            temporal_weights: Numpy array of temporal weights.
            children_ids: List of children IDs.
            alpha_final_z: Weighting factor for combining weighted_z_coord and sibling_spacing. Defaults to 0.7.
            method: String indicating which method to use for calculation. Can be "weighted", "spacing", or "both". Defaults to "both".

        Returns:
            The final z-coordinate as a float.
        """

        # Early exit for invalid method
        if method not in MethodType:
            raise ValueError(f"Invalid method type. Choose from {list(MethodType)}.")

        # Validate alpha_final_z
        if not (0 <= alpha_final_z <= 1):
            raise ValueError("alpha_final_z must be between 0 and 1.")

        weighted_z_coord = sibling_spacing = 0.0

        # Calculate based on method types
        if method in [MethodType.WEIGHTED, MethodType.BOTH]:
            weighted_z_coord = self.calculate_weighted_z_coord(
                normalized_scores, temporal_weights
            )

        if method in [MethodType.SPACING, MethodType.BOTH]:
            sibling_spacing = self.calculate_spacing(
                children_ids, normalized_scores, method
            )

        # Final calculation
        final_z_coord = (
            (alpha_final_z * weighted_z_coord + (1 - alpha_final_z) * sibling_spacing)
            if method == MethodType.BOTH
            else weighted_z_coord
            if method == MethodType.WEIGHTED
            else sibling_spacing
        )

        return final_z_coord

    def calculate_t_coordinate(
        self,
        depth: int,
        alpha_scale: Union[float, Callable[[str, str], float]],
        sub_thread_root: str,
        mapping: ChainMap,
        temporal_weights: List[float],
        i: int,
    ) -> float:
        """
        Calculate the t-coordinate based on given parameters.

        Args:
            depth: Depth level of the message in the tree.
            alpha_scale: A float or callable for alpha scaling.
            sub_thread_root: ID of the sub-thread root.
            message: Type of the message.
            temporal_weights: List of temporal weights.
            i: Index of the message.

        Returns:
            t_coord: Calculated t-coordinate.
        """

        # Normalize depth
        max_depth = self.depth
        normalized_depth = depth / max_depth if max_depth != 0 else 0

        # Get the dynamic alpha_scale if it's a function
        dynamic_alpha_scale = (
            alpha_scale(
                sub_thread_root,
                mapping.message.content.content_type,
            )
            if callable(alpha_scale)
            else alpha_scale
        )

        # Validate dynamic_alpha_scale
        if not 0 <= dynamic_alpha_scale <= 1:
            logging.error("Invalid dynamic alpha_scale.")
            return 0.0

        # T-coordinate
        t_coord = (
            dynamic_alpha_scale * temporal_weights[i]
            + (1 - dynamic_alpha_scale) * normalized_depth
        )

        return t_coord

    def calculate_sibling_spacing(
        self,
        children_ids: List[str],
        temporal_weights: np.array,
        method: str = MethodType.BOTH,
        alpha_final_z: float = 0.5,
        alpha_similarity: float = 0.2,
    ) -> float:
        """
        Calculate the spacing between siblings based on similarity scores, temporal weights, and spacing.

        Args:
            children_ids: List of children IDs.
            temporal_weights: Numpy array of temporal weights.
            method: String indicating which method to use for calculation. Can be "weighted", "spacing", or "both". Defaults to "both".
            alpha_final_z: Weighting factor for combining weighted_z_coord and sibling_spacing. Defaults to 0.5.
            alpha_similarity: Weighting factor for adding the influence of similarity scores. Defaults to 0.2.

        Returns:
            The final z-coordinate as a float.
        """

        if len(children_ids) == 1:
            return 0

        similarity_scores = self._gather_similarity_scores(children_ids)
        normalized_scores = normalize_scores(similarity_scores)

        weighted_z_coord = self.calculate_final_z_coord(
            normalized_scores, temporal_weights, children_ids, alpha_final_z, method
        )

        # Now you can include the similarity score's influence on spacing
        mean_similarity = np.mean(similarity_scores) if similarity_scores else 0
        weighted_z_coord += alpha_similarity * mean_similarity

        return weighted_z_coord

    def calculate_xy_coordinates(
        self,
        i: int,
        depth: int,
        z_coord: float,
        scaling: ScalingType,
        alpha_scale: float,
    ) -> Tuple[float, float]:
        """
        Calculate the x and y coordinates based on the given scaling method and parameters.

        Args:
            i: Index of the message.
            depth: Depth level of the message in the tree.
            z_coord: Calculated z-coordinate for the message.
            scaling: The type of scaling to use, as defined in ScalingType.
            alpha_scale: A float value for scaling in the 'linear_combination' type. Must be between 0 and 1.

        Returns:
            Tuple containing the x and y coordinates.
        """

        if not (0 <= alpha_scale <= 1):
            logging.error("alpha_scale must be between 0 and 1.")
            return 0.0, 0.0

        if depth < 0:
            logging.error("Depth cannot be negative.")
            return 0.0, 0.0

        try:
            # Pre-computed values for efficiency
            scaled_depth = alpha_scale * depth
            scaled_index = alpha_scale * (i + 1)
            scaled_z_coord = (1 - alpha_scale) * z_coord

            # Using a dictionary to map scaling types to calculations
            methods = {
                ScalingType.LINEAR_COMBINATION: (
                    scaled_depth + scaled_z_coord,
                    scaled_index + scaled_z_coord,
                ),
                ScalingType.DIRECT: (depth + z_coord, i + 1 + z_coord),
            }

            return methods.get(scaling, (0.0, 0.0))

        except Exception as e:
            logging.error(
                f"Error occurred while calculating x and y coordinates: {str(e)}"
            )
            return 0.0, 0.0

    def _calculate_coordinates(
        self,
        i: int,
        children_ids: List[str],
        depth: int,
        mapping: object,
        scaling: str = ScalingType.DIRECT,
        alpha_scale: float = 1,
        method: str = MethodType.SPACING,
        alpha_final_z: float = 0.7,
    ) -> Tuple[float, float, float, float, int]:
        """
        Calculate the 3D coordinates for a message based on its relationships.
        ...
        """
        # Validate parameters
        if depth < 0 or not (0 <= alpha_scale <= 1) or not (0 <= alpha_final_z <= 1):
            logging.error("Invalid parameters.")
            return 0.0, 0.0, 0.0, 0.0, 0

        try:
            # Find the roots for all sub-threads
            sub_thread_roots = self.find_sub_thread_roots()

            # Determine the appropriate root for the current message
            sub_thread_root = sub_thread_roots.get(
                mapping.parent, None
            )  # Fallback to None if not found

            # Pre-calculate common variables
            temporal_weights = self.calculate_temporal_weight(
                message_dict=self.message_dict, sub_thread_root=sub_thread_root
            )

            # Z-coordinate
            z_coord = self.calculate_sibling_spacing(
                children_ids, temporal_weights, method, alpha_final_z
            )

            # T-coordinate
            t_coord = self.calculate_t_coordinate(
                depth, alpha_scale, sub_thread_root, mapping, temporal_weights, i
            )
            
            n_parts = len(mapping.message.content.text.split("\n\n"))

            # Coordinate calculation methods
            methods = {
                MethodType.SPACING: (depth, i + 1),
                MethodType.WEIGHTED: self.calculate_xy_coordinates(
                    i, depth, z_coord, scaling, alpha_scale
                ),
                MethodType.BOTH: self.calculate_xy_coordinates(
                    i, depth, z_coord, scaling, alpha_scale
                ),
            }

            x_coord, y_coord = methods.get(method, (0.0, 0.0))

            return x_coord, y_coord, z_coord, t_coord, n_parts

        except Exception as e:
            logging.error(f"Error occurred while calculating coordinates: {str(e)}")
            return 0.0, 0.0, 0.0, 0.0, 0
