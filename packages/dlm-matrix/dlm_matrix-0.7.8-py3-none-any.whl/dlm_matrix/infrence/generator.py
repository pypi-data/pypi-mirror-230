import re
import time
from typing import Optional, List, Dict
from dlm_matrix.infrence.manager import ConversationManager
from dlm_matrix.utils import APIFailureException
from dlm_matrix.infrence.openai import ChatOpenAI
from dlm_matrix.services.utility.engine import DataEngine
from dlm_matrix.chaintrees import ReplyChainSystem
from dlm_matrix.callbacks.streaming import StreamingHandler
from dlm_matrix.infrence.session import PromptSessionWrapper
from dlm_matrix.utils import (
    log_handler,
    setup_logging,
    backoff_handler,
)


class PromptGenerator:
    def __init__(
        self,
        openai_api_key: str,
        model: str = "gpt-3.5-turbo-16k",
        callback: Optional[StreamingHandler] = None,
        dataset_loader: Optional[DataEngine] = None,
        dataset_path: Optional[str] = None,
    ):
        self.conversation_manager = ConversationManager()
        self.retries: int = 3
        callback = callback if callback else StreamingHandler()
        self.chat = ChatOpenAI(
            callbacks=[callback], openai_api_key=openai_api_key, model_name=model
        )
        self.reply_chain_system = ReplyChainSystem()
        self.dataset_loader = (
            dataset_loader
            if dataset_loader
            else DataEngine(local_dataset_path=dataset_path)
        )
        self.session = PromptSessionWrapper()
        self.first_run = True

        setup_logging()

    def create_conversation(self) -> str:
        return self.conversation_manager.create_conversation()

    def generate_prompt_parts(
        self,
        conversation_id: str,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        use_process_conversations: bool = False,
        custom_conversation_data: Optional[List[Dict[str, str]]] = None,
        max_history_length: Optional[int] = None,
        prioritize_recent: bool = True,
        message_split_pattern: Optional[str] = r"\n\n",
    ) -> List[str]:
        conversation_history = self.reply_chain_system.prepare_conversation_history(
            prompt,
            response,
            use_process_conversations,
            custom_conversation_data,
            max_history_length,
            prioritize_recent,
        )

        truncated_history = self.chat._truncate_conversation_history(
            conversation_history
        )

        generated_messages = self.generate_messages(conversation_id, truncated_history)
        text = generated_messages.content.raw
        prompt_parts = re.split(message_split_pattern, text)

        return prompt_parts

    def generate_prompt_task(
        self,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        use_process_conversations: bool = False,
        custom_conversation_data: Optional[List[Dict[str, str]]] = None,
        include_prompt_in_create: bool = False,
    ) -> List[str]:
        retry = 0
        while retry < self.chat.max_retries:
            try:
                conversation_id = self.create_conversation()
                prompt_parts = self.generate_prompt_parts(
                    conversation_id=conversation_id,
                    prompt=prompt,
                    response=response,
                    use_process_conversations=use_process_conversations,
                    custom_conversation_data=custom_conversation_data,
                )

                if include_prompt_in_create:
                    self.dataset_loader.manager.create_prompt(prompt_parts, prompt)
                else:
                    self.dataset_loader.manager.create_prompt(prompt_parts, None)

                break

            except APIFailureException:
                log_handler(f"Prompt failed", level="warning")
                retry += 1
                time.sleep(backoff_handler(retry))

        if retry == self.chat.max_retries:
            log_handler(f"Prompt failed", level="error")
            raise APIFailureException("Prompt failed")
        return prompt_parts

    def generate_messages(
        self,
        conversation_id: str,
        truncated_history: List[str],
        parent: Optional[str] = None,
    ):
        generated_messages = self.chat(truncated_history)
        self.conversation_manager.add_message(
            conversation_id,
            message_id=generated_messages.id,
            content=generated_messages.content,
            author=generated_messages.author,
            parent=parent,
        )
        return generated_messages

    def save_conversation(self, conversation_id: str, title: str = "Untitled"):
        """Save the current conversation to json file"""
        conversation = self.conversation_manager.get_conversation(conversation_id)
        conversation.save_conversation(title)

    def load_conversation(self, conversation_id: str, title: str = "Untitled"):
        """Load a conversation from json file"""
        conversation = self.conversation_manager.get_conversation(conversation_id)
        conversation.load_conversation(title)

    def delete_conversation(self, conversation_id: str) -> None:
        self.conversation_manager.delete_conversation(conversation_id)

    def handle_command(self, command: str, conversation_id: str) -> str:
        if command.startswith("/save"):
            parts = command.split(maxsplit=1)  # Split the command into at most 2 parts
            if len(parts) > 1:
                title = parts[1]  # The second part is our title
                try:
                    self.save_conversation(conversation_id, title)
                    return "Conversation saved successfully with title: " + title
                except Exception as e:
                    return f"Error saving conversation: {e}"
            else:
                return "Please provide a title. Use /save <title>."
        elif command.startswith("/load"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                title = parts[1]
                try:
                    self.load_conversation(conversation_id, title)
                    return "Conversation loaded successfully with title: " + title
                except Exception as e:
                    return f"Error loading conversation: {e}"

            else:
                return "Please provide a title. Use /load <title>."
        elif command.startswith("/delete"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                title = parts[1]
                try:
                    self.delete_conversation(conversation_id, title)
                    return "Conversation deleted successfully with title: " + title
                except Exception as e:
                    return f"Error deleting conversation: {e}"

            else:
                return "Please provide a title. Use /delete <title>."

        elif command == "/restart":
            self.conversation_manager.restart_conversation(conversation_id)
            return "Conversation restarted."

        elif command == "/history":
            return "\n".join(
                self.conversation_manager.get_conversation(
                    conversation_id
                ).get_messages()
            )

        elif command == "/quit":
            return "Quitting and saving the conversation..."

        elif command == "/help":
            return self.help()

        else:
            return "Unknown command. Use /help for a list of commands."

    def help(self):
        commands = {
            "/save": "Save the conversation to a JSON file. Use '/save <title>' to specify a title.",
            "/load": "Load a conversation from a JSON file. Use '/load <title>' to specify a title.",
            "/delete": "Delete a conversation from a JSON file. Use '/delete <title>' to specify a title.",
            "/restart": "Restart the conversation.",
            "/history": "Show the conversation history.",
            "/quit": "Quit the conversation and save it to a JSON file.",
        }
        return "\n".join(
            [f"{command}: {description}" for command, description in commands.items()]
        )
