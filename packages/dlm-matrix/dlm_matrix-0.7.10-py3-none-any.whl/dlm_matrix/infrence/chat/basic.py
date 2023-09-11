import re
import time
from dlm_matrix.infrence.generator import PromptGenerator


class ClIChat(PromptGenerator):
    def run_prompt(self, initial_prompt: str = "", request_feedback: bool = False):
        conversation_id = self.conversation_manager.start_conversation(initial_prompt)
        agent_response = None  # Initially, there's no agent response

        while True:
            prompt_message = "You: "
            user_input = self.session.get_input(prompt_message)
            print("\n")  # Ensure there's a new line after user input

            # Command Handling
            if user_input.startswith("/"):
                response = self.handle_command(
                    user_input.strip().lower(), conversation_id
                )
                print(response)
                print("\n")  # New line after the command's response

                if user_input.strip().lower() == "/restart":
                    self.conversation_manager.end_conversation(conversation_id)
                    conversation_id = self.conversation_manager.start_conversation()
                    agent_response = None  # Reset the agent response when restarting
                continue  # Skip the rest and restart the loop

            # Quit Handling
            if user_input.strip().lower() == "quit":
                print("Thank you for using the system. Goodbye!\n")
                break

            use_process_conversations_flag = True if not agent_response else False

            try:
                last_message_id = self.conversation_manager.get_conversation(
                    conversation_id
                ).get_last_message_id()

                prompt_parts = self.generate_prompt_task(
                    prompt=user_input,
                    response=agent_response,  # Using the agent's response from the previous iteration
                    use_process_conversations=use_process_conversations_flag,
                    custom_conversation_data=None,
                )
                agent_prompt = prompt_parts[0]
                agent_response = (
                    agent_prompt  # Update the agent's response for the next iteration
                )

                self.conversation_manager.handle_user_input(
                    conversation_id, user_input, last_message_id
                )
                self.conversation_manager.handle_agent_response(
                    conversation_id, agent_prompt, last_message_id
                )
                print("\n")  # New line after handling agent response

                if request_feedback:
                    feedback_prompt = self.get_feedback(agent_prompt, user_input)
                    self.conversation_manager.handle_user_input(
                        conversation_id, feedback_prompt, last_message_id
                    )
                    print("\n")  # New line after handling feedback

                time.sleep(0.5)
            except Exception as e:
                print(
                    f"An error occurred: {e}. Please try again.\n"
                )  # New line after error message

        self.conversation_manager.end_conversation(conversation_id)

    def get_feedback(self, agent_response: str, user_prompt: str):
        feedback_prompt = self.generate_prompt_task(
            prompt=user_prompt,
            response=agent_response,
            use_process_conversations=False,
            custom_conversation_data=None,
        )[0]

        feedback = self.session.get_input(feedback_prompt)
        print()  # New line after feedback inpu

        return feedback
