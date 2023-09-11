from typing import List, Dict, Optional, Union, Any
from .manager import SynthesisTechniqueManager
from .builder import ReplyChainBuilder
from .technique import SynthesisTechniqueDirector
from .director import ReplyChainDirector
from dlm_matrix.utils import log_handler


class ReplyChainSystem:
    def __init__(self):
        self.reply_chain_builder = ReplyChainBuilder()

        self.technique_manager = SynthesisTechniqueManager()
        self.name = self.technique_manager.get_random_synthesis_technique_name()

        self.tech_director = SynthesisTechniqueDirector(
            technique_name=self.name,
            builder=self.reply_chain_builder,
            technique_manager=self.technique_manager,
        )

        self.director = ReplyChainDirector(
            technique_director=self.tech_director,
        )

    def construct_reply_chain(self, prompt, response: Optional[str] = None):
        """
        Construct the reply chain with given prompt and response.
        """

        if not isinstance(prompt, str):
            raise ValueError("Prompt must be a string.")
        if response is not None and not isinstance(response, str):
            raise ValueError("Response must be a string.")

        self.director.construct(prompt, response)
        self.chain_tree = self.reply_chain_builder.get_result()

    def _validate_conversation_data(self, data: List[Dict[str, Union[str, None]]]):
        """
        Validate conversation data.
        """
        if not isinstance(data, list):
            raise ValueError("Conversation data must be a list of dictionaries.")

        if not data:
            raise ValueError("Conversation data must not be empty.")

        for item in data:
            if not isinstance(item, dict):
                raise ValueError("Each conversation item must be a dictionary.")
            if "prompt" not in item or not isinstance(item["prompt"], str):
                raise ValueError("The 'prompt' key must exist and be a string.")
            if "response" in item and not (
                isinstance(item["response"], str) or item["response"] is None
            ):
                raise ValueError("The 'response' key must be either a string or None.")

    def process_conversations(self, data: List[Dict[str, str]]) -> None:
        """
        Processes a list of conversation data to construct reply chains.

        Args:
        - data (List[Dict[str, str]]): List of dictionaries containing 'prompt' and 'response' as keys.

        Returns:
        - None
        """

        # Validate the conversation data to ensure it meets expectations
        try:
            self._validate_conversation_data(data)
        except ValueError as e:
            log_handler(f"Validation failed: {e}", step="process_conversations")
            return

        # Initialize counter to keep track of processed conversations
        counter = 0

        # Loop through each conversation data item to construct reply chains
        for item in data:
            try:
                log_handler("Constructing reply chain...", step="process_conversations")
                self.director.construct(item["prompt"], item["response"])
                counter += 1
            except Exception as e:
                log_handler(
                    f"Failed to construct reply chain for item: {item}. Error: {e}",
                    step="process_conversations",
                )
                continue

        # Get the resulting chain tree
        self.chain_tree = self.reply_chain_builder.get_result()

        # Log completion message
        log_handler(
            f"Successfully constructed {counter} reply chains.",
            step="process_conversations",
        )

    def add_nodes_from_chains(self, chains: Optional[List[str]] = None) -> None:
        """
        Add nodes from chains to the chain tree. Each node in the tree represents a conversation segment
        from a given chain.

        Args:
        - chains (Optional[List[str]]): List of conversation chains. If not provided, will use the default chains from the instance.

        Returns:
        - None
        """

        # Check if 'chains' is provided or default to instance chains.
        if chains is None:
            log_handler(
                "No chains provided. Fetching default chains.",
                step="add_nodes_from_chains",
            )
            chains = self.get_chains()

        # Validate that chains are provided and are in expected format
        if not chains or not isinstance(chains, list):
            log_handler(
                "Chains are either empty or not in the expected format. Exiting.",
                step="add_nodes_from_chains",
            )
            return

        # Iterating through each chain and adding them to the tree
        for chain in chains:
            # Ensure the chain has content and the content has text
            if chain.content and chain.content.text:
                # Generate a new unique node ID based on the current number of nodes
                node_id = str(len(self.chain_tree.nodes) + 1)
                raw = chain.content.text

                # Add the node to the chain tree
                self.chain_tree.add_node(raw, node_id)

            else:
                log_handler(
                    f"Skipped chain due to missing content or text.",
                    step="add_nodes_from_chains",
                )

    def _truncate_conversation(
        self,
        chains: List[str],
        max_history_length: Optional[int] = None,
        prioritize_recent: bool = True,
    ) -> List[str]:
        """
        Truncates the conversation history to fit within a specified maximum length.

        Parameters:
            - chains (List[str]): The list of conversation chains to truncate.
            - max_history_length (int, optional): The maximum allowable length for the entire conversation history.
            - prioritize_recent (bool, optional): If True, removes older conversation chains first; otherwise removes the newer ones.

        Returns:
            - List[str]: The truncated list of conversation chains.
        """

        # Validate that 'chains' is a list and is not empty
        if not isinstance(chains, list):
            log_handler(
                "Provided chains parameter is not a list. Raising a ValueError.",
                step="_truncate_conversation",
            )
            raise ValueError("Conversation history must be a list of chains.")
        if not chains:
            log_handler(
                "Provided chains parameter is empty. Raising a ValueError.",
                step="_truncate_conversation",
            )
            raise ValueError("Conversation history must not be empty.")

        # If max_history_length is provided, start the truncation process
        if max_history_length is not None:
            log_handler(
                f"Max history length is set to {max_history_length}. Starting to truncate conversation history.",
                step="_truncate_conversation",
            )

            # Calculate the total length of the conversation chains
            total_length = sum(len(chain.content.text) for chain in chains)
            log_handler(
                f"Total length of conversation history is {total_length}.",
                step="_truncate_conversation",
            )

            # Truncate chains until total_length <= max_history_length
            while total_length > max_history_length:
                log_handler(
                    "Total length exceeds max history length. Truncating...",
                    step="_truncate_conversation",
                )

                # Remove either the oldest or the newest chain based on 'prioritize_recent'
                if prioritize_recent:
                    log_handler(
                        "Prioritizing recent conversations. Removing the oldest chain.",
                        step="_truncate_conversation",
                    )
                    removed_chain = chains.pop(0)
                else:
                    log_handler(
                        "Not prioritizing recent conversations. Removing the newest chain.",
                        step="_truncate_conversation",
                    )
                    removed_chain = chains.pop()

                # Update the total_length
                total_length -= len(removed_chain.content.text)
                log_handler(
                    f"Removed a chain. New total length is {total_length}.",
                    step="_truncate_conversation",
                )

        return chains

    def _process_custom_conversation_data(
        self,
        custom_conversation_data: List[Dict[str, str]],
        use_process_conversations: bool,
    ) -> None:
        """
        Processes custom conversation data based on the given flag use_process_conversations.
        """
        if use_process_conversations:
            log_handler(
                "Using process_conversations method for custom data",
                step="custom_data_process",
            )
            self.process_conversations(custom_conversation_data)
        else:
            log_handler(
                "Using individual construct_reply_chain calls for custom data",
                step="custom_data_process",
            )
            for conversation_item in custom_conversation_data:
                if "prompt" not in conversation_item:
                    raise ValueError(
                        "Each dictionary in custom_conversation_data should have a 'prompt' key."
                    )
                prompt = conversation_item["prompt"]
                response = conversation_item.get("response")
                self.construct_reply_chain(prompt, response)

    def _process_single_conversation(
        self,
        prompt: Optional[str],
        response: Optional[str],
        use_process_conversations: bool,
    ) -> None:
        """
        Processes a single conversation based on the given flag use_process_conversations.
        """
        if use_process_conversations:
            log_handler(
                "Using process_conversations method for single conversation",
                step="single_conversation_process",
            )
            conversation_data = [{"prompt": prompt, "response": response}]
            self.process_conversations(conversation_data)
        else:
            log_handler(
                "Using construct_reply_chain for single conversation",
                step="single_conversation_process",
            )
            self.construct_reply_chain(prompt, response)

    def _validate_parameters(
        self,
        max_history_length: Optional[int],
        custom_conversation_data: Optional[List[Dict[str, str]]],
    ) -> None:
        """
        Validates the parameters.
        """
        if max_history_length is not None and not isinstance(max_history_length, int):
            raise ValueError("max_history_length must be an integer.")

        if custom_conversation_data is not None and not isinstance(
            custom_conversation_data, list
        ):
            raise ValueError("custom_conversation_data must be a list of dictionaries.")

    def prepare_conversation_history(
        self,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        use_process_conversations: bool = False,
        custom_conversation_data: Optional[List[Dict[str, str]]] = None,
        max_history_length: Optional[int] = None,
        prioritize_recent: bool = True,
    ) -> str:
        log_handler("Starting the preparation of conversation history", step="start")

        # Validate the parameters
        log_handler("Validating parameters", step="validation")
        self._validate_parameters(max_history_length, custom_conversation_data)

        # Process custom conversation data if provided
        if custom_conversation_data:
            log_handler("Custom conversation data provided", step="custom_data")
            self._process_custom_conversation_data(
                custom_conversation_data, use_process_conversations
            )
        else:
            log_handler("Single conversation provided", step="single_conversation")
            self._process_single_conversation(
                prompt, response, use_process_conversations
            )

        # Add conversation chains to data structure
        log_handler("Adding nodes from conversation chains", step="add_nodes")
        self.add_nodes_from_chains()

        # Truncate the conversation history if needed
        log_handler("Truncating conversation history", step="truncate")
        truncated_history = self._truncate_conversation(
            self.get_chains(),
            max_history_length=max_history_length,
            prioritize_recent=prioritize_recent,
        )

        log_handler(
            "Completed the preparation of conversation history", step="complete"
        )

        return truncated_history

    def get_chains(self):
        """
        Get chains from the chain tree.
        """
        return self.chain_tree.get_chains()
