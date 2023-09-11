from typing import Optional, Dict, Any, Callable, List
from dlm_matrix.models import Chain, ChainMap, Author, Content
from dlm_matrix.utils import filter_none_values
import datetime
import uuid
import json
import os


class StateMachine:
    """
    Represents a state machine for a conversation.
    Attributes:
        conversation_id (str): The ID of the conversation.
        mappings (Dict[str, Mapping]): A mapping of message IDs to message nodes.
        root (Optional[str]): The ID of the root node.
        timeout (Optional[int]): The timeout for the conversation.
        last_interaction_time (datetime.datetime): The timestamp for the last interaction.
    """

    def __init__(
        self,
        conversation_id: str,
        timeout: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.conversation_id = conversation_id
        self.mappings = {}
        self.root = None
        self.timeout = timeout
        self.last_interaction_time = datetime.datetime.now().timestamp()
        self.history = []

    def _validate_relationship(self, relationship: str) -> bool:
        return relationship in {"before", "after", "child"}

    def _validate_offset(self, parent: Optional[str], offset: Optional[int]) -> bool:
        if parent is None:
            return offset is None
        else:
            return offset is not None

    @classmethod
    def from_conversation(
        cls,
        conversation_id: str,
        conversation: "StateMachine",
        timeout: Optional[int] = None,
    ) -> "StateMachine":
        """Create a StateMachine from an existing conversation."""
        state_machine = cls(conversation_id, timeout)
        state_machine.mappings = conversation.mappings
        state_machine.root = conversation.root
        state_machine.last_interaction_time = conversation.last_interaction_time
        return state_machine

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the StateMachine."""
        return {
            "conversation_id": self.conversation_id,
            "mappings": {
                message_id: {
                    "message": filter_none_values(mapping.message.dict()),
                    "parent": mapping.parent,
                    "children": mapping.children,
                    "prev": mapping.prev,
                    "next": mapping.next,
                }
                for message_id, mapping in self.mappings.items()
            },
            "root": self.root,
            "timeout": self.timeout,
            "last_interaction_time": self.last_interaction_time,
        }

    def add_conversation(
        self,
        conversation: "StateMachine",
        relationship: str = "child",
        parent: Optional[str] = None,
        offset: Optional[int] = None,
    ) -> None:
        """Add a conversation to the current conversation."""
        if parent is not None and parent not in self.mappings:
            raise ValueError(f"Parent ID '{parent}' not found in the conversation.")

        if not self._validate_relationship(relationship):
            raise ValueError(f"Invalid relationship '{relationship}'.")

        if not self._validate_offset(parent, offset):
            raise ValueError(f"Invalid offset '{offset}' for parent ID '{parent}'.")

        if conversation.root in self.mappings:
            raise ValueError(
                f"Conversation already contains a message with ID '{conversation.root}'."
            )

        mapping = ChainMap(
            id=conversation.root,
            message=conversation.mappings[conversation.root].message,
            parent=parent,
            children=[],
            prev=None,
            next=None,
        )

        if parent is None:
            self.root = conversation.root
        else:
            if relationship == "child":
                if offset is None:
                    self.mappings[parent].children.append(conversation.root)
                else:
                    self.mappings[parent].children.insert(offset, conversation.root)
            elif relationship == "before":
                parent_index = self.mappings[
                    self.mappings[parent].parent
                ].children.index(parent)
                self.mappings[self.mappings[parent].parent].children.insert(
                    parent_index + offset, conversation.root
                )
            elif relationship == "after":
                parent_index = self.mappings[
                    self.mappings[parent].parent
                ].children.index(parent)
                self.mappings[self.mappings[parent].parent].children.insert(
                    parent_index + offset + 1, conversation.root
                )

            mapping.prev = self.mappings[parent].id

            if offset is None:
                mapping.next = None
            else:
                mapping.next = self.mappings[parent].children[offset]

        self.mappings[conversation.root] = mapping

        for message_id, mapping in conversation.mappings.items():
            if message_id != conversation.root:
                mapping.children = [
                    conversation.mappings[child_id].id for child_id in mapping.children
                ]

        self.last_interaction_time = datetime.datetime.now().timestamp()

    def add_conversation_before(
        self,
        conversation_id: str,
        conversation: "StateMachine",
        parent: Optional[str] = None,
        offset: Optional[int] = None,
    ) -> None:
        """Add a conversation before the specified message."""
        self.add_conversation(conversation_id, conversation, "before", parent, offset)

    def add_conversation_after(
        self,
        conversation_id: str,
        conversation: "StateMachine",
        parent: Optional[str] = None,
        offset: Optional[int] = None,
    ) -> None:
        self.add_conversation(conversation_id, conversation, "after", parent, offset)

    def add_conversation_child(
        self,
        conversation_id: str,
        conversation: "StateMachine",
        parent: Optional[str] = None,
        offset: Optional[int] = None,
    ) -> None:
        """Add a conversation as a child of the specified message."""
        self.add_conversation(conversation_id, conversation, "child", parent, offset)

    def _create_message(
        self,
        id: str,
        author: Optional[Author],
        content: Content,
        metadata: Optional[Dict[str, Any]],
        weight: int,
        end_turn: Optional[bool],
        recipient: Optional[str],
    ) -> Chain:
        return Chain(
            id=id,
            author=author,
            create_time=get_current_timestamp(),
            content=content,
            metadata=metadata,
            weight=weight,
            end_turn=end_turn,
            recipient=recipient,
        )

    def add_message(
        self,
        message_id: str,
        author: Author,
        content: Content,
        relationship: str = "child",
        parent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        weight: int = 1,
        end_turn: Optional[bool] = None,
        recipient: Optional[str] = None,
        offset: Optional[int] = 0,  # default value for offset
    ) -> None:
        if parent is not None and parent not in self.mappings:
            raise ValueError(f"Parent ID '{parent}' not found in the conversation.")

        if weight <= 0:
            raise ValueError("Weight must be a positive integer.")

        if not self._validate_relationship(relationship):
            raise ValueError(f"Invalid relationship '{relationship}'.")

        message = self._create_message(
            message_id, author, content, metadata, weight, end_turn, recipient
        )
        mapping = ChainMap(id=message_id, message=message, parent=parent, children=[])

        if parent is None:
            self.root = message_id
            # add prev and next attributes
            mapping.prev = None
            mapping.next = None

        else:
            if relationship == "child":
                # check if offset is None
                if offset is None:
                    self.mappings[parent].children.append(message_id)
                else:
                    self.mappings[parent].children.insert(offset, message_id)
            elif relationship == "before":
                parent_index = self.mappings[
                    self.mappings[parent].parent
                ].children.index(parent)
                self.mappings[self.mappings[parent].parent].children.insert(
                    parent_index + offset, message_id
                )
            elif relationship == "after":
                parent_index = self.mappings[
                    self.mappings[parent].parent
                ].children.index(parent)
                self.mappings[self.mappings[parent].parent].children.insert(
                    parent_index + offset + 1, message_id
                )

            # add prev and next attributes
            mapping.prev = self.mappings[parent].id

            # check if offset is None
            if offset is None:
                mapping.next = None
            else:
                mapping.next = self.mappings[parent].children[offset]

        self.mappings[message_id] = mapping
        self.last_interaction_time = datetime.datetime.now().timestamp()

    def regenerate_message(
        self,
        message_id: str,
        content: Optional[Content] = None,
        new_weight: Optional[int] = None,
        metadata_updates: Optional[Dict[str, Any]] = None,
    ) -> None:
        message_node = self._get_message_node(message_id)
        content = content if content is not None else message_node.message.content
        new_weight = (
            new_weight if new_weight is not None else message_node.message.weight
        )
        metadata_updates = (
            metadata_updates
            if metadata_updates is not None
            else message_node.message.metadata
        )

        self.add_message(
            message_id,
            message_node.message.author,
            content,
            message_node.parent,
            metadata_updates,
            new_weight,
            message_node.message.end_turn,
            message_node.message.recipient,
        )

    def merge(
        self,
        other: "StateMachine",
        offset: Optional[int] = None,
        merge_operation: Optional[Callable[[Chain, Chain], Chain]] = None,
    ) -> None:
        if other is self:
            raise ValueError("Cannot merge a conversation with itself.")

        if other.root in self.mappings:
            raise ValueError(
                f"Conversation already contains a message with ID '{other.root}'."
            )

        if not self._validate_offset(self.root, offset):
            raise ValueError(f"Invalid offset '{offset}' for parent ID '{self.root}'.")

        root_mapping = self.mappings[self.root]
        other_root_mapping = other.mappings[other.root]

        self.mappings.update(other.mappings)

        if offset is None:
            root_mapping.children.append(other.root)
        else:
            root_mapping.children.insert(offset, other.root)

        for message_id, mapping in other.mappings.items():
            if message_id != self.root:
                mapping.children = [
                    other.mappings[child_id].id for child_id in mapping.children
                ]

        if other_root_mapping.message.author.role == "user":
            self.reset_timeout()

        self.last_interaction_time = datetime.datetime.now()

        if merge_operation is not None:
            merge_operation(root_mapping.message, other_root_mapping.message)

        return self

    def split(self, message_id: str, offset: Optional[int] = None) -> "StateMachine":
        if message_id not in self.mappings:
            raise ValueError(
                f"Message ID '{message_id}' not found in the conversation."
            )

        if not self._validate_offset(message_id, offset):
            raise ValueError(f"Invalid offset '{offset}' for parent ID '{message_id}'.")

        message_node = self.mappings[message_id]
        parent_id = message_node.parent

        if parent_id is None:
            raise ValueError(f"Cannot split the root message.")

        parent_node = self.mappings[parent_id]
        siblings = parent_node.children

        if message_id not in siblings:
            raise ValueError(
                f"Message ID '{message_id}' is not a sibling of the parent '{parent_id}'."
            )

        sibling_index = siblings.index(message_id)

        new_conversation = StateMachine(
            conversation_id=str(uuid.uuid4()), timeout=self.timeout
        )
        new_conversation.root = message_id

        for sibling_id in reversed(siblings[sibling_index:]):
            sibling_node = self.mappings.pop(sibling_id)
            new_conversation.mappings[sibling_id] = sibling_node
            if sibling_node.parent == message_id:
                sibling_node.parent = None
            sibling_node.children = [
                child_id
                for child_id in sibling_node.children
                if child_id not in siblings
            ]

        new_conversation.mappings[message_id].children = siblings[sibling_index + 1 :]
        del siblings[sibling_index:]

        self.last_interaction_time = datetime.datetime.now()

        return new_conversation

    def load_conversation(self, title) -> None:
        """Load a conversation from json file."""
        with open(f"conversation/{title}.json", "r") as f:
            conovo = json.load(f)

        self.conversation_id = conovo["conversation_id"]
        self.mappings = {
            message_id: ChainMap(
                id=message_id,
                message=Chain(**message_data["message"]),
                parent=message_data["parent"],
                children=message_data["children"],
                prev=message_data["prev"],
                next=message_data["next"],
            )
            for message_id, message_data in conovo["mappings"].items()
        }
        self.root = conovo["root"]
        self.last_interaction_time = conovo["updated_time"]

        return self

    def save_conversation(self, title) -> Dict[str, Any]:
        """Return a dictionary representation of the conversation."""
        conovo = {
            "title": title,
            "id": self.conversation_id,
            "created_time": self.mappings[self.root].message.create_time,
            "updated_time": self.last_interaction_time,
            "mappings": {
                message_id: {
                    "message": filter_none_values(mapping.message.dict()),
                    "parent": mapping.parent,
                    "children": mapping.children,
                    "prev": mapping.prev,
                    "next": mapping.next,
                }
                for message_id, mapping in self.mappings.items()
            },
            "current_node": self.mappings[self.root].message.id,
            "moderation": [],
        }

        # Create the folder if it doesn't exist
        folder_path = "conversation"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save to json file
        with open(f"{folder_path}/{title}.json", "w") as f:
            json.dump([conovo], f, indent=4)

        return conovo

    def delete_conversation(self, title) -> None:
        """Delete a conversation from json file."""
        os.remove(f"conversation/{title}.json")

    def delete_message(self, message_id: str) -> None:
        self._remove_message_from_parent(message_id)
        del self.mappings[message_id]
        self.update_interaction_time()

    def update_message(
        self,
        message_id: str,
        content: Optional[Content] = None,
        metadata_updates: Optional[Dict[str, Any]] = None,
    ) -> None:
        message_node = self._get_message_node(message_id)

        if content is not None:
            message_node.message.content = content

        if metadata_updates is not None:
            message_node.message.metadata.update(metadata_updates)

        self.update_interaction_time()

    def move_message(
        self,
        message_id: str,
        new_parent_id: str,
        new_sibling_index: Optional[int] = None,
    ) -> None:
        message_node = self._get_message_node(message_id)
        self._remove_message_from_parent(message_id)
        message_node.parent = new_parent_id

        if new_sibling_index is None:
            new_sibling_index = len(self.mappings[new_parent_id].children)

        self.mappings[new_parent_id].children.insert(new_sibling_index, message_id)
        self.update_interaction_time()

    def reset_timeout(self) -> None:
        self.update_interaction_time()

    def update_interaction_time(self) -> None:
        self.last_interaction_time = datetime.datetime.now()

    def is_active(self) -> bool:
        if self.timeout is None:
            return True
        time_elapsed = datetime.datetime.now() - self.last_interaction_time
        return time_elapsed.seconds < self.timeout

    def get_history(self) -> List[Chain]:
        return [
            mapping.message.content.parts
            for message_id, mapping in self.mappings.items()
            if message_id != self.root
        ]

    def get_message(self, message_id: str) -> Chain:
        return self._get_message_node(message_id).message

    def _get_parent_id(self) -> str:
        parent_id = self.root
        while True:
            parent_node = self.mappings[parent_id]
            if len(parent_node.children) == 0:
                return parent_id
            parent_id = parent_node.children[-1]

    def _get_message_node(self, message_id: str) -> ChainMap:
        """Retrieve the Mapping corresponding to a given message ID."""
        if message_id not in self.mappings:
            raise ValueError(
                f"Message ID '{message_id}' not found in the conversation."
            )
        return self.mappings[message_id]

    def _remove_message_from_parent(self, message_id: str) -> None:
        """Remove a message from its parent's children list."""
        message_node = self._get_message_node(message_id)
        parent_id = message_node.parent

        if parent_id is None:
            raise ValueError(f"Cannot modify the root message.")

        siblings = self.mappings[parent_id].children

        if message_id not in siblings:
            raise ValueError(
                f"Message ID '{message_id}' is not a sibling of the parent '{parent_id}'."
            )

        siblings.remove(message_id)

    def get_last_message_id(self) -> str:
        """Return the ID of the last message in the conversation."""
        return self._get_parent_id()

    def get_last_message(self) -> Chain:
        """Return the last message in the conversation."""
        return self.get_message(self.get_last_message_id())

    def end_conversation(self) -> None:
        """Remove all messages from the conversation."""
        self.mappings = {self.root: self.mappings[self.root]}
        self.last_interaction_time = datetime.datetime.now()

    def restart_conversation(self) -> None:
        """Remove all messages from the conversation except the root."""
        self.mappings = {
            self.root: self.mappings[self.root],
            self.mappings[self.root].children[-1]: self.mappings[
                self.mappings[self.root].children[-1]
            ],
        }
        self.last_interaction_time = datetime.datetime.now()

    def get_truncated_history(
        self, max_history_length: int, include_current_state: bool = True
    ) -> List[Chain]:
        """Return a truncated version of the conversation history."""
        history = self.get_history()
        if not include_current_state:
            history = history[:-1]
        if len(history) > max_history_length:
            history = history[-max_history_length:]
        return history

    def print_conversation(self) -> None:
        """Print the conversation history."""
        for message in self.get_history():
            print(message)

    def get_messages(self) -> List[str]:
        """Return all text content of messages in the conversation."""
        return [
            mapping.message.content.text
            for mapping in self.mappings.values()
            if mapping.message.content and mapping.message.content.text
        ]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateMachine":
        """Create a StateMachine from a dictionary."""
        return cls(**data)


def validate_type(var: Any, expected_type: type, var_name: str) -> None:
    """Check if the variable is of the expected type, raise a TypeError if not."""
    if not isinstance(var, expected_type):
        raise TypeError(
            f"Expected '{expected_type.__name__}' for {var_name}, got '{type(var).__name__}'."
        )


def get_current_timestamp() -> float:
    """Return the current timestamp."""
    return datetime.datetime.now().timestamp()
