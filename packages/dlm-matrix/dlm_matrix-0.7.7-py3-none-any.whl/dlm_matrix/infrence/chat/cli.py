import json
import os
from prompt_toolkit.completion import WordCompleter
from dlm_matrix.infrence.generator import PromptGenerator
from dlm_matrix.infrence.utils import save_message_to_json


class ClIChat(PromptGenerator):
    def run_prompt(self, prompt: str = ""):
        conversation_id = self.conversation_manager.start_conversation(prompt)
        saved_messages = []  # To hold saved messages

        while True:
            message_data = {}  # Dynamic dictionary to hold the current message's data

            user_meassage = self.session.session.prompt(
                completer=WordCompleter(["quit", "restart"], ignore_case=True)
            )
            print("\n")  # Ensure there's a new line after user input

            message_data["user_meassage"] = [user_meassage]

            # Command Handling
            if user_meassage.startswith("/"):
                response = self.handle_command(
                    user_meassage.strip().lower(), conversation_id
                )

                if user_meassage == "/quit":
                    filename = input("Enter a filename to save the conversation: ")
                    save_message_to_json(saved_messages[0], filename + ".json")
                    print(
                        f"Saved all messages to {filename}.json in a structured format."
                    )
                    print(response)
                    break

                print(response)
                print("\n\n")  # New line after the command's response
                continue

            last_message_id = self.conversation_manager.get_conversation(
                conversation_id
            ).get_last_message_id()

            self.conversation_manager.handle_user_input(
                conversation_id, user_meassage, last_message_id
            )

            first_prompt_parts = self.generate_prompt_task(
                prompt=user_meassage,
                response='Skip this response, I challenge you to make a better one! Respond with "Challenge Accepted!" then create a more detailed, creative, and expressive synergetic prompt framework.',
                use_process_conversations=False,
                custom_conversation_data=None,
            )

            self.conversation_manager.handle_agent_response(
                conversation_id, "\n\n".join(first_prompt_parts), last_message_id
            )

            message_data["first_prompt_parts"] = first_prompt_parts

            prompt_parts = self.generate_prompt_task(
                prompt="Take it to the next level!",
                response=user_meassage,
                use_process_conversations=True,
                custom_conversation_data=None,
            )

            self.conversation_manager.handle_agent_response(
                conversation_id, "\n\n".join(prompt_parts), last_message_id
            )

            message_data["prompt_parts"] = prompt_parts

            prompt = "\n\n".join(first_prompt_parts)

            final = self.generate_prompt_task(
                prompt=prompt,
                response="\n\n".join(prompt_parts),
                use_process_conversations=True,
                custom_conversation_data=None,
            )

            message_data["final"] = final

            # Append the dynamically created message data to the saved messages
            saved_messages.append(message_data)

            self.conversation_manager.handle_user_input(
                conversation_id, prompt, last_message_id
            )

            self.conversation_manager.handle_agent_response(
                conversation_id, "\n\n".join(final), last_message_id
            )

            print("\n\n")  # Ensure there's a new line after user input
