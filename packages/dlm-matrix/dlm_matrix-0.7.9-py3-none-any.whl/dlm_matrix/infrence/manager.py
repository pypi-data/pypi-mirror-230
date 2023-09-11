from typing import Dict, List, Union
from dlm_matrix.infrence.validator import MessageIDValidator
from dlm_matrix.infrence.state import StateMachine
from dlm_matrix.models import Content, Author, Chain, RoleType
from dlm_matrix.utils import generate_id
from pydantic import BaseModel, Field
import json
import datetime


class ConversationManager(BaseModel):
    conversations: Dict[str, StateMachine] = Field(
        {}, description="A dictionary mapping conversation IDs to conversations."
    )

    message_id_validator: MessageIDValidator = Field(
        MessageIDValidator(),
        description="A validator for checking if a message ID exists in a conversation.",
    )

    class Config:
        arbitrary_types_allowed = True

    def conversation_exists(self, conversation_id: str) -> bool:
        return conversation_id in self.conversations

    def _validate_message_id_in_mapping(
        self, conversation: StateMachine, message_id: str
    ) -> None:
        if not self.message_id_validator.validate_message_id_in_mapping(
            conversation, message_id
        ):
            raise ValueError(
                f"Message with ID '{message_id}' does not exist in conversation with ID '{conversation.id}'."
            )

    def start_conversation(self, initial_message: str) -> str:
        conversation_id = self.create_conversation()
        self._add_message(conversation_id, initial_message, RoleType.SYSTEM)
        return conversation_id

    def create_conversation(self) -> str:
        conversation_id = generate_id()
        conversation = StateMachine(conversation_id=conversation_id)
        self.conversations[conversation_id] = conversation
        return conversation_id

    def add_conversation(self, conversation: StateMachine) -> None:
        if not isinstance(conversation, StateMachine):
            raise TypeError(
                f"Expected 'Conversation' object, got '{type(conversation).__name__}'."
            )

        if conversation.id in self.conversations:
            raise ValueError(
                f"Conversation with ID '{conversation.id}' already exists."
            )

        self.conversations[conversation.id] = conversation

    def get_conversation(self, conversation_id: str) -> StateMachine:
        if conversation_id not in self.conversations:
            raise ValueError(
                f"Conversation with ID '{conversation_id}' does not exist."
            )

        return self.conversations[conversation_id]

    def print_conversation(self, conversation_id: str) -> None:
        conversation = self.get_conversation(conversation_id)
        conversation.print_conversation()

    def end_conversation(self, conversation_id: str) -> None:
        conversation = self.get_conversation(conversation_id)
        conversation.end_conversation()

    def restart_conversation(self, conversation_id: str) -> None:
        conversation = self.get_conversation(conversation_id)
        conversation.restart_conversation()

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise ValueError(f"No conversation with ID '{conversation_id}' found.")
        return conversation.get_history()

    def add_message(
        self,
        conversation_id: str,
        message_id: str,
        content: Content,
        author: Author,
        parent: str = None,
    ) -> None:
        conversation = self.get_conversation(conversation_id)
        conversation.add_message(
            message_id=message_id, content=content, author=author, parent=parent
        )

    def update_message(
        self, conversation_id: str, message_id: str, new_message: Chain
    ) -> None:
        conversation = self.get_conversation(conversation_id)
        self._validate_message_id_in_mapping(conversation, message_id)

        conversation.update_message(message_id, new_message)

    def delete_message(self, conversation_id: str, message_id: str) -> bool:
        conversation = self.get_conversation(conversation_id)
        self._validate_message_id_in_mapping(conversation, message_id)

        return conversation.delete_message(message_id)

    def get_message(self, conversation_id: str, message_id: str) -> Chain:
        conversation = self.get_conversation(conversation_id)
        self._validate_message_id_in_mapping(conversation, message_id)

        return conversation.get_message(message_id)

    def move_message(
        self, conversation_id: str, message_id: str, new_parent_id: str
    ) -> None:
        conversation = self.get_conversation(conversation_id)
        self._validate_message_id_in_mapping(conversation, message_id)

        conversation.move_message(message_id, new_parent_id)

    def merge_conversations(
        self, conversation_id_1: str, conversation_id_2: str
    ) -> None:
        conversation_1 = self.get_conversation(conversation_id_1)
        conversation_2 = self.get_conversation(conversation_id_2)

        conversation_1.merge(conversation_2)
        self.delete_conversation(conversation_id_2)

    def get_conversations(self) -> List[StateMachine]:
        return list(self.conversations.values())

    def get_conversation_ids(self) -> List[str]:
        return list(self.conversations.keys())

    def get_conversation_titles(self) -> List[str]:
        return [conv.title for conv in self.conversations.values()]

    def get_conversation_titles_and_ids(self) -> List[Dict[str, str]]:
        return [
            {"title": conv.title, "id": conv.id} for conv in self.conversations.values()
        ]

    def delete_conversation(self, conversation_id: str) -> None:
        if conversation_id not in self.conversations:
            raise ValueError(
                f"Conversation with ID '{conversation_id}' does not exist."
            )

        del self.conversations[conversation_id]

    def delete_all_conversations(self) -> None:
        self.conversations = {}

    def cleanup_inactive_conversations(
        self, inactivity_threshold_in_hours: int = 1
    ) -> None:
        current_time = datetime.datetime.now().timestamp()
        inactive_conversations = []

        # identify inactive conversations
        for conversation_id, conversation in self.conversations.items():
            time_since_last_interaction = (
                current_time - conversation.last_interaction_time
            )
            if time_since_last_interaction > inactivity_threshold_in_hours * 60 * 60:
                inactive_conversations.append(conversation_id)

        # remove inactive conversations
        for conversation_id in inactive_conversations:
            del self.conversations[conversation_id]

    def __len__(self) -> int:
        return len(self.conversations)

    def __getitem__(self, conversation_id: str) -> StateMachine:
        return self.get_conversation(conversation_id)

    def __iter__(self):
        return iter(self.conversations)

    def __contains__(self, conversation_id: str) -> bool:
        return conversation_id in self.conversations

    def __delitem__(self, conversation_id: str) -> None:
        self.delete_conversation(conversation_id)

    def __repr__(self) -> str:
        return f"ConversationManager(conversations={self.conversations})"

    def merge_conversations(
        self, conversation_id_1: str, conversation_id_2: str
    ) -> None:
        conversation_1 = self.get_conversation(conversation_id_1)
        conversation_2 = self.get_conversation(conversation_id_2)

        conversation_1.merge(conversation_2)
        self.delete_conversation(conversation_id_2)

    def export_conversations_to_json(self) -> str:
        conversations_data = [conv.to_dict() for conv in self.conversations.values()]
        return json.dumps(conversations_data, indent=2)

    def import_conversations_from_json(self, json_data: str) -> None:
        try:
            conversations_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")

        if not isinstance(conversations_data, list):
            raise ValueError("JSON data should be a list of conversation dictionaries.")

        for conv_data in conversations_data:
            try:
                conversation = StateMachine.from_dict(conv_data)
            except ValueError as e:
                raise ValueError(f"Invalid conversation data: {e}")

            self.add_conversation(conversation)

    def _add_message(
        self,
        conversation_ids: Union[str, List[str]],
        messages: Union[str, List[str]],
        author_type: RoleType,
        parent_ids: Union[str, List[str], None] = None,
    ) -> None:
        if isinstance(conversation_ids, str):
            conversation_ids = [conversation_ids]

        if isinstance(messages, str):
            messages = [messages]

        if isinstance(parent_ids, str):
            parent_ids = [parent_ids]
        elif parent_ids is None:
            parent_ids = [None] * len(messages)

        for conversation_id in conversation_ids:
            last_parent_id = None
            for message, parent_id in zip(messages, parent_ids):
                message_id = generate_id()  # Assuming generate_id is defined elsewhere
                content = Content.from_text(
                    message
                )  # Assuming Content class is defined elsewhere
                author = Author(
                    role=author_type.value, metadata={}
                )  # Assuming Author class is defined elsewhere

                if parent_id is None and last_parent_id is not None:
                    parent_id = last_parent_id

                self.add_message(
                    conversation_id, message_id, content, author, parent_id
                )
                last_parent_id = message_id

    def handle_user_input(
        self,
        conversation_ids: Union[str, List[str]],
        user_input: Union[str, List[str]],
        parent_ids: Union[str, List[str], None] = None,
    ) -> None:
        self._add_message(conversation_ids, user_input, RoleType.USER, parent_ids)

    def handle_agent_response(
        self,
        conversation_ids: Union[str, List[str]],
        agent_response: Union[str, List[str]],
        parent_ids: Union[str, List[str], None] = None,
    ) -> None:
        self._add_message(
            conversation_ids, agent_response, RoleType.ASSISTANT, parent_ids
        )

    def handle_system_message(
        self,
        conversation_ids: Union[str, List[str]],
        system_message: Union[str, List[str]],
        parent_ids: Union[str, List[str], None] = None,
    ) -> None:
        self._add_message(conversation_ids, system_message, RoleType.SYSTEM, parent_ids)
