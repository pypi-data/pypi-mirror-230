from typing import Dict, List, Tuple
from dlm_matrix.models import ChainTreeIndex, ChainTree, ChainMap, Chain
from tqdm import tqdm


class TreeMerger:
    """
    TreeMerger is responsible for merging multiple conversation trees into batches,
    retrieving mappings from these trees, and updating parent-child relationships.
    """

    def combine_conversations_in_batches(
        self, conversation_trees: List[ChainTreeIndex], batch_size: int = 1000
    ) -> List[ChainTreeIndex]:
        """
        Combine conversation trees in batches.

        Given a list of conversation trees, this method combines them in batches and
        returns a list of combined trees.

        Parameters:
            conversation_trees (List[ChainTreeIndex]): A list of conversation trees to be combined.
            batch_size (int, optional): The size of each batch for combination. Default is 1000.

        Returns:
            List[ChainTreeIndex]: A list of combined conversation trees.
        """
        batched_trees = []
        for i in tqdm(
            range(0, len(conversation_trees), batch_size), desc="Processing batches"
        ):
            batch = conversation_trees[i : i + batch_size]
            combined_tree = self.combine_conversations(batch)
            batched_trees.append(combined_tree)
        return batched_trees

    def retrieve_mappings(
        self, conversation_trees: List[ChainTreeIndex]
    ) -> List[ChainMap]:
        """
        Retrieve the mappings from a list of ChainTreeIndex objects, each representing
        a conversation tree.

        This method iterates through the list of ChainTreeIndex objects and extracts the
        mappings (ChainMap objects) from each tree, extending the list of mappings.

        Parameters:
            conversation_trees (List[ChainTreeIndex]): A list of ChainTreeIndex objects,
            each containing conversation data as a tree.

        Returns:
            List[ChainMap]: A list of ChainMap objects that contain the mappings of
            messages, parents, and children for each conversation tree.
        """
        print("Retrieving mappings from conversations...")
        mappings = []
        for tree in tqdm(conversation_trees):
            mappings.extend(list(tree.conversation.mapping.values()))
        return mappings

    def update_parent_child(self, mappings: List[ChainMap]) -> Dict[str, str]:
        """
        Update the parent-child relationships in the mappings and return a dictionary
        of new mapping IDs.

        This method traverses a list of ChainMap objects and updates the parent-child
        relationships based on the 'parent' and 'children' attributes in each ChainMap.
        It generates a new set of mapping IDs and a dictionary that associates each
        parent message ID with its children message IDs.

        Parameters:
            mappings (List[ChainMap]): A list of ChainMap objects containing conversation
            mappings.

        Returns:
            Dict[str, str]: A dictionary where each key-value pair represents a message
            ID and its new mapping ID.
        """
        print("Creating new IDs for mappings...")

        # If mappings is None or empty, return an empty dictionary
        if not mappings:
            return {}

        new_mapping_ids = {}
        parent_child_map = {}

        for mapping in tqdm(mappings):
            if mapping.message is not None:
                # Still retain the message ID mapping, as you did before
                new_mapping_ids[mapping.message.id] = mapping.message.id

                # Check for parent and establish a parent-child relationship
                parent_id = mapping.parent
                if parent_id:
                    # Store children IDs in a list against their parent
                    if parent_id not in parent_child_map:
                        parent_child_map[parent_id] = []
                    parent_child_map[parent_id].append(mapping.message.id)

        # Now, update the children information for each mapping based on the parent_child_map
        for mapping in mappings:
            if mapping.message and mapping.message.id in parent_child_map:
                mapping.children = parent_child_map[mapping.message.id]

        return new_mapping_ids

    def extract_and_sort_messages(
        self, mappings: List[ChainMap], new_mapping_ids: Dict[str, str]
    ) -> List[Chain]:
        """
        Extract and sort the messages based on their creation time.

        This method traverses a list of ChainMap objects and extracts each message
        object. It then updates the ID of each message with its new mapping ID and sorts
        the messages by their creation time.

        Parameters:
            mappings (List[ChainMap]): A list of ChainMap objects containing conversation
            mappings.

            new_mapping_ids (Dict[str, str]): A dictionary of new mapping IDs, where each
            key-value pair represents a message ID and its new mapping ID.

        Returns:
            List[Chain]: A list of Chain objects, representing messages, sorted by their
            creation time.
        """
        print("Extracting and sorting messages...")
        sorted_messages = []

        for mapping in tqdm(mappings):
            if mapping.message is not None:
                mapping.message.id = new_mapping_ids[mapping.message.id]
                sorted_messages.append(mapping.message)

        # Sort the messages based on their creation time
        sorted_messages.sort(key=lambda m: (m.create_time is None, m.create_time))

        return sorted_messages

    def create_linked_list(self, sorted_messages: List[Chain]) -> List[Chain]:
        """
        Create a doubly-linked list of sorted messages.

        This method iterates through a list of sorted messages (Chain objects) and
        updates the 'prev' and 'next' attributes for each message to establish a
        doubly-linked list.

        Parameters:
            sorted_messages (List[Chain]): A list of Chain objects, representing messages,
            sorted by their creation time.

        Returns:
            List[Chain]: A list of Chain objects, now organized as a doubly-linked list.
        """
        print("Creating linked list...")
        id_mapping = {}
        for i, message in tqdm(enumerate(sorted_messages)):
            # For each message, determine its previous and next based on its position in the sorted list
            message.prev = sorted_messages[i - 1].id if i > 0 else None
            message.next = (
                sorted_messages[i + 1].id if i < len(sorted_messages) - 1 else None
            )
            id_mapping[message.id] = message.id
        return sorted_messages

    def update_mappings(
        self, sorted_messages: List[Chain], conversation_trees: List[ChainTreeIndex]
    ) -> List[ChainMap]:
        """
        Update existing mappings or create new ones for sorted messages.

        This method iterates through a list of sorted messages and a list of conversation trees.
        It updates the existing mappings with new message information or creates new mappings
        if they do not already exist. If a message is by the system and is a prompt, it also
        updates the message content and creation time.

        Parameters:
            sorted_messages (List[Chain]): A list of Chain objects, representing sorted messages.

            conversation_trees (List[ChainTreeIndex]): A list of ChainTreeIndex objects representing
            the structure of conversation trees.

        Returns:
            List[ChainMap]: A list of updated ChainMap objects containing the new mappings.
        """
        print("Updating mappings...")

        combined_mappings = []

        # Create a message_id to ChainMap dictionary for quick look-up
        existing_mappings = {
            mapping.message.id: mapping
            for tree in conversation_trees
            for mapping in tree.conversation.mapping.values()
            if mapping.message is not None
        }

        # Initialize previous message variable
        prev_message = None

        for message in tqdm(sorted_messages):
            if message.id in existing_mappings:
                mapping = existing_mappings[message.id]
                mapping.message = message
            else:
                mapping = ChainMap(id=message.id, message=message)

            # Check if message is by system
            if message.author.role == "system":
                # If message is by system, check if it is a prompt
                related_conversation = None
                for index, conv in enumerate(conversation_trees):
                    if conv.conversation.mapping.get(message.id):
                        related_conversation = conv
                        break

                if related_conversation:
                    # If message is a prompt, update the message content
                    message.content.text = f"Conversation {index + 1}: {related_conversation.conversation.title}"
                    message.content.parts = [message.content.text]
                    message.create_time = related_conversation.conversation.create_time

                if prev_message:
                    mapping.parent = prev_message.id
                    prev_mapping = existing_mappings.get(
                        prev_message.id,
                        ChainMap(id=prev_message.id, message=prev_message),
                    )
                    if prev_mapping.children:
                        prev_mapping.children.append(message.id)
                    else:
                        prev_mapping.children = [message.id]

            combined_mappings.append(mapping)
            prev_message = message

        return combined_mappings

    def combine_conversations(
        self, filtered_trees: List[ChainTreeIndex], title: str = "Combined Conversation"
    ) -> ChainTreeIndex:
        """
        Combine multiple conversation trees into a single conversation tree.

        This method retrieves the mappings from each of the filtered conversation trees
        and performs various operations like updating parent-child relationships, extracting and sorting
        messages, creating linked lists, and finally combining all these into a new single conversation tree.

        Steps involved:
        1. Retrieve mappings from the filtered conversation trees.
        2. Update the parent-child relationships in the mappings.
        3. Extract and sort the messages based on their creation time.
        4. Create a linked list from the sorted messages.
        5. Update the mappings with the new message information.
        6. Create a new combined conversation tree.

        Parameters:
            filtered_trees (List[ChainTreeIndex]): A list of ChainTreeIndex objects, each representing
                a filtered conversation tree.

            title (str, optional): The title to be assigned to the combined conversation. Defaults to 'Combined Conversation'.

        Returns:
            ChainTreeIndex: A ChainTreeIndex object representing the combined conversation tree.

        Raises:
            Exception: Any exception that might occur during the process will be caught and printed.

        """

        try:
            mappings = self.retrieve_mappings(filtered_trees)
            new_mapping_ids = self.update_parent_child(mappings)
            sorted_messages = self.extract_and_sort_messages(mappings, new_mapping_ids)
            sorted_messages = self.create_linked_list(sorted_messages)
            combined_mappings = self.update_mappings(sorted_messages, filtered_trees)
            print("Creating combined conversation...")
            # convert the combined mappings to a dictionary
            combined_mappings = {mapping.id: mapping for mapping in combined_mappings}
            # sort the combined mappings by create_time
            combined_mappings = dict(
                sorted(
                    combined_mappings.items(),
                    key=lambda item: item[1].message.create_time,
                )
            )

            combined_conversation = ChainTree(
                title=title,
                create_time=sorted_messages[0].create_time,
                update_time=sorted_messages[-1].create_time,
                mapping=combined_mappings,
                moderation_results=[],
                current_node="",
            )
            # convert the combined tree to a dictionary
            combined_tree = [ChainTreeIndex(conversation=combined_conversation)]
            return combined_tree

        except Exception as e:
            print(e)
            return None
