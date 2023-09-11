from typing import Dict, Any, Optional, Deque
from collections import deque
import numpy as np
from dlm_matrix.relationship import ChainRelationships
from math import exp, log
from time import time
from typing import Dict


ESTIMATE_HISTORY_MAXLEN = 100
default_params = {
    "weight": 0.11,
    "frequency": 0,
    "importance": 1.0,
    "last_observed": 0,
}

variable_params = {
    "siblings": {"importance": 1.0},
    "cousins": {"importance": 0.8},
    "uncles_aunts": {"importance": 0.7},
    "nephews_nieces": {"importance": 0.6},
    "grandparents": {"weight": 0.16, "importance": 0.9},
    "ancestors": {"weight": 0.2, "importance": 0.5},
    "descendants": {"weight": 0.2, "importance": 1.2},
}


class Estimator(ChainRelationships):
    RELATIONSHIPS = {
        key: {**default_params, **params} for key, params in variable_params.items()
    }

    def __init__(
        self,
        message_dict: Dict[str, Any],
        conversation_dict: Optional[Dict[str, Any]] = None,
    ):
        self.message_dict = message_dict
        self.conversation_dict = conversation_dict

        self._message_references = {msg_id: {} for msg_id in self.message_dict.keys()}

        self.estimate_history: Dict[str, Deque[int]] = {
            "baseline": deque(maxlen=ESTIMATE_HISTORY_MAXLEN),
            "relationships": deque(maxlen=ESTIMATE_HISTORY_MAXLEN),
            "types": deque(maxlen=ESTIMATE_HISTORY_MAXLEN),
            "weighted": deque(maxlen=ESTIMATE_HISTORY_MAXLEN),
        }
        self.estimate_weights: Dict[str, float] = {
            "baseline": 1.0,
            "relationships": 1.0,
            "types": 1.0,
            "weighted": 1.0,
        }

        self.n_neighbors_weighted = 0

    def update_relationship_frequency(self, relationship_dict: Dict[str, Any]):
        """
        Update the frequency count of each relationship type based on the provided dictionary.

        Parameters:
            - relationship_dict: Dictionary containing types of relationships and their instances for a specific message.
        """
        """Update the frequency count for each relationship type based on the provided dictionary."""
        current_time = time()  # or any other method of tracking 'now'
        for rel_type in relationship_dict.keys():
            if rel_type in self.RELATIONSHIPS:
                self.RELATIONSHIPS[rel_type]["frequency"] += 1
                self.RELATIONSHIPS[rel_type][
                    "last_observed"
                ] = current_time  # Update the last observed time

    def get_dynamic_decay_factor(self) -> float:
        """Compute a dynamic decay factor based on average time since the last observed relationship."""
        total_time_since_last = sum(
            rel.get("last_observed", 0) for rel in self.RELATIONSHIPS.values()
        )
        avg_time_since_last = total_time_since_last / len(self.RELATIONSHIPS)

        # Assuming a base decay factor, which is modified based on the average time since the last observed relationship
        base_decay = 0.9
        return base_decay * (
            1 + avg_time_since_last / 100
        )  # Adjust this formula as needed

    def update_relationship_weights(self):
        """
        Update the relationship weights based on advanced metrics such as frequency, recency, and importance.
        """
        total_frequency = sum(rel["frequency"] for rel in self.RELATIONSHIPS.values())
        if total_frequency == 0:
            return

        max_recency = max(
            rel.get("last_observed", 0) for rel in self.RELATIONSHIPS.values()
        )

        # Get dynamic decay factor
        decay_factor = self.get_dynamic_decay_factor()

        # Prepare a list to store new weights temporarily
        new_weights = {}

        for rel_type, rel_data in self.RELATIONSHIPS.items():
            # Frequency: Logarithmic scaling
            frequency_weight = log(rel_data["frequency"] + 1)

            # Recency: Exponential decay
            time_since_last_observed = max_recency - rel_data.get("last_observed", 0)
            recency_weight = exp(-decay_factor * time_since_last_observed)

            # Importance: Quadratic scaling
            importance_weight = (rel_data["importance"]) ** 2

            # Combine the metrics: The coefficients here can be fine-tuned
            new_weight = (
                0.4 * frequency_weight + 0.3 * recency_weight + 0.3 * importance_weight
            )

            # Store the new weight temporarily
            new_weights[rel_type] = new_weight

        # Normalize the new weights
        total_new_weight = sum(new_weights.values())
        for rel_type in self.RELATIONSHIPS:
            self.RELATIONSHIPS[rel_type]["weight"] = (
                new_weights[rel_type] / total_new_weight
            )

    def _update_history(self, new_estimates: Dict[str, int]) -> None:
        """
        Updates the estimate history with new estimates.

        Args:
            new_estimates (Dict[str, int]): A dictionary containing new estimates
                                            keyed by the estimate type.

        Raises:
            ValueError: If an invalid estimate type is encountered.
        """
        for estimate_type, new_estimate in new_estimates.items():
            if estimate_type in self.estimate_history:
                self.estimate_history[estimate_type].append(new_estimate)
            else:
                raise ValueError(f"Invalid estimate type: {estimate_type}")

    def _recalculate_weights(self) -> None:
        """
        Recalculates weights based on the updated history.

        The weight for each estimate type is calculated as the inverse of its
        historical mean. If the mean is zero, the weight is set to zero.
        """
        for estimate_type, history in self.estimate_history.items():
            if not history:  # Skip if history is empty
                continue
            mean_estimate = np.mean(history)
            if mean_estimate > 0:
                self.estimate_weights[estimate_type] = 1 / mean_estimate
            else:
                self.estimate_weights[estimate_type] = 0.0

    def _normalize_weights(self) -> None:
        """
        Normalizes weights so that they sum to 1.

        The function will handle edge cases where the sum of weights is zero.
        In such cases, it sets all weights to equal values.
        """
        total_weight = sum(self.estimate_weights.values())
        if total_weight > 0:
            self.estimate_weights = {
                k: v / total_weight for k, v in self.estimate_weights.items()
            }
        else:
            self.estimate_weights = {
                k: 1.0 / len(self.estimate_weights) for k in self.estimate_weights
            }

    def update_estimate_history_and_weights(
        self, new_estimates: Dict[str, int]
    ) -> Dict[str, float]:
        """
        Update the estimate history with new estimates and recalculate the weights.

        The function updates the history of each estimate type with the new estimates,
        recalculates the weights based on this updated history, and then normalizes these
        weights so that they sum up to 1.

        Args:
            new_estimates (Dict[str, int]): A dictionary containing new estimates
                                            keyed by the estimate type.

        Returns:
            Dict[str, float]: A dictionary containing the normalized weights for each estimate type.
        """
        self._update_history(new_estimates)
        self._recalculate_weights()
        self._normalize_weights()

        return self.estimate_weights

    def compute_new_estimates(
        self, relationship_dict: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Compute new estimates for the number of neighbors based on the given relationship dictionary.

        Args:
            relationship_dict (Dict[str, Any]): A dictionary containing the relationships of a message.

        Returns:
            Dict[str, int]: A dictionary containing the new estimates for the number of neighbors,
                            keyed by the estimate type ("baseline", "relationships", "types", "weighted").
        """
        # Compute baseline n_neighbors based on the square root of the total number of messages
        n_neighbors_baseline = int(np.sqrt(len(self.message_dict)))

        # Compute n_neighbors based on the size of the largest relationship
        n_neighbors_relationships = max(len(v) for v in relationship_dict.values())

        # Compute n_neighbors based on the number of different relationship types
        n_neighbors_types = len([k for k, v in relationship_dict.items() if v])

        # Compute n_neighbors based on the weighted size of each relationship
        n_neighbors_weighted = sum(
            self.RELATIONSHIPS[rel_type]["weight"] * len(rel)
            for rel_type, rel in relationship_dict.items()
        )

        return {
            "baseline": n_neighbors_baseline,
            "relationships": n_neighbors_relationships,
            "types": n_neighbors_types,
            "weighted": n_neighbors_weighted,
        }

    def determine_n_neighbors(self, message_id: str) -> int:
        """
        Calculate the number of neighbors for a given message based on its relationships.

        This function fetches the relationships of a message by its ID, computes new estimates for the
        number of neighbors, updates the estimate history and weights, and then returns the average of
        these new estimates.

        Args:
            message_id (str): The ID of the message for which to calculate the number of neighbors.

        Returns:
            int: The calculated number of neighbors for the given message ID.

        Raises:
            ValueError: If the message ID is not found in the message dictionary.
        """
        if message_id not in self.message_dict:
            raise ValueError(
                f"Message ID {message_id} not found in message dictionary."
            )

        relationship_dict = self.get_relationship(message_id)

        # Update relationship frequencies and weights
        self.update_relationship_frequency(relationship_dict)
        self.update_relationship_weights()

        new_estimates = self.compute_new_estimates(relationship_dict)
        self.update_estimate_history_and_weights(new_estimates)

        self.n_neighbors_weighted = int(
            sum(
                self.estimate_weights[estimate_type] * new_estimate
                for estimate_type, new_estimate in new_estimates.items()
            )
        )

        return int(np.mean(list(new_estimates.values())))
